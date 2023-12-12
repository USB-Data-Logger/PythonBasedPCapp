import tkinter as tk
from tkinter import ttk
import serial
from datetime import datetime

# Define colors for the dark theme
dark_bg = "#2c2f33"
light_text = "#ffffff"
accent_color = "#7289da"
button_bg = "#23272a"

class SerialMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Monitor")
        self.root.geometry("800x450")  # Set main window size to a 16:9 ratio
        self.root.configure(bg=dark_bg)

        self.serial_port = None
        self.baud_rate_var = tk.StringVar(value="9600")
        self.com_port_var = tk.StringVar(value="COM7")
        self.file_suffix = tk.StringVar(value="")  # Variable to hold the user-entered suffix
        self.monitoring = False  # Flag to control the monitoring state

        self.init_ui()

    def init_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background=dark_bg, foreground=light_text)
        style.configure('TButton', background=button_bg, foreground=light_text)
        style.configure('TEntry', background=dark_bg, foreground=light_text, fieldbackground="#43454a")
        style.map('TButton', background=[('active', accent_color)], foreground=[('active', light_text)])
        
        ttk.Label(self.root, text="COM Port:").pack(pady=5)
        ttk.Combobox(self.root, textvariable=self.com_port_var, values=[f"COM{i}" for i in range(10)]).pack(pady=5)

        ttk.Label(self.root, text="Baud Rate:").pack(pady=5)
        ttk.Combobox(self.root, textvariable=self.baud_rate_var, values=["9600", "19200", "38400", "57600", "115200"]).pack(pady=5)

        ttk.Label(self.root, text="Suffix:").pack(pady=5)
        self.file_suffix_entry = ttk.Entry(self.root, textvariable=self.file_suffix)
        self.file_suffix_entry.pack(pady=5)

        self.start_stop_button = ttk.Button(self.root, text="Start Monitoring", command=self.toggle_monitoring)
        self.start_stop_button.pack(pady=10)

        self.status_label = ttk.Label(self.root, text="")
        self.status_label.pack(pady=10)

    def toggle_monitoring(self):
        if not self.monitoring:
            # Start monitoring
            self.file_name = self.get_file_name()  # Update the file name with the current date and time
            try:
                self.serial_port = serial.Serial(self.com_port_var.get(), int(self.baud_rate_var.get()), timeout=1)
                self.start_stop_button["text"] = "Stop Monitoring"
                self.monitoring = True
                self.status_label["text"] = f"Monitoring started, saving to {self.file_name}"
                self.read_serial_data()
            except serial.SerialException as e:
                self.status_label["text"] = f"Error: {e}"
        else:
            # Stop monitoring
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            self.start_stop_button["text"] = "Start Monitoring"
            self.monitoring = False
            self.status_label["text"] = "Monitoring stopped"

    def read_serial_data(self):
        if self.monitoring and self.serial_port and self.serial_port.is_open:
            data = self.serial_port.readline()
            if data:
                timestamped_data = f"{datetime.now().strftime('%Y-%m-%d,%H:%M:%S.%f')[:-3]}, {data.decode().strip()}\n"
                self.save_data_to_file(timestamped_data)
            self.root.after(100, self.read_serial_data)

    def save_data_to_file(self, data):
        with open(self.file_name, "a") as file:
            file.write(data)
            self.status_label["text"] = f"Data saved to {self.file_name}"

    def get_file_name(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
        return f"{current_time} {self.file_suffix.get()}.csv"

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialMonitor(root)
    root.mainloop()