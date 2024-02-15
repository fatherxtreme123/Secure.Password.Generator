import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from CTkListbox import *
import tkinter as tk
import string
import random
import qrcode
from tkinter import filedialog
import os
import json
import pyperclip
import webbrowser

def createToolTip(widget, text):
    try:
        def enter(event):
            widget._after_id = widget.after(600, show_tooltip, event)

        def leave(event):
            widget.after_cancel(widget._after_id)
            tooltip = getattr(widget, "_tooltip", None)
            if tooltip:
                tooltip.destroy()
                widget._tooltip = None

        def show_tooltip(event):
            tooltip = ctk.CTkToplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = ctk.CTkLabel(tooltip, text=text, fg_color="black", text_color="white")
            label.grid()
            widget._tooltip = tooltip

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    except Exception as e:
        CTkMessagebox(title="Error", message=f"An error occurred: {e}")

class App(ctk.CTk):
    def __init__(self):
        try:
            super().__init__()

            self.title('Secure Password Generator')
            self.iconbitmap('Secure Password Generator.ico')
            self.resizable(False, False)

            self.main_frame = ctk.CTkFrame(self)
            self.main_frame.grid(row=0, column=0, sticky="nsew")

            self.left_frame = ctk.CTkFrame(self.main_frame, width=200, height=400)
            self.left_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ns")

            self.right_frame = ctk.CTkFrame(self.main_frame)
            self.right_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

            self.history_display = None

            self.password_history_file = 'password_history.json'
            if os.path.exists(self.password_history_file):
                with open(self.password_history_file, 'r') as f:
                    self.password_history = json.load(f)
            else:
                self.password_history = []

            self.var_upper = tk.BooleanVar(value=True)
            self.var_lower = tk.BooleanVar(value=True)
            self.var_digits = tk.BooleanVar(value=True)
            self.var_symbols = tk.BooleanVar(value=True)
            self.var_random_length = tk.BooleanVar(value=False)
            self.var_length = tk.StringVar(value="Length: 20")
            self.var_symbols_custom = tk.StringVar(value="")
            self.var_exclude_chars = tk.StringVar(value="")

            self.check_upper = ctk.CTkCheckBox(self.right_frame, text="Include Uppercase Letters", variable=self.var_upper)
            self.check_upper.grid(row=0, column=1, sticky="ew", pady=10)
            createToolTip(self.check_upper, "Check this to include at least one uppercase letter in the password.")

            self.check_lower = ctk.CTkCheckBox(self.right_frame, text="Include Lowercase Letters", variable=self.var_lower)
            self.check_lower.grid(row=1, column=1, sticky="ew", pady=10)
            createToolTip(self.check_lower, "Check this to include at least one lowercase letter in the password.")

            self.check_digits = ctk.CTkCheckBox(self.right_frame, text="Include Digits", variable=self.var_digits)
            self.check_digits.grid(row=2, column=1, sticky="ew", pady=10)
            createToolTip(self.check_digits, "Check this to include at least one digit in the password.")

            self.check_symbols = ctk.CTkCheckBox(self.right_frame, text="Include Symbols", variable=self.var_symbols)
            self.check_symbols.grid(row=3, column=1, sticky="ew", pady=10)
            createToolTip(self.check_symbols, "Check this to include at least one symbol in the password.")

            self.check_random_length = ctk.CTkCheckBox(self.right_frame, text="Random Length", variable=self.var_random_length)
            self.check_random_length.grid(row=4, column=1, sticky="ew", pady=10)
            createToolTip(self.check_random_length, "Check this to generate a password with a length randomly chosen between 1 and the value set by the length slider.")

            self.button_symbols_custom = ctk.CTkButton(self.right_frame, text="⮞", command=self.set_symbols_custom, width=30)
            self.button_symbols_custom.grid(row=3, column=2)
            createToolTip(self.button_symbols_custom, "Click to set custom symbols for the password.")

            self.button_exclude_chars = ctk.CTkButton(self.right_frame, text="⮞", command=self.set_exclude_chars, width=30)
            self.button_exclude_chars.grid(row=8, column=2)
            createToolTip(self.button_exclude_chars, "Click to set characters to exclude from the password.")

            self.length_slider_max = 50
            self.length_slider = ctk.CTkSlider(self.right_frame, from_=1, to=self.length_slider_max, command=self.update_length_label)
            self.length_slider.grid(row=6, column=1)
            createToolTip(self.length_slider, "Slide to set the password length.")

            self.length_label = ctk.CTkLabel(self.right_frame, textvariable=self.var_length)
            self.length_label.grid(row=7, column=1)
            createToolTip(self.length_label, "This shows the current length of the password. Click to set a custom length.")
            self.length_label.bind("<Button-1>", self.set_custom_length)

            self.generate_button = ctk.CTkButton(self.right_frame, text='Generate Password', command=self.generate_password)
            self.generate_button.grid(row=8, column=1, sticky="ew", pady=10, padx=10)
            createToolTip(self.generate_button, "Click here to generate a password.")

            self.password_entry = ctk.CTkEntry(self.right_frame, state='readonly')
            self.password_entry.grid(row=9, column=1, sticky="nsew")
            createToolTip(self.password_entry, "The generated password will be displayed here")
            self.password_entry.bind("<Button-1>", self.save_password)

            self.copy_password_button = ctk.CTkButton(self.left_frame, text="Copy Password", command=self.copy_password)
            self.copy_password_button.grid(row=0, column=0, sticky="ew", pady=10)
            createToolTip(self.copy_password_button, "Click to copy the generated password")

            self.qr_button = ctk.CTkButton(self.left_frame, text="Generate password QR code", command=self.generate_qr)
            self.qr_button.grid(row=1, column=0, sticky="ew", pady=10)
            createToolTip(self.qr_button, "Click to generate password QR code")

            self.history_button = ctk.CTkButton(self.left_frame, text="Password History", command=self.show_password_history)
            createToolTip(self.history_button, "Click to view password history")
            self.history_button.grid(row=2, column=0, sticky="ew", pady=10)

            self.batch_button = ctk.CTkButton(self.left_frame, text="Batch Generate Password", command=self.batch_generate_password)
            createToolTip(self.batch_button, "Click to batch generate passwords.")
            self.batch_button.grid(row=3, column=0, sticky="ew", pady=10)

            self.delete_password_button = ctk.CTkButton(self.left_frame, text="Delete Password", command=self.delete_password)
            createToolTip(self.delete_password_button, "Click to delete the password from the entry")
            self.delete_password_button.grid(row=4, column=0, sticky="ew", pady=10)

            self.delete_and_copy_password_button = ctk.CTkButton(self.left_frame, text="Delete and Copy Password", command=self.delete_and_copy_password)
            createToolTip(self.delete_and_copy_password_button, "Click to delete the password from the entry and copy it to the clipboard")
            self.delete_and_copy_password_button.grid(row=5, column=0, sticky="ew", pady=10)

            self.send_feedback_button = ctk.CTkButton(self.left_frame, text="Send Feedback", command=self.send_feedback)
            createToolTip(self.send_feedback_button, "Click to open the GitHub issues page and send feedback")
            self.send_feedback_button.grid(row=6, column=0, sticky="ew", pady=10)

            self.shortcuts_button = ctk.CTkButton(self.left_frame, text="View Shortcuts", command=self.show_shortcuts)
            createToolTip(self.shortcuts_button, "Click to view keyboard shortcuts")
            self.shortcuts_button.grid(row=7, column=0, sticky="ew", pady=10)

            self.templates = {
                "Template 1": {
                    "upper": True, "lower": True, "digits": True, "symbols": True,
                    "length": 20, "random_length": False, "exclude_chars": "", "custom_symbols": ""
                },
                "Template 2": {
                    "upper": True, "lower": True, "digits": False, "symbols": False,
                    "length": 15, "random_length": True, "exclude_chars": "il1Lo0O", "custom_symbols": ""
                },
                "Template 3": {
                    "upper": False, "lower": True, "digits": True, "symbols": True,
                    "length": 30, "random_length": False, "exclude_chars": "", "custom_symbols": "!@#"
                },
                "Template 4": {
                    "upper": True, "lower": True, "digits": True, "symbols": True,
                    "length": 99, "random_length": False, "exclude_chars": "il1Lo0O", "custom_symbols": "!@#"
                },
                "Template 5": {
                    "upper": True, "lower": False, "digits": False, "symbols": False,
                    "length": 10, "random_length": False
                },
                "Template 6": {
                    "upper": False, "lower": True, "digits": True, "symbols": False,
                    "length": 8, "random_length": True
                },
            }
            self.template_var = tk.StringVar(value="Template 1")
            self.template_menu = ctk.CTkOptionMenu(self.right_frame, variable=self.template_var, values=list(self.templates.keys()), command=self.apply_template)
            createToolTip(self.template_menu, "Select a template to apply to the password generation settings.")
            self.template_menu.grid(row=10, column=1, pady=10, sticky="ew")

            self.bind("<Control-g>", lambda event: self.generate_password())
            self.bind("<Control-c>", lambda event: self.copy_password())
            self.bind("<Control-q>", lambda event: self.generate_qr())
            self.bind("<Control-d>", lambda event: self.delete_password())
            self.bind("<Control-e>", lambda event: self.export_password_history())
            self.bind("<Control-s>", lambda event: self.save_password(event))
            self.bind("<Control-f>", lambda event: self.send_feedback())
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def update_length_label(self, value):
        try:
            self.var_length.set(f"Length: {int(float(value))}")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def set_symbols_custom(self):
        try:
            result = ctk.CTkInputDialog(text="Enter custom symbols:", title="Set Custom Symbols")
            symbols_custom = result.get_input()
            if symbols_custom is not None:
                self.var_symbols_custom.set(symbols_custom)
                if symbols_custom:
                    self.check_symbols.configure(text="Include Custom Symbols")
                    self.var_symbols.set(True)
                else:
                    self.check_symbols.configure(text="Include Symbols")
                    self.var_symbols.set(False)
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def set_exclude_chars(self):
        try:
            result = ctk.CTkInputDialog(text="Enter characters to exclude:", title="Set Exclude Characters")
            exclude_chars = result.get_input()
            if exclude_chars is not None:
                self.var_exclude_chars.set(exclude_chars)
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def set_custom_length(self, event):
        try:
            result = ctk.CTkInputDialog(text="Enter custom length:", title="Set Custom Length")
            custom_length = result.get_input()
            if custom_length and custom_length.isdigit():
                custom_length = int(custom_length)
                if custom_length > self.length_slider_max:
                    self.length_slider.configure(to=custom_length)
                    self.length_slider_max = custom_length
                self.length_slider.set(custom_length)
                self.update_length_label(custom_length)
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def generate_password(self):
        try:
            length = int(self.length_slider.get())
            characters = ""
            if self.var_upper.get():
                characters += string.ascii_uppercase
            if self.var_lower.get():
                characters += string.ascii_lowercase
            if self.var_digits.get():
                characters += string.digits
            
            if self.var_symbols_custom.get():
                characters += self.var_symbols_custom.get()
            elif self.var_symbols.get():
                characters += string.punctuation

            exclude_chars = self.var_exclude_chars.get()
            for char in exclude_chars:
                characters = characters.replace(char, "")

            if not characters:
                CTkMessagebox(title="Info", message="No characters available for password generation. Please check the settings.")
                return

            password = ""
            while len(password) < length:
                char = random.choice(characters)
                if char not in exclude_chars:
                    password += char

            self.password_entry.configure(state='normal')
            self.password_entry.delete(0, 'end')
            self.password_entry.insert(0, password)
            self.password_entry.configure(state='readonly')

            self.password_history.append(password)

            with open(self.password_history_file, 'w') as f:
                json.dump(self.password_history, f)
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def batch_generate_password(self):
        try:
            self.var_upper_batch = None
            self.var_lower_batch = None
            self.var_digits_batch = None
            self.var_symbols_batch = None
            self.var_random_length_batch = None
            self.var_length_batch = None
            self.var_quantity_batch = None
            self.var_symbols_custom_batch = tk.StringVar(value="")
            self.var_exclude_chars_batch = tk.StringVar(value="")

            self.batch_frame = ctk.CTkFrame(self.main_frame)
            self.batch_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

            self.right_frame.grid_remove()

            self.batch_button.configure(text="Back to Main Page", command=self.back_to_main_page)

            self.var_upper_batch = tk.BooleanVar(value=True)
            self.check_upper_batch = ctk.CTkCheckBox(self.batch_frame, text="Include Uppercase Letters", variable=self.var_upper_batch)
            createToolTip(self.check_upper_batch, "Check this to include at least one uppercase letter in the passwords.")
            self.check_upper_batch.grid(row=0, column=0, sticky="ew", pady=10)

            self.var_lower_batch = tk.BooleanVar(value=True)
            self.check_lower_batch = ctk.CTkCheckBox(self.batch_frame, text="Include Lowercase Letters", variable=self.var_lower_batch)
            createToolTip(self.check_lower_batch, "Check this to include at least one lowercase letter in the passwords.")
            self.check_lower_batch.grid(row=1, column=0, sticky="ew", pady=10)

            self.var_digits_batch = tk.BooleanVar(value=True)
            self.check_digits_batch = ctk.CTkCheckBox(self.batch_frame, text="Include Digits", variable=self.var_digits_batch)
            createToolTip(self.check_digits_batch, "Check this to include at least one digit in the passwords.")
            self.check_digits_batch.grid(row=2, column=0, sticky="ew", pady=10)

            self.var_symbols_batch = tk.BooleanVar(value=True)
            self.check_symbols_batch = ctk.CTkCheckBox(self.batch_frame, text="Include Symbols", variable=self.var_symbols_batch)
            createToolTip(self.check_symbols_batch, "Check this to include at least one symbol in the passwords.")
            self.check_symbols_batch.grid(row=3, column=0, sticky="ew", pady=10)

            self.var_random_length_batch = tk.BooleanVar(value=False)
            self.check_random_length_batch = ctk.CTkCheckBox(self.batch_frame, text="Random Length", variable=self.var_random_length_batch)
            createToolTip(self.check_random_length_batch, "Check this to generate passwords with a length\nrandomly chosen between 1 and the value set by the length slider.")
            self.check_random_length_batch.grid(row=4, column=0, sticky="ew", pady=10)

            self.button_symbols_custom_batch = ctk.CTkButton(self.batch_frame, text="⮞", command=self.set_symbols_custom_batch, width=30)
            createToolTip(self.button_symbols_custom_batch, "Click to set custom symbols for the passwords.")
            self.button_symbols_custom_batch.grid(row=3, column=1)

            self.button_exclude_chars_batch = ctk.CTkButton(self.batch_frame, text="⮞", command=self.set_exclude_chars_batch, width=30)
            createToolTip(self.button_exclude_chars_batch, "Click to set characters to exclude from the passwords.")
            self.button_exclude_chars_batch.grid(row=10, column=1)

            self.var_length_batch = tk.IntVar(value=20)
            self.length_slider_batch = ctk.CTkSlider(self.batch_frame, from_=1, to=50, variable=self.var_length_batch, command=self.update_length_batch)
            createToolTip(self.length_slider_batch, "Slide this to set the length of the passwords.")
            self.length_slider_batch.grid(row=6, column=0)

            self.length_label_batch = ctk.CTkLabel(self.batch_frame, textvariable=self.var_length_batch)
            createToolTip(self.length_label_batch, "This shows the current length of the passwords. Click to set a custom length.")
            self.length_label_batch.grid(row=7, column=0)
            self.length_label_batch.bind("<Button-1>", self.set_length_batch)

            self.var_quantity_batch = tk.IntVar(value=10)
            self.quantity_slider_batch = ctk.CTkSlider(self.batch_frame, from_=1, to=100, variable=self.var_quantity_batch, command=self.update_quantity_batch)
            createToolTip(self.quantity_slider_batch, "Slide this to set the quantity of the passwords.")
            self.quantity_slider_batch.grid(row=8, column=0)

            self.quantity_label_batch = ctk.CTkLabel(self.batch_frame, textvariable=self.var_quantity_batch)
            createToolTip(self.quantity_label_batch, "This shows the current quantity of the passwords. Click to set a custom quantity.")
            self.quantity_label_batch.grid(row=9, column=0)
            self.quantity_label_batch.bind("<Button-1>", self.set_quantity_batch)

            self.generate_button_batch = ctk.CTkButton(self.batch_frame, text="Generate Passwords", command=self.generate_passwords_batch)
            createToolTip(self.generate_button_batch, "Click here to generate passwords.")
            self.generate_button_batch.grid(row=10, column=0,sticky="ew", pady=10, padx=10)

            self.password_display_batch = CTkListbox(self.batch_frame, width=200, height=200)
            self.password_display_batch.grid(row=11, column=0, sticky="nsew")

            self.copy_all_button_batch = ctk.CTkButton(self.batch_frame, text="Copy All", command=self.copy_all_passwords_batch)
            createToolTip(self.copy_all_button_batch, "Click to copy all the generated passwords")
            self.copy_all_button_batch.grid(row=12, column=0, sticky="ew", pady=10)
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def update_length_batch(self, event):
        try:
            self.var_length_batch.set(round(self.var_length_batch.get()))
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def set_length_batch(self, event):
        try:
            result = ctk.CTkInputDialog(text="Enter password length:", title="Set Length", ) 
            length = result.get_input()
            if length is not None and length.isdigit():
                self.var_length_batch.set(int(length))
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def update_quantity_batch(self, event):
        try:
            self.var_quantity_batch.set(round(self.var_quantity_batch.get()))
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def set_quantity_batch(self, event):
        try:
            result = ctk.CTkInputDialog(text="Enter password quantity:", title="Set Quantity", ) 
            quantity = result.get_input()
            if quantity is not None and quantity.isdigit():
                self.var_quantity_batch.set(int(quantity))
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def generate_passwords_batch(self):
        try:
            quantity = self.var_quantity_batch.get()
            characters = ""
            if self.var_upper_batch.get():
                characters += string.ascii_uppercase
            if self.var_lower_batch.get():
                characters += string.ascii_lowercase
            if self.var_digits_batch.get():
                characters += string.digits
            if self.var_symbols_batch.get():
                characters += self.var_symbols_custom_batch.get() if self.var_symbols_custom_batch.get() else string.punctuation

            characters = "".join(c for c in characters if c not in self.var_exclude_chars_batch.get())

            passwords = []
            if characters:
                for _ in range(quantity):
                    if self.var_random_length_batch.get():
                        length = random.randint(1, self.var_length_batch.get())
                    else:
                        length = self.var_length_batch.get()
                    password = "".join(random.choice(characters) for _ in range(length))
                    passwords.append(password)
            else:
                CTkMessagebox(title="Info", message="No characters available for password generation. Please check the settings.")

            self.password_display_batch.delete(0, 'end')
            for password in passwords:
                self.password_display_batch.insert('end', password)

            self.password_history.extend(passwords)
            self.password_history = self.password_history[-100:]

            with open(self.password_history_file, 'w') as f:
                json.dump(self.password_history, f)

        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def copy_all_passwords_batch(self):
        try:
            if self.password_display_batch.size() == 0:
                CTkMessagebox(title="Info", message="Please generate or enter some passwords first.")
                return
            
            passwords = [self.password_display_batch.get(i) for i in range(self.password_display_batch.size())]
            
            passwords_str = '\n'.join(passwords)
            
            root = self.winfo_toplevel()
            root.clipboard_clear()
            root.clipboard_append(passwords_str)
            root.update()
            
            CTkMessagebox(title="Success", message="Passwords copied to clipboard.")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def set_symbols_custom_batch(self):
        try:
            result = ctk.CTkInputDialog(text="Enter custom symbols:", title="Set Custom Symbols")
            symbols_custom = result.get_input()
            if symbols_custom is not None:
                self.var_symbols_custom_batch.set(symbols_custom)
                if symbols_custom:
                    self.check_symbols_batch.configure(text="Include Custom Symbols")
                else:
                    self.check_symbols_batch.configure(text="Include Symbols")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def set_exclude_chars_batch(self):
        try:
            result = ctk.CTkInputDialog(title="Set Exclude Characters", text="Enter characters to exclude:")
            exclude_chars = result.get_input()
            if exclude_chars is not None:
                self.var_exclude_chars_batch.set(exclude_chars)
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def show_password_history(self):
        try:
            self.history_frame = ctk.CTkFrame(self.main_frame)
            self.history_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

            self.right_frame.grid_remove()

            self.history_button.configure(text="Back to Main Page", command=self.back_to_main_page)
                
            self.history_display = CTkListbox(self.history_frame, width=550, height=420) 
            createToolTip(self.history_display, "The password history will be displayed here")
            for password in self.password_history[-100:]:
                self.history_display.insert('end', password)
            self.history_display.grid(row=2, column=0, sticky="nsew")

            self.clear_button = ctk.CTkButton(self.history_frame, text="Clear History", command=self.clear_password_history)
            createToolTip(self.clear_button, "Click to clear the password history.")
            self.clear_button.grid(row=3, column=0, pady=10, sticky="ew")

            self.copy_all_button = ctk.CTkButton(self.history_frame, text="Copy All", command=self.copy_all_history)
            createToolTip(self.copy_all_button, "Click to copy all the password history.")
            self.copy_all_button.grid(row=4, column=0, pady=10, sticky="ew")

            self.export_button = ctk.CTkButton(self.history_frame, text="Export Password History", command=self.export_password_history)
            createToolTip(self.export_button, "Click to export password history.")
            self.export_button.grid(row=5, column=0, pady=10, sticky="ew")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def back_to_main_page(self):
        try:
            self.right_frame.grid()

            if hasattr(self, 'shortcuts_frame'):
                self.shortcuts_frame.destroy()

            if hasattr(self, 'history_frame'):
                self.history_frame.destroy()

            if hasattr(self, 'batch_frame'):
                self.batch_frame.destroy()

            self.history_button.configure(text="Password History", command=self.show_password_history)
            self.batch_button.configure(text="Batch Generate Passwords", command=self.batch_generate_password)
            self.shortcuts_button.configure(text="View Shortcuts", command=self.show_shortcuts)
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def clear_password_history(self):
        try:
            if not self.password_history:
                CTkMessagebox(title="Info", message="Password history is already empty.")
                return

            self.password_history.clear()

            with open(self.password_history_file, 'w') as f:
                json.dump(self.password_history, f)

            if self.history_display is not None:
                self.history_display.delete(0, 'end')

            CTkMessagebox(title="Clear History", message="Password history has been cleared.")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def copy_all_history(self):
        try:
            if self.password_history:
                pyperclip.copy('\n'.join(self.password_history))
                CTkMessagebox(title="Copy All", message="Password history has been copied to the clipboard.")
            else:
                CTkMessagebox(title="Info", message="Password history is empty.")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def export_password_history(self):
        try:
            if self.password_history:
                filename = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="password_history.txt")
                if filename:
                    with open(filename, 'w') as f:
                        f.write('\n'.join(self.password_history))
            else:
                CTkMessagebox(title="Info", message="Password history is empty.")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def apply_template(self, template_name):
        try:
            template = self.templates[template_name]
            self.var_upper.set(template["upper"])
            self.var_lower.set(template["lower"])
            self.var_digits.set(template["digits"])
            self.var_symbols.set(template["symbols"])
            self.var_random_length.set(template["random_length"])
            self.var_length.set(f"Length: {template['length']}")
            self.length_slider.set(template["length"])
            self.var_symbols_custom.set(template.get("custom_symbols", ""))
            self.var_exclude_chars.set(template.get("exclude_chars", ""))
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def copy_password(self):
        try:
            self.clipboard_clear()
            if self.password_entry.get():
                self.clipboard_append(self.password_entry.get())
                self.update()
            else:
                CTkMessagebox(title="Info", message="Please generate or enter a password first.")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def generate_qr(self):
        try:
            password = self.password_entry.get()
            if password:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(password)
                qr.make(fit=True)
                img = qr.make_image(fill='black', back_color='white')
                filename = filedialog.asksaveasfilename(defaultextension=".png", initialfile="password_qr_code.png", filetypes=[("PNG Image", "*.png")])
                if filename:
                    img.save(filename)
            else:
                CTkMessagebox(title="Info", message="Please generate or enter a password first.")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def save_password(self, event=None):
        try:
            if self.password_entry.get():
                filename = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="password.txt")
                if filename:
                    with open(filename, 'w') as f:
                        f.write(self.password_entry.get())
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def delete_password(self):
        try:
            self.password_entry.configure(state='normal')
            self.password_entry.delete(0, tk.END)
            self.password_entry.configure(state='readonly')
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def delete_and_copy_password(self):
        try:
            self.copy_password()
            self.delete_password()
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def send_feedback(self):
        try:

            webbrowser.open("https://github.com/fatherxtreme123/Secure.Password.Generator/issues")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

    def show_shortcuts(self):
        try:
            shortcuts_info = (
                "Keyboard Shortcuts:\n"
                "Ctrl + G: Generate Password\n"
                "Ctrl + C: Copy Password\n"
                "Ctrl + Q: Generate QR Code\n"
                "Ctrl + D: Delete Password\n"
                "Ctrl + E: Export Password History\n"
                "Ctrl + S: Save Password\n"
                "Ctrl + F: Send Feedback"
            )
            self.shortcuts_frame = ctk.CTkFrame(self.main_frame)
            self.shortcuts_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

            self.right_frame.grid_remove()

            self.shortcuts_button.configure(text="Back to Main Page", command=self.back_to_main_page)

            self.shortcuts_label = ctk.CTkLabel(self.shortcuts_frame, text=shortcuts_info)
            self.shortcuts_label.grid(padx=10, pady=10)

        except Exception as e:
            CTkMessagebox(title="Error", message=f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        CTkMessagebox(title="Error", message=f"An error occurred: {e}")
