import tkinter as tk
from tkinter import ttk
import serial
from serial.tools import list_ports
from datetime import datetime

from tkinter import scrolledtext
# Define colors for the dark theme
dark_bg = "#2c2f33"
light_text = "#ffffff"
accent_color = "#7289da"
button_bg = "#23272a"


def get_com_ports():
    return [port.device for port in list_ports.comports()]


class SerialMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Monitor")
        self.root.geometry("450x350")  # Set main window size to a 16:9 ratio
        self.root.configure(bg=dark_bg)

        self.serial_port = None
        self.baud_rate_var = tk.StringVar(value="9600")
        self.com_port_var = tk.StringVar(value="COM7")
        self.file_suffix = tk.StringVar(value="")  # Variable to hold the user-entered suffix
        self.monitoring = False  # Flag to control the monitoring state

        self.total_row_count = 0

        self.output_message = ""

        self.init_ui()

    def init_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        large_font = ("Helvetica",14,)  # Adjust the size as needed, 14 is an example for 50% larger
        style.configure("TLabel", background=dark_bg, foreground=light_text)
        style.configure("TButton", background=button_bg, foreground=light_text)
        style.configure("TEntry",background=dark_bg,foreground=light_text,fieldbackground="#43454a",)
        style.map("TButton",background=[("active", accent_color)],foreground=[("active", light_text)],)

        ttk.Label(self.root, text="COM Port:").pack(pady=5)
        ttk.Combobox(self.root, textvariable=self.com_port_var, values=[f"COM{i}" for i in range(10)]).pack(pady=5)
         # values=[f"COM{i}" for i in range(10)],

        ttk.Label(self.root, text="Baud Rate:").pack(pady=5)
        ttk.Combobox(self.root, textvariable=self.baud_rate_var, values=["9600", "19200", "38400", "57600", "115200"]).pack(pady=5)

        ttk.Label(self.root, text="Suffix:").pack(pady=5)
        self.file_suffix_entry = ttk.Entry(self.root, textvariable=self.file_suffix)
        self.file_suffix_entry.pack(pady=5)

        self.start_stop_button = ttk.Button(
            self.root, text="Start Monitoring", command=self.toggle_monitoring
        )
        self.start_stop_button.pack(pady=10)

        self.status_label = ttk.Label(self.root, text="")
        self.status_label.pack(pady=10)

        # Add Output Window (Text widget)
       
        self.output_window = scrolledtext.ScrolledText(
            self.root, height=5, bg="white", fg="black", wrap=tk.WORD
        )
        self.output_window.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=5)

        # Set the state of the ScrolledText widget to DISABLED
        self.output_window.config(state=tk.DISABLED)
               
    def toggle_monitoring(self):
        if not self.monitoring:
            # Start monitoring
            self.file_name = (self.get_file_name())  # Update the file name with the current date and time
            try:
                self.serial_port = serial.Serial(
                    self.com_port_var.get(), int(self.baud_rate_var.get()), timeout=1
                )
                self.start_stop_button["text"] = "Stop Monitoring"
                self.monitoring = True
                self.status_label[
                    "text"
                ] = f"Monitoring started, saving to {self.file_name}"
                self.append_output("Monitoring started",end="")

                self.output_message = self.output_window.get(1.0, tk.END)

                self.read_serial_data()

            except serial.SerialException as e:
                self.status_label["text"] = f"Error: {e}"
                self.append_output("Error: Unable to open com port")
        else:
            # Stop monitoring
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            self.start_stop_button["text"] = "Start Monitoring"
            self.monitoring = False
            self.status_label["text"] = "Monitoring stopped"

            self.total_row_count = 0
            self.append_output(f"Data saved to {self.file_name}")
            self.append_output("Monitoring stopped")
            self.append_output("_"*60,end="\n\n")
            self.output_message = self.output_window.get(1.0, tk.END)

    def read_serial_data(self):
        if self.monitoring and self.serial_port and self.serial_port.is_open:
            data = self.serial_port.readline()
            if data:
                timestamped_data = f"{datetime.now().strftime('%Y-%m-%d,%H:%M:%S.%f')[:-3]}, {data.decode().strip()}\n"
                self.save_data_to_file(timestamped_data)
                self.total_row_count += 1
                self.replace_output(
                    self.output_message + f"Total {self.total_row_count} written"
                )

            self.root.after(100, self.read_serial_data)

    def save_data_to_file(self, data):
        with open(self.file_name, "a") as file:
            file.write(data)
            self.status_label["text"] = f"Data saved to {self.file_name}"

    def get_file_name(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
        return f"{current_time} {self.file_suffix.get()}.csv"

    def replace_output(self, new_text,end="\n"):
        """Replace the entire content of the output window."""
        self.output_window.config(state=tk.NORMAL)  # Enable editing to replace text
        self.output_window.delete(1.0, tk.END)  # Delete existing content
        self.output_window.insert(tk.END, new_text + end)  # Insert new text
        self.output_window.config(state=tk.DISABLED)  # Disable editing again
        self.output_window.see(tk.END)  # Scroll to the end

    def append_output(self, text,end="\n"):
        """Append text to the output window."""
        self.output_window.config(state=tk.NORMAL)  # Enable editing to append text
        self.output_window.insert(tk.END, text + end)  # Append text
        self.output_window.config(state=tk.DISABLED)  # Disable editing again
        self.output_window.see(tk.END)  # Scroll to the end


if __name__ == "__main__":
    root = tk.Tk()
    app = SerialMonitor(root)
    root.mainloop()
