import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import random
import string
import qrcode
import TKinterModernThemes as TKMT
import pyperclip
import os
import json

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

            self.var_upper = tk.BooleanVar(value=True)
            self.var_lower = tk.BooleanVar(value=True)
            self.var_digits = tk.BooleanVar(value=True)
            self.var_symbols = tk.BooleanVar(value=True)
            self.var_symbols_custom = tk.StringVar(value="")
            self.var_exclude_chars = tk.StringVar(value="")
            self.var_length = tk.IntVar(value=20)
            self.var_random_length = tk.BooleanVar(value=False)

            self.check_upper = self.Checkbutton("Include Uppercase Letters", self.var_upper)
            createToolTip(self.check_upper, "Check this to include at least one uppercase letter in the password.")
            self.check_upper.grid(row=0, column=1)
            self.check_lower = self.Checkbutton("Include Lowercase Letters", self.var_lower)
            createToolTip(self.check_lower, "Check this to include at least one lowercase letter in the password.")
            self.check_lower.grid(row=1, column=1)
            self.check_digits = self.Checkbutton("Include Digits", self.var_digits)
            createToolTip(self.check_digits, "Check this to include at least one digit in the password.")
            self.check_digits.grid(row=2, column=1)
            self.check_symbols = self.Checkbutton("Include Symbols", self.var_symbols)
            createToolTip(self.check_symbols, "Check this to include at least one symbol in the password.")
            self.check_symbols.grid(row=3, column=1)
            self.check_random_length = self.Checkbutton("Random Length", self.var_random_length)
            createToolTip(self.check_random_length, "Check this to generate a password with a length\nrandomly chosen between 1 and the value set by the length slider.")
            self.check_random_length.grid(row=4, column=1)

            self.button_symbols_custom = ttk.Button(text="⮞", command=self.set_symbols_custom)
            createToolTip(self.button_symbols_custom, "Click to set custom symbols for the password.")
            self.button_symbols_custom.grid(row=3, column=2)
            self.button_exclude_chars = ttk.Button(text="⮞", command=self.set_exclude_chars)
            createToolTip(self.button_exclude_chars, "Click to set characters to exclude from the password.")
            self.button_exclude_chars.grid(row=5, column=2)

            self.length_slider = ttk.Scale(from_=1, to=50, variable=self.var_length, orient="horizontal", command=self.update_length)
            createToolTip(self.length_slider, "Slide this to set the length of the password.")
            self.length_slider.grid(row=6, column=1)

            self.length_label = ttk.Label(textvariable=self.var_length)
            createToolTip(self.length_label, "This shows the current length of the password. Click to set a custom length.")
            self.length_label.grid(row=7, column=1)
            self.length_label.bind("<Button-1>", self.set_length)

            self.templates = {
                "Template 1": {"upper": True, "lower": True, "digits": True, "symbols": True, "length": 20, "random_length": False},
                "Template 2": {"upper": True, "lower": True, "digits": False, "symbols": False, "length": 15, "random_length": True},
                "Template 3": {"upper": False, "lower": True, "digits": True, "symbols": True, "length": 30, "random_length": False},
            }

            self.template_var = tk.StringVar()
            self.template_menu = ttk.OptionMenu(self.master, self.template_var, *self.templates.keys(), command=self.apply_template)
            createToolTip(self.template_menu, "Select a template to apply to the password generation settings.")
            self.template_menu.grid(row=10, column=1)

            self.generate_button = self.Button("Generate Password", self.generate_password)
            createToolTip(self.generate_button, "Click here to generate a password.")
            self.generate_button.grid(row=5, column=1)

            self.password_entry = ttk.Entry(show="", state="readonly")
            createToolTip(self.password_entry, "The generated password will be displayed here")
            self.password_entry.grid(row=9, column=1)
            self.password_entry.bind("<Button-1>", self.save_password)

            self.history_display = None

            self.sidebar = ttk.Frame(self.master)
            self.sidebar.grid(row=0, column=0, sticky="ns")

            self.copy_password_button = ttk.Button(self.sidebar, text="Copy Password", command=self.copy_password)
            createToolTip(self.copy_password_button, "Click to copy the generated password")
            self.copy_password_button.grid(row=0, column=0, sticky="ew")

            self.qr_button = ttk.Button(self.sidebar, text="Generate password QR code", command=self.generate_qr)
            createToolTip(self.qr_button, "Click to generate password QR code")
            self.qr_button.grid(row=1, column=0, sticky="ew")

            self.batch_generate_button = ttk.Button(self.sidebar, text="Batch Generate Passwords", command=self.batch_generate_passwords)
            createToolTip(self.batch_generate_button, "Click to batch generate passwords")
            self.batch_generate_button.grid(row=2, column=0, sticky="ew")

            self.history_button = ttk.Button(self.sidebar, text="Password History", command=self.show_password_history)
            createToolTip(self.history_button, "Click to view password history")
            self.history_button.grid(row=3, column=0, sticky="ew")

            self.password_history_file = 'password_history.json'
            if os.path.exists(self.password_history_file):
                with open(self.password_history_file, 'r') as f:
                    self.password_history = json.load(f)
            else:
                self.password_history = []

            self.master.bind("<Control-c>", lambda event: self.copy_password())
            self.master.bind("<Control-g>", lambda event: self.generate_password())
            self.master.bind("<Control-b>", lambda event: self.batch_generate_passwords())
            self.master.bind("<Control-h>", lambda event: self.show_password_history())
            self.master.bind("<Control-e>", lambda event: self.export_password_history())
            self.master.bind("<Control-s>", self.save_password)

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

    def batch_generate_passwords(self):
        try:
            num_passwords = simpledialog.askinteger("Number of Passwords", "Enter the number of passwords to generate:", initialvalue=2)
            if num_passwords is not None:
                upper = messagebox.askyesno("Uppercase Letters", "Should the password include uppercase letters?")
                lower = messagebox.askyesno("Lowercase Letters", "Should the password include lowercase letters?")
                digits = messagebox.askyesno("Digits", "Should the password include digits?")
                symbols = messagebox.askyesno("Symbols", "Should the password include symbols?")
                length = simpledialog.askinteger("Password Length", "Enter the length of the password:", initialvalue=self.var_length.get())
                characters = ""
                if upper:
                    characters += string.ascii_uppercase
                if lower:
                    characters += string.ascii_lowercase
                if digits:
                    characters += string.digits
                if symbols:
                    characters += self.var_symbols_custom.get() if self.var_symbols_custom.get() else string.punctuation
                passwords = ["".join(random.choice(characters) for _ in range(length)) for _ in range(num_passwords)]
                pyperclip.copy('\n'.join(passwords))
                messagebox.showinfo("Passwords Generated", f"{num_passwords} passwords have been generated and copied to the clipboard.")

                self.password_history.extend(passwords)

                with open(self.password_history_file, 'w') as f:
                    json.dump(self.password_history, f)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def copy_password(self):
        try:
            self.master.clipboard_clear()
            self.master.clipboard_append(self.password_entry.get())
            self.master.update()
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
            history_window = tk.Toplevel(self.master)
            history_window.title("Password History")
            history_window.resizable(False, False)

            self.history_display = tk.Text(history_window, state="disabled")
            self.history_display.insert('end', '\n'.join(self.password_history))
            self.history_display.config(state="normal")
            self.history_display.insert('end', '\n'.join(self.password_history))
            self.history_display.config(state="disabled")
            self.history_display.grid()

            clear_button = ttk.Button(history_window, text="Clear History", command=self.clear_password_history)
            createToolTip(clear_button, "Click and reopen history before the history will be cleared.")
            clear_button.grid(row=1, column=0, sticky="ew")

            self.copy_all_button = ttk.Button(history_window, text="Copy All", command=self.copy_all_history)
            createToolTip(self.copy_all_button, "Click to copy all the password history")
            self.copy_all_button.grid(row=2, column=0, sticky="ew")

            self.export_button = ttk.Button(history_window, text="Export Password History", command=self.export_password_history)
            createToolTip(self.export_button, "Click to export password history")
            self.export_button.grid(row=3, column=0, sticky="ew")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def clear_password_history(self):
        try:
            if self.password_history:
                self.password_history = []
                if self.history_display is not None:
                    self.history_display.delete('1.0', 'end')

            else:
                messagebox.showinfo("Info", "Password history is already empty.")
            with open(self.password_history_file, 'w') as f:
                json.dump(self.password_history, f)
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

if __name__ == "__main__":
    try:
        App().run()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")