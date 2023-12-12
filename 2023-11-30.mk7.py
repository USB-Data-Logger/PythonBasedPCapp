import tkinter as tk
import tkinter.simpledialog
from tkinter import filedialog
import serial
import time
import csv
from datetime import datetime

class SerialMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Monitor")

        self.serial_port = None
        self.baud_rate_var = tk.StringVar(root)
        self.com_port_var = tk.StringVar(root)
        self.file_name = ""

        self.init_ui()

    def init_ui(self):
        # Baud Rate Configuration
        baud_rate_label = tk.Label(self.root, text="Baud Rate:")
        baud_rate_label.pack(pady=5)
        baud_rate_menu = tk.OptionMenu(self.root, self.baud_rate_var, "9600", "115200")
        baud_rate_menu.pack(pady=5)
        self.baud_rate_var.set("9600")  # Default baud rate

        # COM Port Configuration
        com_port_label = tk.Label(self.root, text="COM Port:")
        com_port_label.pack(pady=5)
        com_port_menu = tk.OptionMenu(self.root, self.com_port_var, *[f"COM{i}" for i in range(10)])
        com_port_menu.pack(pady=5)
        self.com_port_var.set("COM7")  # Default COM port

        # Monitoring Control Buttons
        self.start_button = tk.Button(self.root, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self.root, text="Stop Monitoring", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        # Status Display Label
        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack(pady=10)

    def start_monitoring(self):
        # Start serial data monitoring
        try:
            self.file_name = self.get_file_name()
            self.serial_port = serial.Serial(self.com_port_var.get(), int(self.baud_rate_var.get()))
            self.start_button["state"] = tk.DISABLED
            self.stop_button["state"] = tk.NORMAL
            self.status_label["text"] = "Monitoring started"
            self.root.after(100, self.read_serial_data)
        except Exception as e:
            self.status_label["text"] = f"Error: {e}"

    def stop_monitoring(self):
        # Stop serial data monitoring
        if self.serial_port:
            self.serial_port.close()
            self.start_button["state"] = tk.NORMAL
            self.stop_button["state"] = tk.DISABLED
            self.status_label["text"] = "Monitoring stopped"

    def read_serial_data(self):
        # Read and process serial data
        if self.serial_port and self.serial_port.is_open:
            try:
                data = self.serial_port.readline().decode("utf-8").strip()
                if data:  # Checking if data is not empty
                    timestamp = datetime.now().strftime("%Y-%m-%d, %H:%M:%S.%f")[:-3]
                    data_with_timestamp = f"{timestamp}, {data}\n"
                    self.status_label["text"] = data_with_timestamp
                    self.save_data_to_file(data_with_timestamp)
                    self.root.after(100, self.read_serial_data)
                else:
                    self.status_label["text"] = "Invalid data received"
                    self.root.after(100, self.read_serial_data)
            except Exception as e:
                self.status_label["text"] = f"Error: {e}"
                self.root.after(100, self.read_serial_data)

    def get_file_name(self):
        # Get file name for saving data
        date_prefix = datetime.now().strftime("%Y-%m-%d %H.%M.%S.%f")[:-3]
        file_suffix = tkinter.simpledialog.askstring("File Suffix", "Enter file suffix (or leave empty):")
        file_suffix = f"{file_suffix}" if file_suffix else ""
        file_name = f"{date_prefix} {file_suffix}.csv"
        return filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], initialfile=file_name)

    def save_data_to_file(self, data):
        # Save data to file
        if self.file_name:
            with open(self.file_name, "a", newline="") as file:
                file.write(data)
            self.status_label["text"] = f"Data saved to {self.file_name}"

# Tkinter GUI initialization
if __name__ == "__main__":
    root = tk.Tk()
    monitor = SerialMonitor(root)
    root.mainloop()
