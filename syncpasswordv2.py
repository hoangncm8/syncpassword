import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import datetime
import random
import string

# Function to write to log file
def log(message):
    log_dir = os.path.join(os.path.expanduser("~"), "Desktop/log")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, datetime.datetime.now().strftime("%m%d%Y") + ".txt")
    timestamp = datetime.datetime.now().strftime("%m%d%Y-%H:%M:%S")
    
    with open(log_file, "a") as f:
        f.write(f"{timestamp} - {message}\n")
    
    print(f"{timestamp} - {message}")  # Output to console for debugging purposes

# Function to generate random password with a minimum length of 9 characters
def generate_random_password(length=9):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

# Function to check if syncpassword account exists
def check_syncpassword_account():
    try:
        result = subprocess.run(["dscl", ".", "-read", "/Users/syncpassword"], capture_output=True, text=True)
        if "No such key" in result.stderr:
            log("syncpassword account does not exist.")
            messagebox.showinfo("Account Check", "syncpassword account does not exist. Press OK to create it.")
            return False
        else:
            log("syncpassword account exists.")
            messagebox.showinfo("Account Check", "syncpassword account exists. Press OK to reset its password.")
            return True
    except Exception as e:
        log(f"Exception occurred while checking syncpassword: {str(e)}")
        return False

# Function to create or reset syncpassword account
def create_or_reset_syncpassword():
    password = generate_random_password()
    
    if not check_syncpassword_account():
        # Create syncpassword account
        log("Creating syncpassword account with admin rights.")
        try:
            subprocess.run(["sudo", "sysadminctl", "-addUser", "syncpassword", "-password", password, "-admin"], check=True)
            log(f"syncpassword account created successfully with password: {password}.")
            messagebox.showinfo("Account Created", f"syncpassword account created successfully with password: {password}.")
        except subprocess.CalledProcessError as e:
            log(f"Failed to create syncpassword account: {str(e)}")
            messagebox.showerror("Error", "Failed to create syncpassword account.")
            return None
    else:
        # Reset syncpassword account
        log("Resetting password for syncpassword account.")
        try:
            subprocess.run(["sudo", "sysadminctl", "-resetPasswordFor", "syncpassword", "-newPassword", password], check=True)
            log(f"Password reset for syncpassword account successfully with new password: {password}.")
            messagebox.showinfo("Password Reset", f"Password reset for syncpassword account successfully with new password: {password}.")
        except subprocess.CalledProcessError as e:
            log(f"Failed to reset password for syncpassword account: {str(e)}")
            messagebox.showerror("Error", "Failed to reset password for syncpassword account.")
            return None

    return password

# Function to check AD connection
def check_ad_connection():
    try:
        result = subprocess.run(["dscl", "localhost", "-read", "/Active Directory/KMS/All Domains"], capture_output=True, text=True)
        if "No such node" in result.stderr or "eDSUnknownNodeName" in result.stderr:
            log("Error: Unable to connect to KMS's domain. Please check network.")
            messagebox.showerror("Connection Error", "Unable to connect to KMS's domain. Please check network!")
            return False
        elif "PrimaryNTDomain: KMS" in result.stdout:
            log("Connected to KMS's domain successfully.")
            messagebox.showinfo("Connection Success", "Connected to KMS's domain successfully!")
            return True
        else:
            log("Unexpected output from AD connection check. Please check network.")
            messagebox.showerror("Unexpected Error", "Unexpected output from AD connection check. Please check network!")
            return False
    except Exception as e:
        log(f"Exception occurred: {str(e)}")
        messagebox.showerror("Exception", f"An error occurred: {str(e)}")
        return False

# Function to execute sysadminctl commands
def execute_sysadminctl(domainname, passworddomain, sudopassword, localadminpassword):
    if check_ad_connection():
        try:
            log("Starting sysadminctl command")
            
            # Disable secureToken with syncpassword
            cmd = ["sudo", "-S", "sysadminctl", "-secureTokenOff", domainname, "-password", passworddomain, "-adminUser", "syncpassword", "-adminPassword", localadminpassword]
            result = subprocess.run(cmd, capture_output=True, text=True, input=sudopassword + "\n")
            if "Incorrect password for" in result.stderr:
                log(f"Incorrect password for {domainname}")
                messagebox.showerror("Password Error", f"Incorrect password for {domainname}")
                return
            elif result.returncode == 0:
                log("secureTokenOff successful.")
                
                # Enable secureToken with syncpassword
                cmd = ["sudo", "-S", "sysadminctl", "-secureTokenOn", domainname, "-password", passworddomain, "-adminUser", "syncpassword", "-adminPassword", localadminpassword]
                result = subprocess.run(cmd, capture_output=True, text=True, input=sudopassword + "\n")
                
                if result.returncode == 0:
                    log("secureTokenOn successful.")
                    messagebox.showinfo("Success", "secureTokenOn successful.")
                else:
                    log(f"secureTokenOn failed. Error code: {result.returncode}")
                    messagebox.showerror("Error", f"secureTokenOn failed. Error code: {result.returncode}")
            else:
                log(f"secureTokenOff failed. Error code: {result.returncode}")
                messagebox.showerror("Error", f"secureTokenOff failed. Error code: {result.returncode}")
        except Exception as e:
            log(f"Exception occurred: {str(e)}")
            messagebox.showerror("Exception", f"An error occurred: {str(e)}")

# Create the UI
def create_ui():
    root = tk.Tk()
    root.title("KMS Domain Authentication")

    tk.Label(root, text="Domain Username:").grid(row=0, column=0, padx=10, pady=10)
    domainname_entry = tk.Entry(root)
    domainname_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(root, text="Domain Password:").grid(row=1, column=0, padx=10, pady=10)
    passworddomain_entry = tk.Entry(root, show="*")
    passworddomain_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(root, text="Sudo Password:").grid(row=2, column=0, padx=10, pady=10)
    sudopassword_entry = tk.Entry(root, show="*")
    sudopassword_entry.grid(row=2, column=1, padx=10, pady=10)

    def on_submit():
        domainname = domainname_entry.get()
        passworddomain = passworddomain_entry.get()
        sudopassword = sudopassword_entry.get()

        if domainname and passworddomain and sudopassword:
            localadminpassword = create_or_reset_syncpassword()  # Check and create/reset syncpassword account first
            if localadminpassword:
                execute_sysadminctl(domainname, passworddomain, sudopassword, localadminpassword)  # Proceed with sysadminctl commands
        else:
            messagebox.showerror("Input Error", "Please fill out all fields.")

    submit_button = tk.Button(root, text="Submit", command=on_submit)
    submit_button.grid(row=3, column=0, columnspan=2, pady=20)

    root.mainloop()

# Run the UI
if __name__ == "__main__":
    create_ui()
