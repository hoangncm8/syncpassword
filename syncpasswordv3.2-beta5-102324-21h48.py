import tkinter as tk
import subprocess
import random
import string
import os
import sys
from tkinter import messagebox
from datetime import datetime

# Global variables to store random passwords and other important variables
random_password = ""
sudo_password = ""
domainname = ""
domainpassword = ""
username = "kmssync" #Fixed temporary account

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

def generate_random_password(length=12):
    """Create a random password with a specified length."""
    log(f"*** Starting to create a random password with a specified {length} length. ***")
    global random_password
    characters = string.ascii_letters + string.digits
    random_password = ''.join(random.choice(characters) for _ in range(length))
    log(f"Set random password with length {length} characters: {random_password}")
    return random_password

def check_sudo_password():
    """Check the current sudo password."""
    log("*** Checking the current sudo password. ***")
    command = "sudo -v"  # Command to check sudo authentication
    result, error = sudopassword_command(command)

    if error:
        log("Sudo password verification failed.")
        messagebox.showerror("Error", "Sudo password is incorrect or has expired.")
        return False  # Return False if verification fails
    else:
        log("Sudo password is correct!")
        return True  # Return True if verification is successful

def sudopassword_command(command):
    """Run command with sudo rights and return the result."""
    try:
        result = subprocess.run(['sudo', '-S'] + command.split(), input=f"{entry_sudo_password.get()}\n", text=True, capture_output=True)
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)

def call_sudopassword_input():
    sudo_password = entry_sudo_password.get() # Store sudo password in variable

    # Check access rights
    subprocess.run(['sudo', '-k'], check=True)  # Reset sudo cache
    subprocess.run(['sudo', '-S', '-p', '', 'true'], input=f"{sudo_password}\n", text=True, check=True)

def create_account():
    log(f"*** Start creating a temporary account {username} process ***")
    # username = "kmssyncpassword"  # Use fixed username
    domainname = entry_domain_name.get()  # Store domain name in variable
    domainpassword = entry_domain_password.get()  # Store domain password in variable
    sudo_password = entry_sudo_password.get()

    if sudo_password and domainname and domainpassword:
        random_password = generate_random_password()

        try:
            # # Check access rights
            # subprocess.run(['sudo', '-k'], check=True)  # Reset sudo cache
            # subprocess.run(['sudo', '-S', '-p', '', 'true'], input=f"{sudo_password}\n", text=True, check=True)
            
            call_sudopassword_input()

            # Create a new account
            log(f"Starting to create {username} account")
            subprocess.run(['sudo', 'sysadminctl', '-addUser', username, '-password', random_password, '-admin'], check=True)
            # label_status.config(text=f"Account '{username}' has been created successfully!\nPassword has been saved to {password_file_path}", fg="green")
            log(f"Account {username} has been created successfully with the random password: {random_password}")
            # messagebox.showinfo("Success",f"A temporary account {username} has been created successfully")

            # Call the check_admin_membership function after creating the account
            log(f"Checking if {username} is a member of the admin group.")
            check_admin_membership()         

        except subprocess.CalledProcessError as e:
            #label_status.config(text=f"Error: {e}", fg="red")
            messagebox.showerror("Error!", f"Incorrect KMS Account or Current Login Password.")
        except Exception as e:
            label_status.config(text=f"Undefined error: {e}", fg="red")
            messagebox.showerror("Error!", f"Undefined error: {e}")

    else:
        label_status.config(text="Please enter all information!", fg="red")
        
def check_admin_membership():
    """Check if username is in the admin group."""
    check_count = 0  # Count the number of rechecks after confirming admin status

    while True:
        # Run the dseditgroup command to check admin group membership
        log(f"*** Checking if the temporary account {username} is in the admin group. ***")

        call_sudopassword_input()

        command = ["sudo", "dseditgroup", "-o", "checkmember", "-m", username, "admin"]
        # result = sudopassword_command(command)
        result = subprocess.run(command, capture_output=True, text=True)

        if "yes" in result.stdout or result.stderr:
            log(f"The temporary account {username} is a member of the admin group now.")
            
            if check_count < 5:
                check_count += 1
                log(f"Re-checking membership status... Attempt {check_count}")
                continue  # Continue checking until 5 attempts are reached
            else:
                log("Membership confirmed after 5 re-checks.")
            # Activate secure token
                log("Activating secure token")
                activate_secure_token(domainname, domainpassword)
                break
        else:
            log(f"Warning! The temporary account {username} is NOT a member of the ADMIN group. Therefore, this process will be terminated.")
            check_count += 1  # Tăng số lần kiểm tra
            if check_count == 7:
                messagebox.showwarning("Warning", f"The temporary account {username} does not have admin rights after 7 checks. Therefore, this process will be terminated.")
                delete_user(username)

def delete_user(username):
    """Delete a user on macOS using sysadminctl."""
    try:

        call_sudopassword_input()

        # Lệnh để xóa người dùng
        cmd = ["sudo", "sysadminctl", "-deleteUser", username]
        result = subprocess.run(cmd, capture_output=True, text=True)
        log(result.stdout)  # Log STDOUT result
        log(result.stderr)   # Log STDERR result (if any)
        
        # Gọi lệnh hệ thống
        # subprocess.run(command, check=True)
        # command = ["sudo", "dseditgroup", "-o", "checkmember", "-m", username, "admin"]
        # result = sudopassword_command(command)

        cmd_del = ["sudo", "dseditgroup", "-o", "checkmember", "-m", username, "admin"]
        result_del = subprocess.run(cmd_del, capture_output=True, text=True)
        log(result_del.stdout)  # Log STDOUT result
        log(result_del.stderr)   # Log STDERR result (if any)

        if "not found" in result_del.stdout or result_del.stderr:
            log(f"The temporary account {username} has been successfully deleted.")
            # print(f"User '{username}' has been successfully deleted.")
        else:
            log(f"Error deleting the temporary account {username}. Please remove it manually.")
        
    except subprocess.CalledProcessError as e:
        log(f"Error deleting user {username}.")
        # print(f"Error deleting user '{username}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def activate_secure_token(domainname, domainpassword):
    """Activate secure token for the account."""
    # username = "syncpassword"  # Use fixed username
    domainname = entry_domain_name.get()  # Store domain name in variable
    domainpassword = entry_domain_password.get()  # Store domain password in variable
    
    log(f"*** Start process enable secure token for the temporary account {username} ***")

    call_sudopassword_input()

    # Check sudo password before continuing
    if not check_sudo_password():
        return  # If sudo password is incorrect, stop the secure token activation process
    
    log(f"*** Checking the secure token status of {username} ***")

    # Check Secure Token status
    check_cmd = ["sysadminctl", "-secureTokenStatus", username]
    check_result = subprocess.run(check_cmd, capture_output=True, text=True)

    # Log the result
    log(check_result.stderr)   # Log STDERR result (if any)

    if "DISABLED" in check_result.stderr:

        # log(f"Activating secure token: sudo sysadminctl -secureTokenOn {username} -password {random_password} -adminUser {domainname} -adminPassword {domainpassword}")
        log(f"Starting to enable the secure token for account {username}.")
        
        # Run the command to activate Secure Token
        cmd = ["sudo", "sysadminctl", "-secureTokenOn", username, "-password", random_password, "-adminUser", domainname, "-adminPassword", domainpassword]
        result = subprocess.run(cmd, capture_output=True, text=True)
        log(result.stderr)   # Log STDERR result (if any)
        log(f"Finished enable secureToken for {username}")

        # # Check if the Secure Token activation was successful
        # if result.returncode != 0:
        #     log(f"Error enabling secure token: {result.returncode}")
        #     messagebox.showerror("Error", "Failed to enable secure token.")
        #     return

        log(f"Checking the secure token status of {username}")
        
        # Check Secure Token status
        check_cmd = ["sudo", "sysadminctl", "-secureTokenStatus", username]
        check_result = subprocess.run(check_cmd, capture_output=True, text=True)

        # Log the result
        log(check_result.stderr)   # Log STDERR result (if any)

        # If the status returns "DISABLE", report an error
        if "ENABLED" in check_result.stderr:
            log(f"Secure token ENABLED successfully for {username}.")
            log(check_result.stderr)   # Log STDERR result (if any)
            # messagebox.showinfo("Success", f"Secure token ENABLED successfully for {username}!")
            # check_network()
            secureTokenOff(domainname, domainpassword, random_password)

        elif "Incorrect password" in check_result.stderr:
            log(f"Incorrect password for {domainname}")
            log(check_result.stderr)   # Log STDERR result (if any)
            messagebox.showerror("Error", f"Incorrect password for {domainname}.")
            delete_user(username)

        elif "Operation is not permitted without secure token unlock" in check_result.stderr:
            log("Operation is not permitted without secure token unlock.")
            log(check_result.stderr)   # Log STDERR result (if any)
            messagebox.showerror("Error!", "Error! Please check your new email password.")
            delete_user(username)

        else: 
            log(f"Failed to enable secure token for {username}.")
            log(check_result.stderr)   # Log STDERR result (if any)
            messagebox.showerror("Error", f"Failed to enable secure token for {username}.")
            delete_user(username)

    else:
            log(f"Unable to proceed with the process to enable the secure token for {username} because the current secure token is DISABLED.")
            log(check_result.stderr)   # Log STDERR result (if any)
            messagebox.showerror("Error", f"Unable to proceed with the process to enable the secure token for {username} because the current secure token is DISABLED.")
            delete_user(username)

#################################################################################################
def check_securetoken_status():
    """Kiểm tra trạng thái secure token hiện tại"""
    domainname = entry_domain_name.get()

    log(f"Checking the current secure token status of {domainname}")

    # Check Secure Token status
    check_cmd = ["sysadminctl", "-secureTokenStatus", domainname]
    check_result = subprocess.run(check_cmd, capture_output=True, text=True)

    # Log the result
    log(check_result.stderr)   # Log STDERR result (if any)

    return check_result.stderr

    # if "DISABLED" in check_result.stderr:
    #     log(check_result.stderr)   # Log STDERR result (if any)
    #     log(f"Secure token is DISABLED for user {domainname}.")
    #     # messagebox.showinfo("Success!", f"Secure token is DISABLED for user {domainname}")

    # elif "ENABLED" in check_result.stderr:
    #     log(check_result.stderr)   # Log STDERR result (if any)
    #     log(f"Secure token is ENABLED for user {domainname}. ")
    #     # messagebox.showinfo("Success", f"Secure token is ENABLED for user {domainname}")

    # if "Incorrect password" in check_result.stderr:
    #     log(check_result.stderr)   # Log STDERR result (if any)
    #     log(f"Incorrect password for {domainname}. Please check your password.")
    #     messagebox.showerror("Error!", f"Incorrect password for {domainname}. Please check your password.")

    # elif "Unknown user" in check_result.stderr:
    #     log(check_result.stderr)   # Log STDERR result (if any)
    #     log(f"Unknown user {domainname}. Please check user account information.")
    #     messagebox.showerror("Error!", f"Unknown user {domainname}. Please check user account information.")

def secureTokenOff(domainname, domainpassword, random_password):
    """Disable secure token."""
    # username = "syncpassword"  # Use fixed username
    domainname = entry_domain_name.get()  # Store domain name in variable
    domainpassword = entry_domain_password.get()  # Store domain password in variable
    # messagebox.showinfo("Disable SecureToken", f"Starting to disable secure token for account {domainname}.")

    call_sudopassword_input()

    log(f"Starting to disable secure token for account {domainname}.")
    
    # Check sudo password before proceeding
    if not check_sudo_password():
        return  # If sudo password is incorrect, stop the secure token disable process
    
    log(f"Checking the secure token status of {domainname}")

    # # Check Secure Token status
    # check_cmd = ["sudo", "sysadminctl", "-secureTokenStatus", domainname]
    # check_result = subprocess.run(check_cmd, capture_output=True, text=True)

    # # Log the result
    # log(check_result.stdout)  # Log STDOUT result
    # log(check_result.stderr)   # Log STDERR result (if any)

    # # If the status returned contains "ENABLED", process disable the secure token
    # if "ENABLED" in check_result.stderr:

    result = check_securetoken_status()

    if "ENABLED" in result:

        log(f"Starting to disable the secure token for account {domainname}.")

        # Run the command to disable Secure Token
        cmd = ["sudo", "sysadminctl", "-secureTokenOff", domainname, "-password", domainpassword, "-adminUser", username, "-adminPassword", random_password]
        result = subprocess.run(cmd, capture_output=True, text=True)
        log(result.stdout)  # Log STDOUT result
        log(result.stderr)   # Log STDERR result (if any)

        log(f"Finished disable secureToken for {domainname}")
        
        # log(f"Checking the secure token status of {domainname}")
        
        # # Check Secure Token status
        # check_cmd = ["sudo", "sysadminctl", "-secureTokenStatus", domainname]
        # check_result = subprocess.run(check_cmd, capture_output=True, text=True)

        # # Log the result
        # log(check_result.stderr)   # Log STDERR result (if any)

        result = check_securetoken_status()
        
        # If the status returned contains "ENABLED", report an error
        # if "DISABLED" in check_result.stderr:
        if "DISABLED" in result:
           
            # log(check_result.stderr)   # Log STDERR result (if any)

            log(f"Successfully DISABLED secure token for {domainname}.")
            # messagebox.showinfo("Success!", f"Successfully DISABLED secure token for {domainname}.")
            secureTokenOn(domainname, domainpassword, random_password)  # Proceed to secureTokenOn function

        # elif "Incorrect password" in check_result.stderr:
        elif "Incorrect password" in result:

            # log(check_result.stderr)   # Log STDERR result (if any)
            log(f"Incorrect password for {domainname}. Please check your password.")
            messagebox.showerror("Error!", f"Incorrect password for {domainname}. Please check your password.")
            delete_user(username)

        # elif "Operation is not permitted without secure token unlock" in check_result.stderr:
        elif "Operation is not permitted without secure token unlock" in result:
    
            # log(check_result.stderr)   # Log STDERR result (if any)
            log("Operation is not permitted without secure token unlock")
            messagebox.showerror("Error!", f"Failed to disable secure token for {domainname}. Please check your password.")
            delete_user(username)

        # elif "ENABLED" in check_result.stderr:
        elif "ENABLED" in result:
           
            # log(check_result.stderr)   # Log STDERR result (if any)
            log(f"Failed to disable secure token for {domainname}.")
            messagebox.showerror("Error!", f"Failed to disable secure token for {domainname}.")
            delete_user(username)

    else:
        # log(check_result.stderr)   # Log STDERR result (if any)
        log(f"Failed to disable secure token for {domainname}. The current secure token status is ENABLED")
        messagebox.showerror("Error!", f"Failed to disable secure token for {domainname}. The current secure token status is ENABLED")
        delete_user(username)
        
#################################################################################################
def secureTokenOn(domainname, domainpassword, random_password):
    """Enable secure token."""
    # username = "syncpassword"  # Use fixed username
    domainname = entry_domain_name.get()  # Store domain name in variable
    domainpassword = entry_domain_password.get()  # Store domain password in variable
    # messagebox.showinfo("Enable SecureToken", f"Starting to enable secure token for account {domainname}")
    log(f"Starting to enable secure token for account {domainname}")
    
    call_sudopassword_input()

    # Check sudo password before proceeding
    if not check_sudo_password():
        return  # If sudo password is incorrect, stop the secure token activation process
    
    log(f"Checking the secure token status of {domainname}")

    # # Check Secure Token status
    # check_cmd = ["sudo", "sysadminctl", "-secureTokenStatus", domainname]
    # check_result = subprocess.run(check_cmd, capture_output=True, text=True)

    # # Log the result
    # log(check_result.stdout)  # Log STDOUT result
    # log(check_result.stderr)   # Log STDERR result (if any)

    # check_securetoken_status()

    result = check_securetoken_status()

    # If the status returned contains "ENABLED", process disable the secure token

    # if "DISABLED" in check_result.stderr:
    if "DISABLED" in result:

        log(f"Starting to enable the secure token for account {domainname}.")

        # Run the command to enable Secure Token
        cmd = ["sudo", "sysadminctl", "-secureTokenOn", domainname, "-password", domainpassword, "-adminUser", username, "-adminPassword", random_password]
        result = subprocess.run(cmd, capture_output=True, text=True)
        log(result.stderr)   # Log STDERR result (if any)
        log(f"Finished enable secureToken for {domainname}")

        # # Check if the Secure Token activation was successful
        # if result.returncode != 0:
        #     log(f"Error enabling secure token: {result.returncode}")
        #     messagebox.showerror("Error", "Failed to enable secure token.")
        #     return
        
        log(f"Checking the secure token status of {domainname}")

        # # Check Secure Token status
        # check_cmd = ["sudo", "sysadminctl", "-secureTokenStatus", domainname]
        # check_result = subprocess.run(check_cmd, capture_output=True, text=True)

        # # Log the result
        # log(check_result.stderr)   # Log STDERR result (if any)

        result = check_securetoken_status()

        # If the status returns "DISABLE", report an error
        # if "ENABLED" in check_result.stderr:
        if "ENABLED" in result:
            # log(check_result.stderr)   # Log STDERR result (if any)
            log(f"Successfully ENABLED secure token for {domainname}. ")
            messagebox.showinfo("Success", f"Successfully ENABLED secure token for {domainname}!")
            log("Deleting the temporary account kmssync")
            delete_user(username)

        # elif "Incorrect password" in check_result.stderr:
        elif "Incorrect password" in result:
            # log(check_result.stderr)   # Log STDERR result (if any)
            log(f"Incorrect password for {domainname}.")
            messagebox.showerror("Error", f"Incorrect password for {domainname}.")
            delete_user(username)

        # elif "Operation is not permitted without secure token unlock" in check_result.stderr:
        elif "Operation is not permitted without secure token unlock" in result:
            # log(check_result.stderr)   # Log STDERR result (if any)
            log("Operation is not permitted without secure token unlock.")
            messagebox.showerror("Error!", f"Failed to disable secure token for {domainname}. Please check your new email password.")
            delete_user(username)

        # elif "DISABLED" in check_result.stderr:
        elif "DISABLED" in result:
            # log(check_result.stderr)   # Log STDERR result (if any)
            log(f"Failed to enable secure token for {domainname}.")
            messagebox.showerror("Error", f"Failed to enable secure token for {domainname}.")
            delete_user(username)

    else: 
        # log(check_result.stderr)   # Log STDERR result (if any)
        log(f"Failed to enable secure token for {domainname}. The current secure token status is DISABLED")
        messagebox.showerror("Error", f"Failed to enable secure token for {domainname}. The current secure token status is DISABLED")
        delete_user(username)

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
                delete_user(username)
                exit_program()
        else:
            messagebox.showerror("Max Attempts Reached", "Failed to connect after 5 attempts.")
            exit_program()

    elif "PrimaryNTDomain: KMS" in result.stdout or result.stderr:
        log("Successfully connected to KMS's network.")
        # messagebox.showinfo("Successfully", "Successfully connected to KMS's network!")
        # secureTokenOff(domainname, domainpassword, random_password)  # Disable secure token sau khi kết nối thành công
        # create_account()

        result = check_securetoken_status()

        if "ENABLED" in result:
            create_account()

        else:
            log(f"Secure token is DISABLED for user {domainname}.")
            messagebox.showerror("Error!", f"The current secure token status of {domainname} is DISABLED. Please contact the IT team for assistance!")
            exit_program()

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

# Hàm xử lý sự kiện khi nhấn nút Check Network
def on_check_network():
    check_ad_connection_button(attempts=0)

def check_network():
    check_ad_connection(attempts=0)

def exit_program():
    """Close the application."""
    root.quit()

###########################################################################################

# Setup the interface
root = tk.Tk()
root.title("Synchronize Password")
root.geometry("400x220")  # Kích thước mới: 600 pixel chiều rộng và 400 pixel chiều cao

# Enter Domain name
label_domain_name = tk.Label(root, text="KMS Account:")
label_domain_name.grid(row=0, column=0, padx=10, pady=15, sticky='w')  #'w' để căn trái
entry_domain_name = tk.Entry(root)
entry_domain_name.grid(row=0, column=1, padx=5, pady=5)  #Padding 5 pixel ngang và 10 pixel dọc

# Enter Domain password
label_domain_password = tk.Label(root, text="New Email Password:")
label_domain_password.grid(row=1, column=0, padx=10, pady=5, sticky='w')  # Set position
entry_domain_password = tk.Entry(root, show='*')
entry_domain_password.grid(row=1, column=1, padx=5, pady=5)  # Set position

# Enter sudo password
label_sudo_password = tk.Label(root, text="Old Email Password or    \nCurrent Login Password:")
label_sudo_password.grid(row=2, column=0, padx=10, pady=5, sticky='w')  # Set position
entry_sudo_password = tk.Entry(root, show='*')
entry_sudo_password.grid(row=2, column=1, padx=5, pady=5)  # Set position

# Check Network button
btn_check_network = tk.Button(root, text="Check Network", command=on_check_network)
btn_check_network.grid(row=3, column=0, padx=10, pady=10)  # Bên trái

# Create account button
btn_create = tk.Button(root, text="Sync Password", command=check_network)
btn_create.grid(row=3, column=1,padx=10,pady=10)  # Bên phải

# Status label
label_status = tk.Label(root, text="")
label_status.grid(row=4, column=0, columnspan=2)  # Center the status label

# Run the interface
root.mainloop()