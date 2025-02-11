import tkinter as tk
import subprocess
import random
import string
import os
import sys
from tkinter import messagebox
from datetime import datetime

# Global variables to store random passwords and other important variables
domainname = ""
domainpassword = ""
sudo_password = ""
username = "it"

# Log function
def log(message):
    """Log information."""
    print(message)  # Can be changed to log to a file if needed
    document = os.path.join(os.path.expanduser("~"), "Documents")
    log_dir = os.path.join(document, "synclogs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, datetime.now().strftime("%m%d%Y") + ".log")

    with open(log_file, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {message}\n")

# Check privilege sudo permission
def check_sudo_password():
    """Check the current sudo password."""
    log("Checking the current sudo password.")
    command = "sudo -v"  # Command to check sudo authentication
    error = sudopassword_command(command)

    if error:
        log("Sudo password verification failed.")
        messagebox.showerror("Error", "Sudo password is incorrect or has expired.")
        return False  # Return False if verification fails
    else:
        log("Sudo password is correct!")
        return True  # Return True if verification is successful

def sudopassword_command(command):
    sudo_password = entry_sudo_password.get()
    """Run command with sudo rights and return the result."""
    if sudo_password and domainname and domainpassword:
        try:
            # Check access rights
            subprocess.run(['sudo', '-k'], check=True)  # Reset sudo cache
            # subprocess.run(['sudo', '-S', '-p', '', 'true'], input=f"{sudo_password}\n", text=True, check=True)
            result = subprocess.run(['sudo', '-S'] + command.split(), input=f"{sudo_password}\n", text=True, capture_output=True)
            return result.stdout, result.stderr
        except Exception as e:
            return "", str(e)
    else:
        label_status.config(text="Please enter all information!", fg="red")

### secureTokenOff process ###
def secureTokenOff(domainname, domainpassword, sudo_password, username):
    """Disable secure token."""
    domainname = entry_domain_name.get()  # Store domain name in variable
    domainpassword = entry_domain_password.get()  # Store domain password in variable
    sudo_password = entry_sudo_password.get() # Store sudo password in variable

    log(f"***Start -secureTokenOff process***")
    log("Checking sudo permission")
    
    if sudo_password and domainname and domainpassword:

        # Check sudo password before proceeding
        if not check_sudo_password():
            return  # If sudo password is incorrect, stop the secure token disable process
        
        log(f"Checking the current secure token status of {domainname}")

        # Check Secure Token status
        check_cmd = ["sysadminctl", "-secureTokenStatus", domainname]
        check_result = subprocess.run(check_cmd, capture_output=True, text=True)

        # Log the result
        log(check_result.stdout)  # Log STDOUT result
        log(check_result.stderr)   # Log STDERR result (if any)

        # If the status returned contains "ENABLED", process disable the secure token
        if "ENABLED" in check_result.stderr:
                
            log(f"Starting to disable the secure token for account {domainname}.")
                
            #######################################################
            secureTokenOff_button()
            #######################################################

            log(f"Finished disable secureToken for {domainname}")

            log(f"Checking the secure token status of {domainname}")
            
            # Check Secure Token status
            check_cmd = ["sysadminctl", "-secureTokenStatus", domainname]
            check_result = subprocess.run(check_cmd, capture_output=True, text=True)

            # Log the result
            log(check_result.stdout)  # Log STDOUT result
            log(check_result.stderr)   # Log STDERR result (if any)

            # If the status returned contains "ENABLED", report an error
            if "DISABLED" in check_result.stderr:
                log(check_result.stdout)  # Log STDOUT result
                log(check_result.stderr)   # Log STDERR result (if any)
                log(f"Successfully DISABLED secure token for {domainname}.")
                # messagebox.showinfo("Success!", f"Successfully DISABLED secure token for {domainname}.")
                secureTokenOn(domainname, domainpassword, sudo_password, username)  # Proceed to secureTokenOn function

            elif "Incorrect password" in check_result.stderr:
                log(check_result.stdout)  # Log STDOUT result
                log(check_result.stderr)   # Log STDERR result (if any)
                log(f"Incorrect password for {domainname}. Please check your password.")
                messagebox.showerror("Error!", f"Incorrect password for {domainname}. Please check your password.")

            elif "Operation is not permitted without secure token unlock" in check_result.stderr:
                log(check_result.stdout)  # Log STDOUT result
                log(check_result.stderr)   # Log STDERR result (if any)
                log("Operation is not permitted without secure token unlock")
                messagebox.showerror("Error!", f"Failed to disable secure token for {domainname}. Please check your password.")

            elif "ENABLED" in check_result.stderr:
                log(check_result.stdout)  # Log STDOUT result
                log(check_result.stderr)   # Log STDERR result (if any)
                log(f"Failed to disable secure token for {domainname}.")
                messagebox.showerror("Error!", f"Failed to disable secure token for {domainname}.")

        else:
            log(check_result.stdout)  # Log STDOUT result
            log(check_result.stderr)   # Log STDERR result (if any)
            log(f"Failed to disable secure token for {domainname}. The current secure token status is ENABLED")
            messagebox.showerror("Error!", f"Failed to disable secure token for {domainname}. The current secure token status is ENABLED")
    else:
        label_status.config(text="Please enter all information!", fg="red")
       
#################################################################################################
def secureTokenOn(domainname, domainpassword, sudo_password, username):
    """Enable secure token."""
    domainname = entry_domain_name.get()  # Store domain name in variable
    domainpassword = entry_domain_password.get()  # Store domain password in variable
    sudo_password = entry_sudo_password.get() # Store sudo password in variable

    log(f"***Start -secureTokenOn process***")

    if sudo_password and domainname and domainpassword:
    
        # Check sudo password before proceeding
        if not check_sudo_password():
            return  # If sudo password is incorrect, stop the secure token activation process
        
        log(f"Checking the current secure token status of {domainname}")

        # Check Secure Token status
        check_cmd = ["sysadminctl", "-secureTokenStatus", domainname]
        check_result = subprocess.run(check_cmd, capture_output=True, text=True)

        # Log the result
        log(check_result.stdout)  # Log STDOUT result
        log(check_result.stderr)   # Log STDERR result (if any)

        # If the status returned contains "ENABLED", process disable the secure token
        if "DISABLED" in check_result.stderr:

            log(f"Starting to enable the secure token for account {domainname}.")

            # Run the command to enable Secure Token
            cmd = ["sudo", "sysadminctl", "-secureTokenOn", domainname, "-password", domainpassword, "-adminUser", username, "-adminPassword", sudo_password]
            result = subprocess.run(cmd, capture_output=True, text=True)
            log(result.stdout)  # Log STDOUT result
            log(result.stderr)   # Log STDERR result (if any)

            log(f"Finished enable secureToken for {domainname}")
        
            log(f"Checking the secure token status of {domainname}")
            
            # Check Secure Token status
            check_cmd = ["sysadminctl", "-secureTokenStatus", domainname]
            check_result = subprocess.run(check_cmd, capture_output=True, text=True)

            # Log the result
            log(check_result.stdout)  # Log STDOUT result
            log(check_result.stderr)   # Log STDERR result (if any)

            # Check Secure Token status
            check_cmd = ["sysadminctl", "-secureTokenStatus", domainname]
            check_result = subprocess.run(check_cmd, capture_output=True, text=True)

            # Log the result
            log(check_result.stdout)  # Log STDOUT result
            log(check_result.stderr)   # Log STDERR result (if any)

            # If the status returns "DISABLE", report an error
            if "ENABLED" in check_result.stderr:
                log(check_result.stdout)  # Log STDOUT result
                log(check_result.stderr)   # Log STDERR result (if any)
                log(f"Successfully ENABLED secure token for {domainname}. ")
                messagebox.showinfo("Success", f"Successfully ENABLED secure token for {domainname}!")

            elif "Incorrect password" in check_result.stderr:
                log(check_result.stdout)  # Log STDOUT result
                log(check_result.stderr)   # Log STDERR result (if any)
                log(f"Incorrect password for {domainname}.")
                messagebox.showerror("Error", f"Incorrect password for {domainname}.")

            elif "Operation is not permitted without secure token unlock" in check_result.stderr:
                log(check_result.stdout)  # Log STDOUT result
                log(check_result.stderr)   # Log STDERR result (if any)
                log("Operation is not permitted without secure token unlock.")
                messagebox.showerror("Error!", f"Failed to disable secure token for {domainname}. Please check your new email password.")

            elif "DISABLED" in check_result.stderr:
                log(check_result.stdout)  # Log STDOUT result
                log(check_result.stderr)   # Log STDERR result (if any)
                log(f"Failed to enable secure token for {domainname}.")
                messagebox.showerror("Error", f"Failed to enable secure token for {domainname}.")

        else: 
            log(check_result.stdout)  # Log STDOUT result
            log(check_result.stderr)   # Log STDERR result (if any)
            log(f"Failed to enable secure token for {domainname}. The current secure token status is DISABLED")
            messagebox.showerror("Error", f"Failed to enable secure token for {domainname}. The current secure token status is DISABLED")

    else:
        label_status.config(text="Please enter all information!", fg="red")

#################################################################################################
def secureTokenOff_button():
    """Disable secure token."""
    domainname = entry_domain_name.get()  # Store domain name in variable
    domainpassword = entry_domain_password.get()  # Store domain password in variable
    sudo_password = entry_sudo_password.get() # Store sudo password in variable

    log(f"***Start -secureTokenOff process***")
    log("Checking sudo permission")
    
    if sudo_password and domainname and domainpassword:

        # Check sudo password before proceeding
        if not check_sudo_password():
            return  # If sudo password is incorrect, stop the secure token disable process
        
        log(f"Checking the current secure token status of {domainname}")

        # Check Secure Token status
        check_cmd = ["sysadminctl", "-secureTokenStatus", domainname]
        check_result = subprocess.run(check_cmd, capture_output=True, text=True)

        # Log the result
        log(check_result.stdout)  # Log STDOUT result
        log(check_result.stderr)   # Log STDERR result (if any)

        # If the status returned contains "ENABLED", process disable the secure token
        if "ENABLED" in check_result.stderr:
                
            log(f"Starting to disable the secure token for account {domainname}.")
            #######################################################

            # check_sudo_password()

            # Check access rights
            subprocess.run(['sudo', '-k'], check=True)  # Reset sudo cache
            subprocess.run(['sudo', '-S', '-p', '', 'true'], input=f"{sudo_password}\n", text=True, check=True)

            log(f"Running command -secureTokenOff for {domainname}")

            # Run the command to disable Secure Token
            subprocess.run(["sudo", "sysadminctl", "-secureTokenOff", domainname, "-password", domainpassword, "-adminUser", username, "-adminPassword", sudo_password], check=True)
                                    
            # Run the command to disable Secure Token
            # cmd = ["sudo", "sysadminctl", "-secureTokenOff", domainname, "-password", domainpassword, "-adminUser", username, "-adminPassword", sudo_password]
            # result = subprocess.run(cmd, capture_output=True, text=True)
            
            # log(result.stdout)  # Log STDOUT result
            # log(result.stderr)   # Log STDERR result (if any)

            #######################################################
            log(f"Finished disable secureToken for {domainname}")

            log(f"Checking the secure token status of {domainname}")
            
            # Check Secure Token status
            check_cmd = ["sysadminctl", "-secureTokenStatus", domainname]
            check_result = subprocess.run(check_cmd, capture_output=True, text=True)

            # Log the result
            log(check_result.stdout)  # Log STDOUT result
            log(check_result.stderr)   # Log STDERR result (if any)

            # If the status returned contains "ENABLED", report an error
            if "DISABLED" in check_result.stderr:
                log(check_result.stdout)  # Log STDOUT result
                log(check_result.stderr)   # Log STDERR result (if any)
                log(f"Successfully DISABLED secure token for {domainname}.")
                messagebox.showinfo("Success!", f"Successfully DISABLED secure token for {domainname}.")
                # secureTokenOn(domainname, domainpassword, sudo_password, username)  # Proceed to secureTokenOn function

            elif "Incorrect password" in check_result.stderr:
                log(check_result.stdout)  # Log STDOUT result
                log(check_result.stderr)   # Log STDERR result (if any)
                log(f"Incorrect password for {domainname}. Please check your password.")
                messagebox.showerror("Error!", f"Incorrect password for {domainname}. Please check your password.")

            elif "Operation is not permitted without secure token unlock" in check_result.stderr:
                log(check_result.stdout)  # Log STDOUT result
                log(check_result.stderr)   # Log STDERR result (if any)
                log("Operation is not permitted without secure token unlock")
                messagebox.showerror("Error!", f"Failed to disable secure token for {domainname}. Please check your password.")

            elif "ENABLED" in check_result.stderr:
                log(check_result.stdout)  # Log STDOUT result
                log(check_result.stderr)   # Log STDERR result (if any)
                log(f"Failed to disable secure token for {domainname}.")
                messagebox.showerror("Error!", f"Failed to disable secure token for {domainname}.")

        else:
            log(check_result.stdout)  # Log STDOUT result
            log(check_result.stderr)   # Log STDERR result (if any)
            log(f"Failed to disable secure token for {domainname}. The current secure token status is ENABLED")
            messagebox.showerror("Error!", f"Failed to disable secure token for {domainname}.")

    else:
        label_status.config(text="Please enter all information!", fg="red")
        # messagebox.showerror("Error!", "Please enter all information!")


def secureTokenOn_button():
    """Enable secure token."""
    domainname = entry_domain_name.get()  # Store domain name in variable
    domainpassword = entry_domain_password.get()  # Store domain password in variable
    sudo_password = entry_sudo_password.get() # Store sudo password in variable

    log(f"***Start -secureTokenOn process***")
    log("Checking sudo permission")
    
    if sudo_password and domainname and domainpassword:

        # Check sudo password before proceeding
        if not check_sudo_password():
            return  # If sudo password is incorrect, stop the secure token activation process
        
        log(f"Checking the current secure token status of {domainname}")

        # Check Secure Token status
        check_cmd = ["sysadminctl", "-secureTokenStatus", domainname]
        check_result = subprocess.run(check_cmd, capture_output=True, text=True)

        # Log the result
        log(check_result.stdout)  # Log STDOUT result
        log(check_result.stderr)   # Log STDERR result (if any)

        # If the status returned contains "ENABLED", process disable the secure token
        if "DISABLED" in check_result.stderr:

            log(f"Starting to enable the secure token for account {domainname}.")
                
            #######################################################

            # Check access rights
            subprocess.run(['sudo', '-k'], check=True)  # Reset sudo cache
            subprocess.run(['sudo', '-S', '-p', '', 'true'], input=f"{sudo_password}\n", text=True, check=True)

            log(f"Running command -secureTokenOn for {domainname}")

            # Run the command to enable Secure Token
            subprocess.run(["sudo", "sysadminctl", "-secureTokenOn", domainname, "-password", domainpassword, "-adminUser", username, "-adminPassword", sudo_password], check=True)
                                    
            # # Run the command to enable Secure Token
            # cmd = ["sudo", "sysadminctl", "-secureTokenOn", domainname, "-password", domainpassword, "-adminUser", username, "-adminPassword", sudo_password]
            # result = subprocess.run(cmd, capture_output=True, text=True)
            # log(result.stdout)  # Log STDOUT result
            # log(result.stderr)   # Log STDERR result (if any)

            #######################################################

            log(f"Finished enable secureToken for {domainname}")
        
            log(f"Checking the secure token status of {domainname}")

            # Check Secure Token status
            check_cmd = ["sysadminctl", "-secureTokenStatus", domainname]
            check_result = subprocess.run(check_cmd, capture_output=True, text=True)

            # Log the result
            log(check_result.stdout)  # Log STDOUT result
            log(check_result.stderr)   # Log STDERR result (if any)

            # If the status returns "DISABLE", report an error
            if "ENABLED" in check_result.stderr:
                log(check_result.stdout)  # Log STDOUT result
                log(check_result.stderr)   # Log STDERR result (if any)
                log(f"Successfully ENABLED secure token for {domainname}. ")
                messagebox.showinfo("Success", f"Successfully ENABLED secure token for {domainname}!")

            elif "Incorrect password" in check_result.stderr:
                log(check_result.stdout)  # Log STDOUT result
                log(check_result.stderr)   # Log STDERR result (if any)
                log(f"Incorrect password for {domainname}.")
                messagebox.showerror("Error", f"Incorrect password for {domainname}.")

            elif "Operation is not permitted without secure token unlock" in check_result.stderr:
                log(check_result.stdout)  # Log STDOUT result
                log(check_result.stderr)   # Log STDERR result (if any)
                log("Operation is not permitted without secure token unlock.")
                messagebox.showerror("Error!", f"Failed to disable secure token for {domainname}. Please check your new email password.")

            elif "DISABLED" in check_result.stderr:
                log(check_result.stdout)  # Log STDOUT result
                log(check_result.stderr)   # Log STDERR result (if any)
                log(f"Failed to enable secure token for {domainname}.")
                messagebox.showerror("Error", f"Failed to enable secure token for {domainname}.")

        else: 
            log(check_result.stdout)  # Log STDOUT result
            log(check_result.stderr)   # Log STDERR result (if any)
            log(f"Failed to enable secure token for {domainname}. The current secure token status is DISABLED")
            messagebox.showerror("Error", f"Failed to enable secure token for {domainname}.")

    else:
        label_status.config(text="Please enter all information!", fg="red")
        # messagebox.showerror("Error!", "Please enter all information!")

# Hàm check securetoken status
def check_secureToken_status():
    """Kiểm tra trạng thái secure token hiện tại"""
    domainname = entry_domain_name.get()

    if domainname:

        log(f"Checking the current secure token status of {domainname}")

        # Check Secure Token status
        check_cmd = ["sysadminctl", "-secureTokenStatus", domainname]
        check_result = subprocess.run(check_cmd, capture_output=True, text=True)

        # Log the result
        log(check_result.stdout)  # Log STDOUT result
        log(check_result.stderr)   # Log STDERR result (if any)

        if "DISABLED" in check_result.stderr:
            log(check_result.stdout)  # Log STDOUT result
            log(check_result.stderr)   # Log STDERR result (if any)
            log(f"Secure token is DISABLED for user {domainname}.")
            messagebox.showinfo("Success!", f"Secure token is DISABLED for user {domainname}")

        elif "ENABLED" in check_result.stderr:
            log(check_result.stdout)  # Log STDOUT result
            log(check_result.stderr)   # Log STDERR result (if any)
            log(f"Secure token is ENABLED for user {domainname}. ")
            messagebox.showinfo("Success", f"Secure token is ENABLED for user {domainname}")

        elif "Incorrect password" in check_result.stderr:
            log(check_result.stdout)  # Log STDOUT result
            log(check_result.stderr)   # Log STDERR result (if any)
            log(f"Incorrect password for {domainname}. Please check your password.")
            messagebox.showerror("Error!", f"Incorrect password for {domainname}. Please check your password.")

        elif "Unknown user" in check_result.stderr:
            log(check_result.stdout)  # Log STDOUT result
            log(check_result.stderr)   # Log STDERR result (if any)
            log(f"Unknown user {domainname}. Please check user account information.")
            messagebox.showerror("Error!", f"Unknown user {domainname}. Please check user account information.")

    else:
        label_status.config(text="Please enter all information!", fg="red")

#################################################################################################
# Hàm kiểm tra kết nối Active Directory
def check_ad_connection(attempts=0):
    """Kiểm tra kết nối Active Directory."""
    command = ["dscl", "localhost", "-read", "/Active Directory/KMS"]    
    result = subprocess.run(command, text=True, capture_output=True)
    log(result.stdout)
    log(result.stderr)

    # Kiểm tra các lỗi kết nối
    if "eDSUnknownNodeName" in result.stderr or "eDSCannotAccessSession" in result.stderr or "eDSUnknownNodeName" in result.stdout or "eDSCannotAccessSession" in result.stdout:
        log(f"Error: Unable to connect to the KMS network. {result.stderr}")
        
        # Hiển thị thông báo lỗi cho người dùng
        if attempts < 5:
            retry = messagebox.askretrycancel("Connection Error", "Unable to connect to the KMS network. Please check the VPN connection!")
            if retry:
                check_ad_connection(attempts + 1)  # Tăng số lần thử và gọi lại hàm
            else:
                log("User canceled the operation due to connection failure")
                exit_program()
        else:
            messagebox.showerror("Max Attempts Reached", "Failed to connect after 5 attempts.")
            exit_program()
    elif "PrimaryNTDomain: KMS" in result.stdout or result.stderr:
        log("Successfully connected to KMS's network.")
        messagebox.showinfo("Successfully", "Successfully connected to KMS's network!")
        secureTokenOff(domainname, domainpassword, sudo_password, username)  # Disable secure token sau khi kết nối thành công

# Hàm xử lý sự kiện khi nhấn nút Check Network
def check_ad_connection_button(attempts=0):
    """Kiểm tra kết nối Active Directory."""
    command = ["dscl", "localhost", "-read", "/Active Directory/KMS"]    
    result = subprocess.run(command, text=True, capture_output=True)

    # Kiểm tra các lỗi kết nối
    if "eDSUnknownNodeName" in result.stderr or "eDSCannotAccessSession" in result.stderr or "eDSUnknownNodeName" in result.stdout or "eDSCannotAccessSession" in result.stdout:
        log(f"Error: Unable to connect to the KMS network. {result.stderr}")
        
        # Hiển thị thông báo lỗi cho người dùng
        if attempts < 5:
            retry = messagebox.askretrycancel("Connection Error", "Unable to connect to the KMS network. Please check the VPN connection!")
            if retry:
                check_ad_connection_button(attempts + 1)  # Tăng số lần thử và gọi lại hàm
            else:
                log("User canceled the operation due to connection failure")
                exit_program()
        else:
            messagebox.showerror("Max Attempts Reached", "Failed to connect after 5 attempts.")
            exit_program()
    elif "PrimaryNTDomain: KMS" in result.stdout or result.stderr:
        log("Successfully connected to KMS's network.")
        messagebox.showinfo("Successfully", "Successfully connected to KMS's network!")
        # Quay lại màn hình nhập liệu

# Hàm xử lý sự kiện khi nhấn nút Check Network
def on_check_network():
    check_ad_connection_button(attempts=0)

def exit_program():
    """Close the application."""
    root.quit()

###########################################################################################

# Setup the interface
root = tk.Tk()
root.title("Synchronize Password - Only For IT Version")
#root.geometry("520x250")  # Kích thước mới: 600 pixel chiều rộng và 400 pixel chiều cao

# Enter Domain name
label_domain_name = tk.Label(root, text="User's KMS Account:")
label_domain_name.grid(row=0, column=0, padx=10, pady=15, sticky='w')  #'w' để căn trái
entry_domain_name = tk.Entry(root)
entry_domain_name.grid(row=0, column=1, columnspan=2, padx=5, pady=5)  #Padding 5 pixel ngang và 10 pixel dọc

# Enter Domain password
label_domain_password = tk.Label(root, text="User's New Password:")
label_domain_password.grid(row=1, column=0, padx=10, pady=5, sticky='w')  # Set position
entry_domain_password = tk.Entry(root, show='*')
entry_domain_password.grid(row=1, column=1, columnspan=2, padx=5, pady=5)  # Set position

# Enter sudo password
label_sudo_password = tk.Label(root, text="Local Admin (IT) Password:")
label_sudo_password.grid(row=2, column=0, padx=10, pady=5, sticky='w')  # Set position
entry_sudo_password = tk.Entry(root, show='*')
entry_sudo_password.grid(row=2, column=1, columnspan=2, padx=5, pady=5)  # Set position

# Check Network button
btn_check_network = tk.Button(root, text="Check Network", command=on_check_network)
btn_check_network.grid(row=3, column=0, columnspan=1, padx=10, pady=10)  # Bên trái

# Check Secure Token Status button
btn_check_network = tk.Button(root, text="Check Token Status", command=check_secureToken_status)
# btn_check_network.grid(row=4, column=0, padx=10, pady=10)  # Bên trái
btn_check_network.grid(row=3, column=1, padx=10,pady=10)  # Bên phải

# SecureToken Off button
btn_check_network = tk.Button(root, text="SecureToken Off", command=secureTokenOff_button)
btn_check_network.grid(row=4, column=0, padx=10, pady=10)  # Bên trái

# SecureToken On button
btn_create = tk.Button(root, text="SecureToken On", command=secureTokenOn_button)
btn_create.grid(row=4, column=1,padx=10,pady=10)  # Bên phải

# SecureToken Off/On process button
btn_create = tk.Button(root, text="Sync Password", command=check_ad_connection)
# btn_create.grid(row=3, column=1,padx=10,pady=10)  # Bên phải
btn_create.grid(row=4, column=2, columnspan=1, padx=10,pady=10)  # Bên phải

# Status label
label_status = tk.Label(root, text="")
label_status.grid(row=5, column=0, columnspan=2)  # Center the status label

# Run the interface
root.mainloop()