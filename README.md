# Access Authenticator

It is an implementation of an online attendance system that uses QR codes or barcodes to track attendance. The program captures the camera feed and processes it to detect QR codes or barcodes. Once a QR code or barcode is detected, the program checks if the QR code or barcode contains authorized user information. If the user is authorized, the program logs the entry or exit and sends the data to a Google Sheet.

The program is divided into several functions, including `on_entry`, `on_exit`, `check_last_log`, `update_log`, `update_sheet`, `popup_message`, and `display_message`. These functions are used to handle different parts of the program logic, such as displaying messages, checking the last log, and updating logs.

The program uses several libraries, including `cv2` for capturing and processing the camera feed, `pyzbar` for decoding the QR codes or barcodes, `numpy` for working with arrays, `tkinter` for creating GUI elements, and `gspread` and `oauth2client` for accessing and modifying Google Sheets. The Google Sheets credentials and sheet information are defined at the beginning of the program, along with the authorized users, log path, and time between logs.

The program runs in an infinite loop, where it continuously captures the camera feed and processes it to detect QR codes or barcodes. If a QR code or barcode is detected, the program checks if the user is authorized, logs the entry or exit, sends the data to a Google Sheet, and displays a message on the GUI. The program also checks the last log to ensure that there are no duplicates.

Overall, the program provides a simple implementation of an online attendance system that can be easily extended and customized for different use cases.
