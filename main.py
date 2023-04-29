import datetime
import time
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import tkinter as tk
import os
from tkinter import messagebox
from tkinter import simpledialog
import webbrowser
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define your Google Sheets credentials and sheet information
SERVICE_ACCOUNT_FILE = 'D:/online-attendance-system/access-authenticator-385111-93691effbea6.json'
SPREADSHEET_ID = '1CDykRNnzaveg5wsrgHpTHgUH_uDrX2mqFt4rmi7lO2c'
ENTRY_SHEET_NAME = 'Entry Log'
EXIT_SHEET_NAME = 'Exit Log'
DATA_SHEET_NAME = 'Data'

# Authorize with the Google Sheets API
scope = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
client = gspread.authorize(creds)
entry_sheet = client.open_by_key(SPREADSHEET_ID).worksheet(ENTRY_SHEET_NAME)
exit_sheet = client.open_by_key(SPREADSHEET_ID).worksheet(EXIT_SHEET_NAME)
data_sheet = client.open_by_key(SPREADSHEET_ID).worksheet(DATA_SHEET_NAME)

# Load the authorized users from a file
with open('./authorized.txt', 'r') as f:
    authorized_users = [l[:-1] for l in f.readlines()]
    f.close()

log_path = './log.csv'

most_recent_access = {}

time_between_logs = 5

cap = cv2.VideoCapture(0)

# Display the popup message
def popup_message():
    popup = tk.Tk()
    popup.title("Access Denied")
    popup.geometry("200x100")
    label = tk.Label(popup, text="Access Denied")
    label.pack(side="top", fill="x", pady=10)
    button = tk.Button(popup, text="Close", command=popup.destroy)
    button.pack()
    popup.mainloop()

last_qrcode_data = None

# Display entry or exit successful message
def display_message(action):
    global last_qrcode_data
    if data != last_qrcode_data:
        # Create a new message box window
        msg_box = tk.Toplevel()
        msg_box.title("Message")
        msg_box.geometry("200x100")

        # Add a label to the message box window
        label = tk.Label(msg_box, text=action)
        label.pack(side="top", fill="x", pady=35)

        # Schedule a function call to close the message box window after 2 seconds
        msg_box.after(2000, lambda: msg_box.destroy())

        last_qrcode_data = data

# Define the on entry function
def on_entry(qr_info):
    data = qr_info[0].data.decode()
    if data in authorized_users:
        update_log("entry")
        display_message("Entry Successful")
        update_sheet(data, "Entry")
    else:
        print("Access Denied")

# Define the on exit function
def on_exit(qr_info):
    data = qr_info[0].data.decode()
    if data in authorized_users:
        update_log("exit")
        display_message("Exit Successful")
        update_sheet(data, "Exit")
    else:
        print("Access Denied")

# Update the log
def update_log(action):
    data = qr_info[0].data.decode()
    if data not in most_recent_access.keys() \
            or time.time() - most_recent_access[data] > time_between_logs:
        most_recent_access[data] = time.time()

        with open(log_path, "a") as f:
            f.write("{},{},{}\n".format(data, datetime.datetime.now(), action))
            f.close()

# Send data to sheet
def update_sheet(data, action):
    # Get the current time in the correct format
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    # Check if the action is Entry or Exit and append the data to the respective sheet
    if action == 'Entry':
        entry_sheet.append_row([data, current_date, current_time, action])
    elif action == 'Exit':
        exit_sheet.append_row([data, current_date, current_time, action])

# Send roll numbers data to sheet
def send_roll_numbers_to_sheet():
    data_sheet = client.open_by_key(SPREADSHEET_ID).worksheet(DATA_SHEET_NAME)

    # Read the roll numbers from file
    with open('authorized.txt', 'r') as f:
        roll_numbers = set(f.read().splitlines())

    # Remove duplicate roll numbers from file
    unique_roll_numbers = list(set(roll_numbers))

    # Get existing roll numbers from the sheet
    existing_roll_numbers = set(data_sheet.col_values(1)[1:])

    # Append only unique roll numbers to the sheet
    for roll_number in unique_roll_numbers:
        if roll_number not in existing_roll_numbers:
            data_sheet.append_row([roll_number])

# Create a global variable to keep track of unauthorized people
unauthorized_images_count = 0

# Open data log link
def open_data_log():
        password = simpledialog.askstring("Password", "Enter the Password:", show="*")
        if password == "SNMD":
            webbrowser.open("https://docs.google.com/spreadsheets/d/1CDykRNnzaveg5wsrgHpTHgUH_uDrX2mqFt4rmi7lO2c")
            return
        else:
            messagebox.showerror("Incorrect Password", "Sorry, the password is incorrect.")

# Set up the GUI window and buttons
root = tk.Tk()
root.title("Actions")

# Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set window size and position
window_width = int(screen_width / 2)
window_height = screen_height
window_position_x = int(screen_width / 2)
window_position_y = 0
root.geometry(f"{window_width}x{window_height}+{window_position_x}+{window_position_y}")

# Create a new window for the admin access
admin_window = tk.Toplevel(root)
admin_window.title("Admin Panel")
admin_window.geometry(f"{window_width}x{window_height}+{window_position_x}+{window_position_y}")
# Hide the window initially until correct password is entered for admin access
admin_window.withdraw()

# Function to show the admin access
def open_admin():
    attempts = 0
    while attempts < 3:
        password = simpledialog.askstring("Password", "Enter the Password:", show="*")
        if password == "admin":
            admin_window.deiconify()
            root.withdraw()
            break
        else:
            attempts += 1
            messagebox.showerror("Incorrect Password", f"Sorry, the password is incorrect. You have {3 - attempts} attempts left.")

    if attempts == 3:
        messagebox.showerror("Too Many Attempts", "You have entered an incorrect password more than three times. Your photo will be taken and stored.")

    # Capture the image for unauthorized access
    ret, frame = cap.read()
    if ret and frame is not None:
        # Create a folder if it doesn't exist
        if not os.path.exists("captured_images"):
            os.makedirs("captured_images")
        # Save the image in the folder
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"captured_images/unauthorized_{timestamp}.png"
        cv2.imwrite(filename, frame)

# Function to register new roll number in admin access
def register_roll_number():
    roll_number = simpledialog.askstring("Register Roll Number", "Enter the Roll Number:")
    if roll_number:
        # Read the content of the authorized.txt file
        with open('authorized.txt', 'r') as file:
            content = file.readlines()

        # Check if the roll number is already present in the file
        if roll_number + '\n' in content:
            messagebox.showerror("Roll Number Already Registered", f"The roll number {roll_number} is already registered.")
        else:
            # Add the roll number to the file if it's unique
            with open("authorized.txt", "a") as f:
                f.write(f"{roll_number}\n")
            messagebox.showinfo("Roll Number Registered", f"The roll number {roll_number} has been registered successfully.")
            send_roll_numbers_to_sheet()

# Function to delete roll number from file
def delete_roll_number():
    # Create a dialog box to ask for the roll number to be deleted
    roll_number = simpledialog.askstring("Delete Roll Number", "Enter the Roll Number:")

    if roll_number is not None:
        # Read the content of the authorized.txt file
        with open('authorized.txt', 'r') as file:
            content = file.readlines()

        # Remove the roll number from the content
        try:
            content.remove(roll_number + '\n')
        except ValueError:
            messagebox.showerror("Roll Number Not Found", f"The Roll Number {roll_number} was not found.")
            return

        # Remove the blank lines if any
        content = list(filter(lambda x: x.strip(), content))

        # Write the modified content back to the authorized.txt file
        with open('authorized.txt', 'w') as file:
            file.writelines(content)
        messagebox.showinfo("Roll Number Deleted", f"The Roll Number {roll_number} has been deleted successfully.")
        
entry_button = tk.Button(root, text="ENTRY", width=50, height=10, state="disabled", bg="white")
exit_button = tk.Button(root, text="EXIT", width=50, height=10, state="disabled", bg="white")
admin_button = tk.Button(root, text="ADMIN", width=50, height=10, bg="white", command=open_admin)

entry_button.grid(row=0, column=0, padx=140, pady=35)
exit_button.grid(row=1, column=0, padx=140, pady=10)
admin_button.grid(row=3, column=0, padx=140, pady=30)

# Function to go back to user mode
def go_back_to_user_mode():
    admin_window.withdraw()
    root.deiconify()

# Add a back button to the admin window
back_button = tk.Button(admin_window, text="BACK", width=50, height=10, bg="white", command=go_back_to_user_mode)
back_button.pack()

# Add a button to the admin access to open the data log
data_log_button_admin = tk.Button(admin_window, text="DATA LOG", width=50, height=10, bg="white", command=open_data_log)
data_log_button_admin.pack()

# Add a button to the admin access to register new roll number
register_button_admin = tk.Button(admin_window, text="REGISTER ROLL NUMBER", width=50, height=10, bg="white", command=register_roll_number)
register_button_admin.pack()

# Add a button to the admin access to delete a roll number
delete_roll_button = tk.Button(admin_window, text="DELETE ROLL NUMBER", width=50, height=10, bg="white", command=delete_roll_number)
delete_roll_button.pack()

# Check the last log
def check_last_log(data, action):
    last_log = ''
    with open(log_path, 'r') as f:
        lines = f.readlines()
        for line in reversed(lines):
            if line.startswith(data):
                last_log = line
                break
        f.close()

    if last_log and last_log.endswith(action + '\n'):
        return True
    else:
        return False

# Start the main loop
unauthorized_images_count = 0
while True:
    ret, frame = cap.read()
    
    if ret and frame is not None:
        for barcode in decode(frame):
            qr_info = [barcode]
            cv2.polylines(frame, [np.array(barcode.polygon)], True, (255, 0, 0), 5)

            if qr_info:
                data = qr_info[0].data.decode()

                if data in authorized_users:
                    if check_last_log(data, "entry"):
                        # messagebox.showinfo("Authorized", "Access Granted. Make your Exit.")
                        display_message("Access Granted. Make you Exit.", data)
                        entry_button.config(state=tk.DISABLED)
                        exit_button.config(state=tk.NORMAL)
                    elif check_last_log(data, "exit"):
                        # messagebox.showinfo("Authorized", "Access Granted. Make your Entry.")
                        display_message("Access Granted. Make you Entry.", data)
                        entry_button.config(state=tk.NORMAL)
                        exit_button.config(state=tk.DISABLED)
                    # Reset the unauthorized count if an authorized person is detected
                    unauthorized_images_count = 0
                else:
                    entry_button.config(state=tk.DISABLED)
                    exit_button.config(state=tk.DISABLED)
                    # messagebox.showerror("Unauthorized", "Access Denied")
                    display_message("Access Denied.", data)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    cv2.imshow('Webcam', frame)
    root.update()

    entry_button.config(command=lambda: on_entry(qr_info))
    exit_button.config(command=lambda: on_exit(qr_info))

cap.release()
cv2.destroyAllWindows()
