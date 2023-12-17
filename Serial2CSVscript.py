import customtkinter as ctk

import serial
from serial.tools import list_ports
from datetime import datetime
import json
import os
import logging
from plyer import filechooser
from tktooltip import ToolTip
from PIL import Image
from PIL import ImageTk
import sys

ctk.set_appearance_mode("dark")
default_setting = {
    "folder": os.getcwd(),
    "file_name_template": "Default (Date+time+Optional suffix)",
    "suffix": "",
    "baud_rate": "9600",
    "com_port": "COM7",
    "buffer_size": "10",
}


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_resources(resource):
    return resource_path(os.path.join(ASSET_PATH, resource))


SETTINGS_FILE = "settings.json"
ASSET_PATH = "asset"


file_name_template = {
    "Default (Date+time+Optional suffix)": "%Y-%m-%d %H.%M.%S %o",
    "Date only (Date+Optional suffix)": "%Y-%m-%d %o",
    "User Input": "%o",
}

pad_x = 10
pad_y = 10


def load_settings(settings_path):
    if os.path.isfile(settings_path):
        with open(settings_path) as f:
            settings = json.load(f)
            if not os.path.isdir(settings["folder"]):
                settings["folder"] = os.getcwd()
            return settings
    return default_setting


settings = load_settings(SETTINGS_FILE)

place_holder = (
    "Enter File name"
    if settings["file_name_template"] == "User Input"
    else "Optional suffix"
)


def _get_com_ports():
    return [port.device for port in list_ports.comports()]


def save_settings(settings_file, settings):
    file_obj = open(settings_file, "w")
    json.dump(settings, file_obj, indent=4)
    file_obj.close()


def get_formatted_date(format_str, suffix=""):
    format_str = format_str.replace("%o", suffix)
    return datetime.now().strftime(format_str)


def get_com_port():
    com_ports = [f"COM{i}" for i in range(10)]
    if not settings["com_port"] in com_ports:
        com_ports.append(settings["com_port"])
    return com_ports


class SettingsWindow:
    def __init__(self, parent, on_distroy=None):
        self.parent = parent

        self.on_distroy = on_distroy
        self.settings_window = ctk.CTkToplevel(parent)
        self.settings_window.transient(self.parent)

        self.settings_window.configure()
        self.settings_window.title("Settings")
        self.settings_window.geometry("460x200")
        self.settings_window.resizable(False, False)

        # Folder Selection
        self.folder_label = ctk.CTkLabel(
            self.settings_window, text="Select Folder Location:"
        )
        self.folder_label.place(x=10, y=7)
        self.folder_var = ctk.StringVar()
        self.folder_entry = ctk.CTkEntry(
            self.settings_window,
            width=210,
            textvariable=self.folder_var,
        )
        self.folder_entry.place(x=150, y=7)
        ToolTip(self.folder_entry, msg=self.folder_var.get)

        self.browse_button = ctk.CTkButton(
            self.settings_window,
            text="Browse",
            width=80,
            fg_color="#0F0F0F",
            hover_color="#474747",
            command=self.browse_folder,
        )
        self.browse_button.place(x=373, y=7)

        # File Name Template
        self.template_label = ctk.CTkLabel(
            self.settings_window, text="File Name Template:"
        )
        self.template_label.place(x=10, y=50)
        self.template_var = ctk.StringVar()
        self.combo_format = ctk.CTkComboBox(
            self.settings_window,
            values=[i for i in file_name_template.keys()],
            command=self.combo_format_selected,
            width=300,
        )
        self.combo_format.place(x=150, y=50)

        self.file_template_render = ctk.StringVar()
        ctk.CTkLabel(
            self.settings_window,
            font=("impack", 15, "bold"),
            width=150,
            textvariable=self.file_template_render,
        ).place(x=150, y=80)

        # Buffer Size
        self.buffer_label = ctk.CTkLabel(self.settings_window, text="Buffer Size:")
        self.buffer_label.place(x=20, y=110)

        self.buffer_var = ctk.StringVar()

        self.buffer_entry = ctk.CTkEntry(
            self.settings_window, textvariable=self.buffer_var
        )
        self.buffer_entry.place(x=150, y=110)

        # Save and Exit Button
        self.save_and_exit_btn = ctk.CTkButton(
            self.settings_window,
            text="Save And Exit",
            fg_color="#0F0F0F",
            hover_color="#474747",
            command=self.settings_ok,
        )
        self.save_and_exit_btn.place(x=150, y=160)

        self.discard_button = ctk.CTkButton(
            self.settings_window,
            text="Discard Settings",
            fg_color="#0F0F0F",
            hover_color="#474747",
            command=self.settings_window.destroy,
        )
        self.discard_button.place(x=310, y=160)

        self.settings_window.wm_iconbitmap()
        self.settings_window.after(
            300,
            lambda: self.settings_window.iconphoto(
                False, ImageTk.PhotoImage(Image.open(get_resources("Smallicon.png")))
            ),
        )
        self.load_settings()
        self.settings_window.focus()

    def combo_format_selected(self, choice):
        global place_holder
        foramtted_date = get_formatted_date(file_name_template.get(choice, choice))
        if choice != "User Input":
            self.file_template_render.set(foramtted_date + "[Optional suffix].csv")
            place_holder = "Optional suffix"
        else:
            self.file_template_render.set(
                foramtted_date + "[User must input file name].csv"
            )

            place_holder = "Enter File Name"

        self.template_var.set(choice)
        settings["file_name_template"] = choice

    def load_settings(self):
        self.folder_var.set(settings["folder"])
        self.template_var.set(settings["file_name_template"])
        self.combo_format.set(settings["file_name_template"])
        foramtted_date = get_formatted_date(
            file_name_template.get(
                settings["file_name_template"],
                settings["file_name_template"],
            )
        )
        if settings["file_name_template"] != "User Input":
            self.file_template_render.set(foramtted_date + "[Optional suffix].csv")
        else:
            self.file_template_render.set(foramtted_date + ".csv")

        self.template_var.set(settings["file_name_template"])
        self.buffer_var.set(settings["buffer_size"])

    def browse_folder(self):
        folder_selected = filechooser.choose_dir()
        if folder_selected:
            folder_selected = folder_selected[0]
        else:
            folder_selected = settings["folder"]
        if folder_selected:
            self.folder_var.set(folder_selected)

    def settings_ok(self):
        settings["folder"] = self.folder_var.get()
        settings["file_name_template"] = self.combo_format.get()

        settings["buffer_size"] = self.buffer_var.get()
        if self.on_distroy:
            self.on_distroy()
        self.settings_window.destroy()


class SerialMonitor:
    def __init__(self, root):
        self.data_buffer = []
        self.buffer_limit = int(
            settings["buffer_size"]
        )  # Number of lines after which to flush the buffer
        self.root = root
        self.root.title("Serial to CSV")

        root_width = 450
        root_height = 300
        self.root.geometry(f"{root_width}x{root_height}")

        x_coordinate = (root.winfo_screenwidth() - root_width) // 2
        y_coordinate = (root.winfo_screenheight() - root_height) // 2
        self.root.geometry(f"+{x_coordinate}+{y_coordinate}")

        self.root.resizable(False, False)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.configure()

        self.root.grid_columnconfigure((0), weight=1)

        self.serial_port = None

        self.file_suffix = ctk.StringVar(
            value=settings["suffix"]
        )  # Variable to hold the user-entered suffix
        self.monitoring = False  # Flag to control the monitoring state

        self.total_row_count = 0

        self.buffer_flush_count = 0  # Variable to track buffer flush count
        self.output_message = ""
        self.file_path = settings["folder"]
        self.icon_path = ImageTk.PhotoImage(Image.open(get_resources("Smallicon.png")))

        self.root.wm_iconbitmap()
        self.root.iconphoto(False, self.icon_path)
        self.init_ui()
        self.update_lbl_prefix()

    def save_log_file(self):
        with open("log.txt", "a") as log_file:
            log_file.write(self.output_message)

    def update_lbl_prefix(self):
        self.lbl_prefix.configure(
            text=(
                get_formatted_date(
                    file_name_template.get(
                        settings["file_name_template"], settings["file_name_template"]
                    )
                )
            )
        )

    def on_closing(self):
        settings["suffix"] = self.file_suffix_entry.get()
        save_settings(SETTINGS_FILE, settings)
        self.save_log_file()
        self.root.destroy()

    def init_ui(self):
        ctk.CTkLabel(self.root, text="COM Port:", font=("impack", 20, "bold")).place(
            x=30, y=0
        )
        ctk.CTkLabel(self.root, text="Baud Rate:", font=("impack", 20, "bold")).place(
            x=320, y=0
        )

        self.combo_com_port = ctk.CTkComboBox(
            self.root,
            values=get_com_port(),
            command=self.com_port_clicked,
        )
        self.combo_com_port.place(x=10, y=25)
        self.combo_com_port.set(settings["com_port"])
        ToolTip(
            self.combo_com_port,
            msg="you can type custom com port number\n or path address in the window",
            bg="grey",
            fg="white",
        )

        self.combo_baud_rate = ctk.CTkComboBox(
            self.root,
            values=["9600", "19200", "38400", "57600", "115200"],
            command=self.baud_rate_clicked,
        )
        self.combo_baud_rate.place(x=300, y=25)
        self.combo_baud_rate.set(settings["baud_rate"])
        ToolTip(
            self.combo_baud_rate,
            msg="you can type custom value\nin the window if needed",
            bg="grey",
            fg="white",
            x_offset=-90,
        )

        ctk.CTkLabel(
            self.root,
            text="Output file name",
            font=(
                "impack",
                15,
            ),
        ).place(x=170, y=65)

        self.lbl_prefix = ctk.CTkLabel(self.root)
        self.lbl_prefix.place(x=30, y=90)
        self.file_suffix_entry = ctk.CTkEntry(
            self.root,
            # Here the placeholder text needs to be updated accordingly
            placeholder_text=place_holder,
        )

        self.file_suffix_entry.place(x=155, y=90)
        ctk.CTkLabel(self.root, text=".csv").place(x=300, y=90)

        self.start_stop_button = ctk.CTkButton(
            self.root,
            text="Start Monitoring",
            fg_color="#0F0F0F",
            hover_color="#474747",
            command=self.toggle_monitoring,
        )
        self.start_stop_button.place(x=155, y=130)

        self.help_btn = ctk.CTkButton(
            self.root,
            width=80,
            text="Help",
            fg_color="#0F0F0F",
            hover_color="#474747",
            command=self.open_help,
        )

        self.help_btn.place(x=360, y=90)

        self.setting_btn = ctk.CTkButton(
            self.root,
            width=80,
            text="Settings",
            fg_color="#0F0F0F",
            hover_color="#474747",
            command=self.open_settings,
        )

        self.setting_btn.place(x=360, y=130)

        self.status_label = ctk.CTkLabel(self.root, text="Monitoring Console")
        self.status_label.place(x=10, y=138)

        self.output_window = ctk.CTkTextbox(
            self.root,
            width=430,
            height=120,
            fg_color="#0F0F0F",
            wrap=ctk.WORD,  # setting for how many line
        )
        self.output_window.place(x=10, y=170)

        # Set the state of the ScrolledText widget to DISABLED
        self.output_window.configure(state=ctk.DISABLED)
        ToolTip(self.output_window, msg="Message")

    # Function to open Help Image
    def open_help(self):
        # Load the PNG file
        image = Image.open(get_resources("HelpImage.png"))
        # Convert the image to a format which Tkinter can use
        photo = ctk.CTkImage(light_image=image, size=image.size)

        # Create a new window or Use an existing widget to disply the image
        image_window = ctk.CTkToplevel(root)
        image_window.transient(self.root)
        image_window.title("Help Image")
        image_window.wm_iconbitmap()
        image_window.after(300, lambda: image_window.iconphoto(False, self.icon_path))

        # Create a label in the new window to display the image
        image_label = ctk.CTkLabel(image_window, image=photo, text="")
        # image_label.image = photo # Keep a reference
        image_label.pack(fill=ctk.BOTH, expand=True)

    def com_port_clicked(self, choice):
        settings["com_port"] = choice

    def baud_rate_clicked(self, choice):
        settings["baud_rate"] = choice

    def open_settings(self):
        SettingsWindow(self.root, self.settings_window_distroy)

    def settings_window_distroy(self):
        save_settings(SETTINGS_FILE, settings)
        self.file_suffix_entry.configure(placeholder_text=place_holder)
        self.update_lbl_prefix()

    def toggle_monitoring(self):
        settings["com_port"] = self.combo_com_port.get()
        settings["baud_rate"] = self.combo_baud_rate.get()
        if not self.monitoring:
            # Start monitoring
            self.file_name = self.get_file_name()  # Update the file name
            self.file_path = os.path.join(settings["folder"], self.file_name)
            try:
                self.serial_port = serial.Serial(
                    settings["com_port"], int(settings["baud_rate"]), timeout=1
                )
                self.start_stop_button.configure(text="Stop Monitoring")
                self.monitoring = True
                self.append_output(
                    f"Monitoring started, saving to {self.file_name}", end=""
                )
                self.output_message = self.output_window.get(1.0, ctk.END)
                self.read_serial_data()
            except serial.SerialException as e:
                self.append_output(f"Error: {e}")
        else:
            # Stop monitoring

            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            self.start_stop_button.configure(text="Start Monitoring")
            self.monitoring = False
            self.flush_buffer()  # Flush buffer when stopping
            self.append_output("Monitoring stopped")
            self.append_output(f"Data saved to {self.file_name}")
            self.total_row_count = 0
            self.buffer_flush_count = 0
            self.output_message = self.output_window.get(1.0, ctk.END)

    def read_serial_data(self):
        if self.monitoring and self.serial_port and self.serial_port.is_open:
            data = self.serial_port.readline()
            timestamped_data = f"{datetime.now().strftime('%Y-%m-%d,%H:%M:%S.%f')[:-3]}, {data.decode().strip()}\n"
            self.data_buffer.append(timestamped_data)

            if len(self.data_buffer) >= int(settings["buffer_size"]):
                self.flush_buffer()
            self.update_row_count()
            self.update_output()
            self.root.after(100, self.read_serial_data)

    def flush_buffer(self):
        with open(self.file_path, "a") as file:
            file.writelines(self.data_buffer)
        self.data_buffer.clear()  # Clear the buffer after flushing
        self.buffer_flush_count += 1  # Increment buffer flush count

    def update_row_count(self):
        self.total_row_count += 1

    def update_output(self):
        text = f"Row Count = {self.total_row_count}, Buffer Flush = {self.buffer_flush_count}"
        self.replace_output(self.output_message + text)

    def get_file_name(self, ext=".csv"):
        template = settings["file_name_template"]
        current_time = get_formatted_date(
            file_name_template.get(template, template),
            suffix=self.file_suffix_entry.get(),
        )
        return f"{current_time}{ext}"

    def replace_output(self, new_text, end="\n"):
        """Replace the entire content of the output window."""
        self.output_window.configure(state=ctk.NORMAL)  # Enable editing to replace text
        self.output_window.delete(1.0, ctk.END)  # Delete existing content
        self.output_window.insert(ctk.END, new_text + end)  # Insert new text
        self.output_window.configure(state=ctk.DISABLED)  # Disable editing again
        self.output_window.see(ctk.END)  # Scroll to the end

    def append_output(self, text, end="\n"):
        """Append text to the output window."""
        self.output_window.configure(state=ctk.NORMAL)  # Enable editing to append text
        self.output_window.insert(ctk.END, text + end)  # Append text
        self.output_window.configure(state=ctk.DISABLED)  # Disable editing again
        self.output_window.see(ctk.END)  # Scroll to the end


if __name__ == "__main__":
    root = ctk.CTk()
    app = SerialMonitor(root)
    root.mainloop()
