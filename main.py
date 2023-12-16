import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import random
import string
import qrcode
import TKinterModernThemes as TKMT
import pyperclip
import os
import json
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
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root}+{event.y_root}")
            label = tk.Label(tooltip, text=text, background="black", foreground="white")
            label.grid()
            widget._tooltip = tooltip

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

class App(TKMT.ThemedTKinterFrame):
    def __init__(self):
        try:
            super().__init__("Secure Password Generator", "Sun-valley", "dark")
            self.master.iconbitmap('Secure Password Generator.ico')
            self.master.resizable(False, False)

            self.main_frame = ttk.Frame(self.master)
            self.main_frame.grid(row=0, column=0, sticky="nsew")

            self.left_frame = ttk.Frame(self.main_frame, width=200, height=400)
            self.left_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ns")

            self.right_frame = ttk.Frame(self.main_frame)
            self.right_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

            self.var_upper = tk.BooleanVar(value=True)
            self.var_lower = tk.BooleanVar(value=True)
            self.var_digits = tk.BooleanVar(value=True)
            self.var_symbols = tk.BooleanVar(value=True)
            self.var_symbols_custom = tk.StringVar(value="")
            self.var_exclude_chars = tk.StringVar(value="")
            self.var_length = tk.IntVar(value=20)
            self.var_random_length = tk.BooleanVar(value=False)

            self.check_upper = ttk.Checkbutton(self.right_frame, text="Include Uppercase Letters", variable=self.var_upper)
            createToolTip(self.check_upper, "Check this to include at least one uppercase letter in the password.")
            self.check_upper.grid(row=0, column=1, sticky="ew", pady=10)
            self.check_lower = ttk.Checkbutton(self.right_frame, text="Include Lowercase Letters", variable=self.var_lower)
            createToolTip(self.check_lower, "Check this to include at least one lowercase letter in the password.")
            self.check_lower.grid(row=1, column=1, sticky="ew", pady=10)
            self.check_digits = ttk.Checkbutton(self.right_frame, text="Include Digits", variable=self.var_digits)
            createToolTip(self.check_digits, "Check this to include at least one digit in the password.")
            self.check_digits.grid(row=2, column=1, sticky="ew", pady=10)
            self.check_symbols = ttk.Checkbutton(self.right_frame, text="Include Symbols", variable=self.var_symbols)
            createToolTip(self.check_symbols, "Check this to include at least one symbol in the password.")
            self.check_symbols.grid(row=3, column=1, sticky="ew", pady=10)
            self.check_random_length = ttk.Checkbutton(self.right_frame, text="Random Length", variable=self.var_random_length)
            createToolTip(self.check_random_length, "Check this to generate a password with a length\nrandomly chosen between 1 and the value set by the length slider.")
            self.check_random_length.grid(row=4, column=1, sticky="ew", pady=10)

            self.button_symbols_custom = ttk.Button(self.right_frame, text="⮞", command=self.set_symbols_custom)
            createToolTip(self.button_symbols_custom, "Click to set custom symbols for the password.")
            self.button_symbols_custom.grid(row=3, column=2)
            self.button_exclude_chars = ttk.Button(self.right_frame, text="⮞", command=self.set_exclude_chars)
            createToolTip(self.button_exclude_chars, "Click to set characters to exclude from the password.")
            self.button_exclude_chars.grid(row=5, column=2)

            self.length_slider = ttk.Scale(self.right_frame, from_=1, to=50, variable=self.var_length, orient="horizontal", command=self.update_length)
            createToolTip(self.length_slider, "Slide this to set the length of the password.")
            self.length_slider.grid(row=6, column=1)

            self.length_label = ttk.Label(self.right_frame, textvariable=self.var_length)
            createToolTip(self.length_label, "This shows the current length of the password. Click to set a custom length.")
            self.length_label.grid(row=7, column=1)
            self.length_label.bind("<Button-1>", self.set_length)

            self.templates = {
                "Template 1": {"upper": True, "lower": True, "digits": True, "symbols": True, "length": 20, "random_length": False},
                "Template 2": {"upper": True, "lower": True, "digits": False, "symbols": False, "length": 15, "random_length": True},
                "Template 3": {"upper": False, "lower": True, "digits": True, "symbols": True, "length": 30, "random_length": False},
                "Template 4": {"upper": True, "lower": True, "digits": True, "symbols": True, "length": 99, "random_length": False},
            }

            self.template_var = tk.StringVar()
            self.template_menu = ttk.OptionMenu(self.right_frame, self.template_var, *self.templates.keys(), command=self.apply_template)
            createToolTip(self.template_menu, "Select a template to apply to the password generation settings.")
            self.template_menu.grid(row=10, column=1)

            self.generate_button = ttk.Button(self.right_frame, text="Generate Password", command=self.generate_password)
            createToolTip(self.generate_button, "Click here to generate a password.")
            self.generate_button.grid(row=5, column=1,sticky="ew", pady=10, padx=10)

            self.password_entry = ttk.Entry(self.right_frame, show="", state="readonly")
            createToolTip(self.password_entry, "The generated password will be displayed here")
            self.password_entry.grid(row=9, column=1, sticky="nsew")
            self.password_entry.bind("<Button-1>", self.save_password)

            self.copy_password_button = ttk.Button(self.left_frame, text="Copy Password", command=self.copy_password)
            createToolTip(self.copy_password_button, "Click to copy the generated password")
            self.copy_password_button.grid(row=0, column=0, sticky="ew", pady=10)

            self.qr_button = ttk.Button(self.left_frame, text="Generate password QR code", command=self.generate_qr)
            createToolTip(self.qr_button, "Click to generate password QR code")
            self.qr_button.grid(row=1, column=0, sticky="ew", pady=10)

            self.history_button = ttk.Button(self.left_frame, text="Password History", command=self.show_password_history)
            createToolTip(self.history_button, "Click to view password history")
            self.history_button.grid(row=2, column=0, sticky="ew", pady=10)

            self.batch_button = ttk.Button(self.left_frame, text="Batch Generate Password", command=self.batch_generate_password)
            createToolTip(self.batch_button, "Click to batch generate passwords.")
            self.batch_button.grid(row=3, column=0, sticky="ew", pady=10)

            self.delete_password_button = ttk.Button(self.left_frame, text="Delete Password", command=self.delete_password)
            createToolTip(self.delete_password_button, "Click to delete the password from the entry")
            self.delete_password_button.grid(row=4, column=0, sticky="ew", pady=10)

            self.delete_and_copy_password_button = ttk.Button(self.left_frame, text="Delete and Copy Password", command=self.delete_and_copy_password)
            createToolTip(self.delete_and_copy_password_button, "Click to delete the password from the entry and copy it to the clipboard")
            self.delete_and_copy_password_button.grid(row=5, column=0, sticky="ew", pady=10)

            self.send_feedback_button = ttk.Button(self.left_frame, text="Send Feedback", command=self.send_feedback)
            createToolTip(self.send_feedback_button, "Click to open the GitHub issues page and send feedback")
            self.send_feedback_button.grid(row=6, column=0, sticky="ew", pady=10)

            self.shortcuts_button = ttk.Button(self.left_frame, text="View Shortcuts", command=self.show_shortcuts)
            createToolTip(self.shortcuts_button, "Click to view keyboard shortcuts")
            self.shortcuts_button.grid(row=7, column=0, sticky="ew", pady=10)

            self.history_display = None

            self.password_history_file = 'password_history.json'
            if os.path.exists(self.password_history_file):
                with open(self.password_history_file, 'r') as f:
                    self.password_history = json.load(f)
            else:
                self.password_history = []

            self.master.bind("<Control-g>", lambda event: self.generate_password())
            self.master.bind("<Control-c>", lambda event: self.copy_password())
            self.master.bind("<Control-q>", lambda event: self.generate_qr())
            self.master.bind("<Control-d>", lambda event: self.delete_password())
            self.master.bind("<Control-e>", lambda event: self.export_password_history())
            self.master.bind("<Control-s>", lambda event: self.save_password(event))
            self.master.bind("<Control-f>", lambda event: self.send_feedback())

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def generate_password(self):
        try:
            length = random.randint(1, self.var_length.get()) if self.var_random_length.get() else self.var_length.get()
            characters = ""
            if self.var_upper.get():
                characters += string.ascii_uppercase
            if self.var_lower.get():
                characters += string.ascii_lowercase
            if self.var_digits.get():
                characters += string.digits
            if self.var_symbols.get():
                characters += self.var_symbols_custom.get() if self.var_symbols_custom.get() else string.punctuation

            characters = "".join(c for c in characters if c not in self.var_exclude_chars.get())

            if characters:
                password = "".join(random.choice(characters) for _ in range(length))
            else:
                password = "Please select at least one option to generate password."

            self.password_entry.config(state='normal')
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, password)
            self.password_entry.config(state='readonly')

            self.password = password

            self.password_history.append(password)

            with open(self.password_history_file, 'w') as f:
                json.dump(self.password_history, f)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

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

            self.batch_frame = ttk.Frame(self.main_frame)
            self.batch_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

            self.right_frame.grid_remove()

            self.batch_button.config(text="Back to Main Page", command=self.back_to_main_page)

            self.var_upper_batch = tk.BooleanVar(value=True)
            self.check_upper_batch = ttk.Checkbutton(self.batch_frame, text="Include Uppercase Letters", variable=self.var_upper_batch)
            createToolTip(self.check_upper_batch, "Check this to include at least one uppercase letter in the passwords.")
            self.check_upper_batch.grid(row=0, column=0, sticky="ew", pady=10)

            self.var_lower_batch = tk.BooleanVar(value=True)
            self.check_lower_batch = ttk.Checkbutton(self.batch_frame, text="Include Lowercase Letters", variable=self.var_lower_batch)
            createToolTip(self.check_lower_batch, "Check this to include at least one lowercase letter in the passwords.")
            self.check_lower_batch.grid(row=1, column=0, sticky="ew", pady=10)

            self.var_digits_batch = tk.BooleanVar(value=True)
            self.check_digits_batch = ttk.Checkbutton(self.batch_frame, text="Include Digits", variable=self.var_digits_batch)
            createToolTip(self.check_digits_batch, "Check this to include at least one digit in the passwords.")
            self.check_digits_batch.grid(row=2, column=0, sticky="ew", pady=10)

            self.var_symbols_batch = tk.BooleanVar(value=True)
            self.check_symbols_batch = ttk.Checkbutton(self.batch_frame, text="Include Symbols", variable=self.var_symbols_batch)
            createToolTip(self.check_symbols_batch, "Check this to include at least one symbol in the passwords.")
            self.check_symbols_batch.grid(row=3, column=0, sticky="ew", pady=10)

            self.var_random_length_batch = tk.BooleanVar(value=False)
            self.check_random_length_batch = ttk.Checkbutton(self.batch_frame, text="Random Length", variable=self.var_random_length_batch)
            createToolTip(self.check_random_length_batch, "Check this to generate passwords with a length\nrandomly chosen between 1 and the value set by the length slider.")
            self.check_random_length_batch.grid(row=4, column=0, sticky="ew", pady=10)

            self.button_symbols_custom_batch = ttk.Button(self.batch_frame, text="⮞", command=self.set_symbols_custom_batch)
            createToolTip(self.button_symbols_custom_batch, "Click to set custom symbols for the passwords.")
            self.button_symbols_custom_batch.grid(row=3, column=1)

            self.button_exclude_chars_batch = ttk.Button(self.batch_frame, text="⮞", command=self.set_exclude_chars_batch)
            createToolTip(self.button_exclude_chars_batch, "Click to set characters to exclude from the passwords.")
            self.button_exclude_chars_batch.grid(row=10, column=1)

            self.var_length_batch = tk.IntVar(value=20)
            self.length_slider_batch = ttk.Scale(self.batch_frame, from_=1, to=50, variable=self.var_length_batch, orient="horizontal", command=self.update_length_batch)
            createToolTip(self.length_slider_batch, "Slide this to set the length of the passwords.")
            self.length_slider_batch.grid(row=6, column=0)

            self.length_label_batch = ttk.Label(self.batch_frame, textvariable=self.var_length_batch)
            createToolTip(self.length_label_batch, "This shows the current length of the passwords. Click to set a custom length.")
            self.length_label_batch.grid(row=7, column=0)
            self.length_label_batch.bind("<Button-1>", self.set_length_batch)

            self.var_quantity_batch = tk.IntVar(value=10)
            self.quantity_slider_batch = ttk.Scale(self.batch_frame, from_=1, to=100, variable=self.var_quantity_batch, orient="horizontal", command=self.update_quantity_batch)
            createToolTip(self.quantity_slider_batch, "Slide this to set the quantity of the passwords.")
            self.quantity_slider_batch.grid(row=8, column=0)

            self.quantity_label_batch = ttk.Label(self.batch_frame, textvariable=self.var_quantity_batch)
            createToolTip(self.quantity_label_batch, "This shows the current quantity of the passwords. Click to set a custom quantity.")
            self.quantity_label_batch.grid(row=9, column=0)
            self.quantity_label_batch.bind("<Button-1>", self.set_quantity_batch)

            self.generate_button_batch = ttk.Button(self.batch_frame, text="Generate Passwords", command=self.generate_passwords_batch)
            createToolTip(self.generate_button_batch, "Click here to generate passwords.")
            self.generate_button_batch.grid(row=10, column=0,sticky="ew", pady=10, padx=10)

            self.password_display_batch = tk.Text(self.batch_frame, state="disabled")
            createToolTip(self.password_display_batch, "The generated passwords will be displayed here")
            self.password_display_batch.grid(row=11, column=0, sticky="nsew")

            scrollbar = ttk.Scrollbar(self.batch_frame, command=self.password_display_batch.yview)
            createToolTip(scrollbar, "This is the scrollbar for the password display for batch password generation.")
            scrollbar.grid(row=11, column=1, sticky="ns")
            self.password_display_batch['yscrollcommand'] = scrollbar.set

            self.copy_all_button_batch = ttk.Button(self.batch_frame, text="Copy All", command=self.copy_all_passwords_batch)
            createToolTip(self.copy_all_button_batch, "Click to copy all the generated passwords")
            self.copy_all_button_batch.grid(row=12, column=0, sticky="ew", pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def update_length_batch(self, event):
        try:
            self.var_length_batch.set(round(self.var_length_batch.get()))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def set_length_batch(self, event):
        try:
            length = simpledialog.askstring("Set Length", "Enter password length:", initialvalue=self.var_length_batch.get())
            if length is not None and length.isdigit():
                self.var_length_batch.set(int(length))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def update_quantity_batch(self, event):
        try:
            self.var_quantity_batch.set(round(self.var_quantity_batch.get()))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def set_quantity_batch(self, event):
        try:
            quantity = simpledialog.askstring("Set Quantity", "Enter password quantity:", initialvalue=self.var_quantity_batch.get())
            if quantity is not None and quantity.isdigit():
                self.var_quantity_batch.set(int(quantity))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def generate_passwords_batch(self):
        try:
            length = random.randint(1, self.var_length_batch.get()) if self.var_random_length_batch.get() else self.var_length_batch.get()
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
                    password = "".join(random.choice(characters) for _ in range(length))
                    passwords.append(password)
            else:
                passwords.append("Please select at least one option to generate passwords.")

            self.password_display_batch.config(state='normal')
            self.password_display_batch.delete('1.0', 'end')
            self.password_display_batch.insert('end', '\n'.join(passwords))
            self.password_display_batch.config(state='disabled')

            self.password_history.extend(passwords)

            with open(self.password_history_file, 'w') as f:
                json.dump(self.password_history, f)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def copy_all_passwords_batch(self):
        try:
            self.master.clipboard_clear()
            if self.password_display_batch.get('1.0', 'end').strip():
                self.master.clipboard_append(self.password_display_batch.get('1.0', 'end'))
                self.master.update()
            else:
                messagebox.showinfo("Info", "Please generate or enter some passwords first.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def set_symbols_custom_batch(self):
        try:
            symbols_custom = simpledialog.askstring("Set Custom Symbols", "Enter custom symbols:", initialvalue=self.var_symbols_custom_batch.get())
            if symbols_custom is not None:
                self.var_symbols_custom_batch.set(symbols_custom)
                if symbols_custom:
                    self.check_symbols_batch.config(text="Include Custom Symbols")
                else:
                    self.check_symbols_batch.config(text="Include Symbols")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def set_exclude_chars_batch(self):
        try:
            exclude_chars = simpledialog.askstring("Set Exclude Characters", "Enter characters to exclude:", initialvalue=self.var_exclude_chars_batch.get())
            if exclude_chars is not None:
                self.var_exclude_chars_batch.set(exclude_chars)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def copy_password(self):
            try:
                self.master.clipboard_clear()
                if self.password_entry.get():
                    self.master.clipboard_append(self.password_entry.get())
                    self.master.update()
                else:
                    messagebox.showinfo("Info", "Please generate or enter a password first.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def update_length(self, event):
        try:
            self.var_length.set(round(self.var_length.get()))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def set_length(self, event):
        try:
            length = simpledialog.askstring("Set Length", "Enter password length:", initialvalue=self.var_length.get())
            if length is not None and length.isdigit():
                self.var_length.set(int(length))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def set_symbols_custom(self):
        try:
            symbols_custom = simpledialog.askstring("Set Custom Symbols", "Enter custom symbols:", initialvalue=self.var_symbols_custom.get())
            if symbols_custom is not None:
                self.var_symbols_custom.set(symbols_custom)
                if symbols_custom:
                    self.check_symbols.config(text="Include Custom Symbols")
                else:
                    self.check_symbols.config(text="Include Symbols")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def set_exclude_chars(self):
        try:
            exclude_chars = simpledialog.askstring("Set Exclude Characters", "Enter characters to exclude:", initialvalue=self.var_exclude_chars.get())
            if exclude_chars is not None:
                self.var_exclude_chars.set(exclude_chars)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def apply_template(self, value):
        try:
            template = self.templates[value]
            self.var_upper.set(template["upper"])
            self.var_lower.set(template["lower"])
            self.var_digits.set(template["digits"])
            self.var_symbols.set(template["symbols"])
            self.var_length.set(template["length"])
            self.var_random_length.set(template["random_length"])

            remaining_templates = [k for k in self.templates.keys() if k != value]
            self.template_menu['menu'].delete(0, 'end')
            for template in remaining_templates:
                self.template_menu['menu'].add_command(label=template, command=tk._setit(self.template_var, template, self.apply_template))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def generate_qr(self):
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.password)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')

            filename = filedialog.asksaveasfilename(defaultextension=".png", initialfile="password_qr_code.png")
            if filename:
                img.save(filename)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def show_password_history(self):
        try:
            self.history_frame = ttk.Frame(self.main_frame)
            self.history_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

            self.right_frame.grid_remove()

            self.history_button.config(text="Back to Main Page", command=self.back_to_main_page)
                
            self.history_display = tk.Text(self.history_frame, state="disabled") 
            createToolTip(self.history_display, "The password history will be displayed here")
            self.history_display.config(state="normal")
            self.history_display.insert('end', '\n'.join(self.password_history))
            self.history_display.config(state="disabled")
            self.history_display.grid(row=2, column=0, sticky="nsew")

            scrollbar = ttk.Scrollbar(self.history_frame, command=self.history_display.yview)
            createToolTip(scrollbar, "This is the scrollbar for the password history display.")
            scrollbar.grid(row=2, column=1, sticky="ns")
            self.history_display['yscrollcommand'] = scrollbar.set

            self.clear_button = ttk.Button(self.history_frame, text="Clear History", command=self.clear_password_history)
            createToolTip(self.clear_button, "Click to clear the password history.")
            self.clear_button.grid(row=3, column=0, pady=10, sticky="ew")

            self.copy_all_button = ttk.Button(self.history_frame, text="Copy All", command=self.copy_all_history)
            createToolTip(self.copy_all_button, "Click to copy all the password history.")
            self.copy_all_button.grid(row=4, column=0, pady=10, sticky="ew")

            self.export_button = ttk.Button(self.history_frame, text="Export Password History", command=self.export_password_history)
            createToolTip(self.export_button, "Click to export password history.")
            self.export_button.grid(row=5, column=0, pady=10, sticky="ew")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def back_to_main_page(self):
        try:
            self.right_frame.grid()

            if hasattr(self, 'shortcuts_frame'):
                self.shortcuts_frame.destroy()

            if hasattr(self, 'history_frame'):
                self.history_frame.destroy()

            if hasattr(self, 'batch_frame'):
                self.batch_frame.destroy()

            self.history_button.config(text="Password History", command=self.show_password_history)
            self.batch_button.config(text="Batch Generate Passwords", command=self.batch_generate_password)
            self.shortcuts_button.config(text="View Shortcuts", command=self.show_shortcuts)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def clear_password_history(self):
        try:
            if self.password_history:
                self.password_history = []
                if self.history_display is not None:
                    self.history_display.config(state="normal")
                    self.history_display.delete('1.0', 'end')
                    self.history_display.config(state="disabled")

                with open(self.password_history_file, 'w') as f:
                    json.dump(self.password_history, f)

                messagebox.showinfo("Clear History", "Password history has been cleared.")
            else:
                messagebox.showinfo("Info", "Password history is already empty.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def copy_all_history(self):
        try:
            if self.password_history:
                pyperclip.copy('\n'.join(self.password_history))
                messagebox.showinfo("Copy All", "Password history has been copied to the clipboard.")
            else:
                messagebox.showinfo("Info", "Password history is empty.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def export_password_history(self):
        try:
            if self.password_history:
                filename = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="password_history.txt")
                if filename:
                    with open(filename, 'w') as f:
                        f.write('\n'.join(self.password_history))
            else:
                messagebox.showinfo("Info", "Password history is empty.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def save_password(self, event):
        try:
            if self.password_entry.get() and self.password_entry.get() != "Please select at least one option to generate password.":
                filename = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="password.txt")
                if filename:
                    with open(filename, 'w') as f:
                        f.write(self.password_entry.get())
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def delete_password(self):
        try:
            self.password_entry.config(state='normal')
            self.password_entry.delete(0, tk.END)
            self.password_entry.config(state='readonly')
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def delete_and_copy_password(self):
        try:
            self.copy_password()
            self.delete_password()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def send_feedback(self):
        try:

            webbrowser.open("https://github.com/fatherxtreme123/Secure.Password.Generator/issues")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

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
            self.shortcuts_frame = ttk.Frame(self.main_frame)
            self.shortcuts_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

            self.right_frame.grid_remove()

            self.shortcuts_button.config(text="Back to Main Page", command=self.back_to_main_page)

            self.shortcuts_label = ttk.Label(self.shortcuts_frame, text=shortcuts_info)
            self.shortcuts_label.grid(padx=10, pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        App().run()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
