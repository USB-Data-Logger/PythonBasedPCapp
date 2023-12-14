import tkinter as tk
import serial
from tkinter import ttk
from serial.tools import list_ports
from datetime import datetime
from tkinter import filedialog
from tkinter import scrolledtext
import json
import os

# Define colors for the dark theme
dark_bg = "#2c2f33"
light_text = "#ffffff"
accent_color = "#7289da"
button_bg = "#23272a"

SETTINGS_FILE = "settings.json"

file_name_template = {
    "Default": "%Y-%m-%d %H.%M.%S",
    "Date only": "%Y-%m-%d",
    "With Milisecond": "%Y-%m-%d %H.%M.%S.%f",
}

pad_x = 20


def load_settings(settings_path):
    file_obj = open(settings_path)
    settings = json.load(file_obj)
    if not os.path.isdir(settings["folder"]):
        settings["folder"] = os.getcwd()

    file_obj.close()
    return settings


settings = load_settings(SETTINGS_FILE)


def get_com_ports():
    return [port.device for port in list_ports.comports()]


def save_settings(settings_file, settings):
    file_obj = open(settings_file, "w")
    json.dump(settings, file_obj, indent=4)
    file_obj.close()


def get_formatted_date(format_str):
    return datetime.now().strftime(format_str)


class HintEntry(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey',*args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def get(self):
        if not  self['fg']==self.placeholder_color:
            return super().get()
        return ""

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()

class SettingsWindow:
    def __init__(self, parent):
       
        self.parent = parent
        self.settings_window = tk.Toplevel(parent)

        self.settings_window.configure(bg=dark_bg)
        self.settings_window.title("Settings")
        self.settings_window.geometry("450x200")
        self.settings_window.resizable(False, False)
        # Folder Selection
        self.folder_label = ttk.Label(self.settings_window, text="Select Folder:")
        self.folder_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.folder_var = tk.StringVar()
        self.folder_entry = ttk.Entry(
            self.settings_window, textvariable=self.folder_var, width=30
        )
        self.folder_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        self.browse_button = ttk.Button(
            self.settings_window, text="Browse", command=self.browse_folder
        )
        self.browse_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

        # File Name Template
        self.template_label = ttk.Label(
            self.settings_window, text="File Name Template:"
        )
        self.template_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.template_var = tk.StringVar()
        self.combo_format = ttk.Combobox(
            self.settings_window,
            textvariable=self.template_var,
            values=[i for i in file_name_template.keys()],
        )
        self.combo_format.grid(
            row=1,
            column=1,
            padx=10,
            pady=5,
            sticky=tk.W,
        )

        self.combo_format.bind("<<ComboboxSelected>>", self.combo_format_selected)

        self.file_template_render = tk.StringVar()
        ttk.Label(self.settings_window, textvariable=self.file_template_render).grid(
            row=2, columnspan=2, padx=pad_x, sticky=tk.W
        )

        # Buffer Size
        self.buffer_label = ttk.Label(self.settings_window, text="Buffer Size:")
        self.buffer_label.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        self.buffer_var = tk.StringVar()
        self.buffer_entry = ttk.Entry(
            self.settings_window, textvariable=self.buffer_var, width=10
        )
        self.buffer_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

        # OK Button
        self.ok_button = ttk.Button(
            self.settings_window, text="OK", command=self.settings_ok
        )
        self.ok_button.grid(row=4, column=0, columnspan=3, pady=10)
        self.load_settings()

    def combo_format_selected(self, event):
        template = self.template_var.get()
        foramtted_date = get_formatted_date(file_name_template.get(template, template))
        self.file_template_render.set(foramtted_date)

    def load_settings(self):
        self.folder_var.set(settings["folder"])
        self.template_var.set(settings["file_name_template"])
        foramtted_date = get_formatted_date(
            file_name_template.get(
                settings["file_name_template"], settings["file_name_template"]
            )
        )
        self.file_template_render.set(foramtted_date)

        self.buffer_var.set(settings["buffer_size"])

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_var.set(folder_selected)

    def settings_ok(self):
        settings["folder"] = self.folder_var.get()
        settings["file_name_template"] = self.template_var.get()
        settings["buffer_size"] = self.buffer_var.get()
        self.settings_window.destroy()


class SerialMonitor:
    def __init__(self, root):
        self.data_buffer = []
        self.buffer_limit = int(
            settings["buffer_size"]
        )  # Number of lines after which to flush the buffer
        self.root = root
        self.root.title("Serial to CSV")
        self.root.geometry("450x300")  # Set main window size to a 16:9 ratio

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        #self.root.resizable(False, False) # to make thing more flexiabel
        self.root.configure(bg=dark_bg)

        self.serial_port = None
        self.baud_rate_var = tk.StringVar(value=settings["baud_rate"])
        self.com_port_var = tk.StringVar(value=settings["com_port"])
        self.file_suffix = tk.StringVar(
            value=settings["suffix"]
        )  # Variable to hold the user-entered suffix
        self.monitoring = False  # Flag to control the monitoring state

        self.total_row_count = 0

        self.buffer_flush_count = 0  # Variable to track buffer flush count
        self.output_message = ""
        self.file_path = settings["folder"]

        self.init_ui()

    def on_closing(self):
        settings["suffix"] = self.file_suffix_entry.get()
        settings["baud_rate"] = self.baud_rate_var.get()
        settings["com_port"] = self.com_port_var.get()
        save_settings(SETTINGS_FILE, settings)
        self.root.destroy()

    def init_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        # large_font = ("Helvetica",14,)  # Adjust the size as needed, 14 is an example for 50% larger
        style.configure("TLabel", background=dark_bg, foreground=light_text)
        style.configure("TButton", background=button_bg, foreground=light_text)
        style.configure(
            "TEntry",
            background=dark_bg,
            foreground=light_text,
            fieldbackground="#43454a",
        )
        style.map(
            "TButton",
            background=[("active", accent_color)],
            foreground=[("active", light_text)],
        )
        frame = tk.Frame(root, bg=dark_bg)
        frame.pack(fill=tk.X)

        ttk.Label(frame, text="COM Port:", font=("impack", 20, "bold")).grid(
            row=0, column=0, padx=pad_x
        )
        ttk.Label(frame, text="Baud Rate:", font=("impack", 20, "bold")).grid(
            row=0, column=1, padx=pad_x
        )

        ttk.Combobox(
            frame,
            textvariable=self.com_port_var,
            values=[f"COM{i}" for i in range(10)],
        ).grid(row=1, column=0, padx=pad_x)

        ttk.Combobox(
            frame,
            textvariable=self.baud_rate_var,
            values=["9600", "19200", "38400", "57600", "115200"],
        ).grid(row=1, column=1, padx=pad_x)
        ttk.Label(self.root, text="type in custom value or address if needed").place(
            x=5, y=65
        )
        # values=[f"COM{i}" for i in range(10)],

        ttk.Label(self.root, text="type in custom rate if needed").place(x=260, y=65)

        ttk.Label(
            self.root,
            text="Output file name",
            font=(
                "impack",
                10,
            ),
        ).place(x=10, y=90)
        ttk.Label(self.root, text="YYYY-MM-DD HH.MM.SS").place(x=30, y=115)
        ttk.Label(self.root, text=".csv").place(x=300, y=115)
        self.file_suffix_entry = HintEntry(
            self.root,
            textvariable=self.file_suffix,
            placeholder="optional suffix",
        )
        self.file_suffix_entry.place(x=170, y=115)

        self.start_stop_button = ttk.Button(
            self.root, text="Start Monitoring", command=self.toggle_monitoring
        )

        self.start_stop_button.place(x=180, y=140)
        self.setting_btn = ttk.Button(
            self.root, text="Settings", command=self.open_settings
        )

        self.setting_btn.place(x=360, y=140)

        self.status_label = ttk.Label(self.root, text="Monitoring Console")
        self.status_label.place(x=10, y=155)

        # Add Output Window (Text widget)

        self.output_window = scrolledtext.ScrolledText(
            self.root, height=7, bg="white", fg="black", wrap=tk.WORD   #setting for how many line
        )
        self.output_window.pack(side="bottom", fill=tk.X)

        # Set the state of the ScrolledText widget to DISABLED
        self.output_window.config(state=tk.DISABLED)

    def open_settings(self):
        settings_window = SettingsWindow(self.root)

    def toggle_monitoring(self):
        if not self.monitoring:
            # Start monitoring
            self.file_name = self.get_file_name()  # Update the file name
            self.file_path = os.path.join(settings["folder"], self.file_name)
            try:
                self.serial_port = serial.Serial(
                    self.com_port_var.get(), int(self.baud_rate_var.get()), timeout=1
                )
                self.start_stop_button["text"] = "Stop Monitoring"
                self.monitoring = True
                self.append_output(f"Monitoring started, saving to {self.file_name}")
                self.read_serial_data()
            except serial.SerialException as e:
                self.append_output(f"Error: {e}")
        else:
            # Stop monitoring
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            self.start_stop_button["text"] = "Start Monitoring"
            self.monitoring = False
            self.flush_buffer()  # Flush buffer when stopping
            self.append_output("Monitoring stopped")
            self.append_output(f"Data saved to {self.file_name}")

    def read_serial_data(self):
        if self.monitoring and self.serial_port and self.serial_port.is_open:
            data = self.serial_port.readline()
            if data:
                timestamped_data = f"{datetime.now().strftime('%Y-%m-%d,%H:%M:%S.%f')[:-3]}, {data.decode().strip()}\n"
                self.data_buffer.append(timestamped_data)
                if len(self.data_buffer) >= self.buffer_limit:
                    self.flush_buffer()  # Flush buffer if it reaches the limit
                else:
                    self.update_row_count()  # Update row count in real-time
            self.root.after(100, self.read_serial_data)




    def flush_buffer(self):
        with open(self.file_path, "a") as file:
            for data in self.data_buffer:
                file.write(data)
        self.data_buffer.clear()  # Clear the buffer after flushing
        self.buffer_flush_count += 1  # Increment buffer flush count
        self.update_output() 
   
    def update_row_count(self):
        self.total_row_count += 1
        self.update_output()  # Update the output without creating new rows

    def update_output(self):
        text = f"Row Count = {self.total_row_count}, Buffer Flush = {self.buffer_flush_count}"
        self.replace_output(text)

    def save_data_to_file(self, data):
        with open(self.file_name, "a") as file:
            file.write(data)
            self.append_output(f"Data saved to {self.file_name}")

    def get_file_name(self):
        template = settings["file_name_template"]
        current_time = get_formatted_date(file_name_template.get(template, template))
        return f"{current_time} {self.file_suffix_entry.get()}.csv"

    def replace_output(self, new_text, end="\n"):
        """Replace the entire content of the output window."""
        self.output_window.config(state=tk.NORMAL)  # Enable editing to replace text
        self.output_window.delete(1.0, tk.END)  # Delete existing content
        self.output_window.insert(tk.END, new_text + end)  # Insert new text
        self.output_window.config(state=tk.DISABLED)  # Disable editing again
        self.output_window.see(tk.END)  # Scroll to the end

    def append_output(self, text, end="\n"):
        """Append text to the output window."""
        self.output_window.config(state=tk.NORMAL)  # Enable editing to append text
        self.output_window.insert(tk.END, text + end)  # Append text
        self.output_window.config(state=tk.DISABLED)  # Disable editing again
        self.output_window.see(tk.END)  # Scroll to the end


if __name__ == "__main__":
    root = tk.Tk()
    app = SerialMonitor(root)
    root.mainloop()
