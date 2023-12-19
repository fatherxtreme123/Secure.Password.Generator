# Secure Password Generator

## Overview
Secure Password Generator is a Python application built with Tkinter, designed to generate strong and secure passwords. This application provides a user-friendly interface with various customization options, ensuring the creation of robust passwords tailored to your requirements.

## Features
1. **Customizable Password Generation**
   - Include or exclude uppercase letters, lowercase letters, digits, and symbols in your generated passwords.
   - Set the length of the password or choose to generate a password with a random length.

2. **Templates**
   - Select predefined templates to quickly apply common password configurations.

3. **Custom Symbols and Exclusions**
   - Define custom symbols to include in passwords.
   - Specify characters to exclude from generated passwords.

4. **Password History**
   - View and manage a history of generated passwords.
   - Copy individual passwords or the entire history to the clipboard.

5. **QR Code Generation**
   - Generate a QR code for a password, providing an alternative way to share or store passwords securely.

6. **Batch Password Generation**
   - Quickly generate multiple passwords with specified configurations.

7. **Export and Save**
   - Export password history to a text file.
   - Save individual passwords to text files.

## Usage Instructions
1. **Password Generation**
   - Configure your password preferences using the provided checkboxes and sliders.
   - Click the "Generate Password" button to create a password based on your settings.

2. **Templates**
   - Choose from predefined templates for common password configurations.

3. **Customization**
   - Use the "Set Custom Symbols" button to define custom symbols for password generation.
   - Use the "Set Exclude Characters" button to specify characters to exclude from generated passwords.

4. **Password History**
   - Click the "Password History" button to view a history of generated passwords.
   - Clear the history, copy passwords, or export the history to a text file.

5. **QR Code Generation**
   - Click the "Generate password QR code" button to create a QR code for the current password.

6. **Batch Password Generation**
   - Click the "Batch Generate Passwords" button to generate multiple passwords at once.

7. **Copy and Save**
   - Use the "Copy Password" button to copy the current password to the clipboard.
   - Click the password entry to save the current password to a text file.

## Shortcuts
- **Ctrl + C**: Copy the current password to the clipboard.
- **Ctrl + G**: Generate a new password.
- **Ctrl + B**: Batch generate passwords.
- **Ctrl + H**: View password history.
- **Ctrl + E**: Export password history to a text file.
- **Ctrl + S**: Save the current password to a text file.

## Password History
- The password history is stored locally in a JSON file (`password_history.json`).
- Passwords can be cleared, copied, or exported from the password history window.

## Troubleshooting
- If you encounter any issues or errors, refer to the error messages displayed for guidance.
- Ensure that the required dependencies, including Tkinter and TKinterModernThemes, are installed.

## Disclaimer
- Secure Password Generator is provided as-is without any warranties. Use generated passwords responsibly and securely.
