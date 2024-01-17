import os
from datetime import datetime
from os import path
import threading

from PIL import Image
from tktooltip import ToolTip
import customtkinter as ctk

from libs.utils import (
    get_icon,
    get_formatted_date,
    resource_path,
    get_com_port,
)
from libs import constants
from libs import settings as st

from libs.serial_communicator import SerialCommunicator
from dialogs.settings_window import SettingsWindow
from dialogs.help_window import HelpWindow

PAD_X = 10
PAD_y = 10


class SerialMonitor:
    def __init__(self, root):
        self.serial_communicator = SerialCommunicator()
        self.serial_thread = None
        self.data_buffer = []

        self.settings = st.load_settings(constants.SETTINGS_FILE)
        self.place_holder = (
            "Enter File name"
            if self.settings["file_name_template"] == "User Input"
            else "Optional suffix"
        )

        ctk.set_appearance_mode(self.settings.get("theme", "dark"))

        self.buffer_limit = int(
            self.settings["buffer_size"]
        )  # Number of lines after which to flush the buffer
        self.root = root
        self.root.title("Serial to CSV")

        self.root.geometry(constants.MAIN_WINDOW_GEOMETRY)

        x_coordinate = (root.winfo_screenwidth() - constants.MAIN_WINDOW_WIDTH) // 2
        y_coordinate = (root.winfo_screenheight() - constants.MAIN_WINDO_HEIGHT) // 2
        self.root.geometry(f"+{x_coordinate}+{y_coordinate}")

        self.root.resizable(False, False)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.configure()

        self.root.grid_columnconfigure((0), weight=1)

        self.serial_port = None

        self.file_suffix = ctk.StringVar(
            value=self.settings["suffix"]
        )  # Variable to hold the user-entered suffix
        self.monitoring = False  # Flag to control the monitoring state

        self.total_row_count = 0

        self.buffer_flush_count = 0  # Variable to track buffer flush count
        self.output_message = ""
        self.file_path = self.settings["folder"]
        self.icon_path = get_icon(path.join(constants.ASSET_PATH, "Smallicon.ico"))

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
                    constants.FILE_NAME_TEMPLATE.get(
                        self.settings["file_name_template"],
                        self.settings["file_name_template"],
                    )
                )
            )
        )

    def on_closing(self):
        self.settings["suffix"] = self.file_suffix_entry.get()
        st.save_settings(constants.SETTINGS_FILE, self.settings)
        self.save_log_file()
        if self.serial_thread:
            self.stop_logging_thread()
            self.serial_communicator.close_serial_port()
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
            values=get_com_port(self.settings),
            command=self.com_port_clicked,
        )
        self.combo_com_port.place(x=10, y=25)
        self.combo_com_port.set(self.settings["com_port"])
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
        self.combo_baud_rate.set(self.settings["baud_rate"])
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
            placeholder_text=self.place_holder,
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
            command=lambda :HelpWindow(self.root),
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
    def com_port_clicked(self, choice):
        self.settings["com_port"] = choice

    def baud_rate_clicked(self, choice):
        self.settings["baud_rate"] = choice

    def open_settings(self):
        self.settings_window = SettingsWindow(
            self.root, self.settings, self.settings_window_distroy
        )

    def settings_window_distroy(self):
        self.settings = self.settings_window.settings
        self.place_holder = self.settings_window.place_holder
        st.save_settings(constants.SETTINGS_FILE, self.settings)
        self.file_suffix_entry.configure(placeholder_text=self.place_holder)
        self.update_lbl_prefix()

    def open_serial_port(self):
        self.serial_communicator.open_serial_port(
            self.settings["com_port"],
            int(self.settings["baud_rate"]),
        )

    def create_logging_thread(self):
        self.serial_communicator.stop_thread = False
        self.serial_thread = threading.Thread(target=self.serial_reader)
        self.serial_thread.start()

    def stop_logging_thread(self):
        self.serial_communicator.stop_thread = True
        self.serial_thread.join()

    def toggle_monitoring(self):
        self.settings["com_port"] = self.combo_com_port.get()
        self.settings["baud_rate"] = self.combo_baud_rate.get()
        if not self.monitoring:
            # Start monitoring
            self.file_name = self.get_file_name()  # Update the file name
            self.file_path = os.path.join(self.settings["folder"], self.file_name)
            try:
                self.open_serial_port()
                self.create_logging_thread()
                self.start_stop_button.configure(text="Stop Monitoring")
                self.monitoring = True

                self.replace_output(
                    f"Monitoring started, saving to {self.file_name}", end="",mode="a"
                )
                self.output_message = self.output_window.get(1.0, ctk.END)
                self.root.after(100, self.update_output)
            except Exception as e:
                self.replace_output(f"Error: {e}",mode="a")
        else:
            # Stop monitoring

            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            self.start_stop_button.configure(text="Start Monitoring")

            self.stop_logging_thread()
            self.serial_communicator.close_serial_port()
            self.flush_buffer()  # Flush buffer when stopping
            self.update_output()
            self.monitoring = False
            self.replace_output("Monitoring stopped",mode="a")
            self.replace_output(f"Data saved to {self.file_name}",mode="a")
            self.total_row_count = 0
            self.buffer_flush_count = 0
            self.output_message = self.output_window.get(1.0, ctk.END)

    def serial_reader(self):
        starting_time = datetime.now()
        while not self.serial_communicator.stop_thread:
            line = self.serial_communicator.read_line()
            if line:
                current_time = datetime.now()
                elapsed_time = current_time - starting_time
                timestamped_data = f"{current_time.strftime('%Y-%m-%d,%H:%M:%S.%f')[:-3]},{str(elapsed_time)[:-3]},{line}\n"
                self.data_buffer.append(timestamped_data)
                if len(self.data_buffer) >= int(self.settings["buffer_size"]):
                    self.flush_buffer()
                self.total_row_count += 1

    def flush_buffer(self):
        with open(self.file_path, "a") as file:
            file.writelines(self.data_buffer)
        self.data_buffer.clear()  # Clear the buffer after flushing
        self.buffer_flush_count += 1  # Increment buffer flush count

    def update_output(self):
        if self.monitoring:
            text = f"Row Count = {self.total_row_count}, Buffer Flush = {self.buffer_flush_count}"
            self.replace_output(self.output_message + text)
            self.root.after(100, self.update_output)

    def get_file_name(self, ext=".csv"):
        template = self.settings["file_name_template"]
        current_time = get_formatted_date(
            constants.FILE_NAME_TEMPLATE.get(template, template),
            suffix=self.file_suffix_entry.get(),
        )
        return f"{current_time}{ext}"

    def replace_output(self, text, end="\n",mode="w"):
        """Replace the entire content of the output window."""
        self.output_window.configure(state=ctk.NORMAL)  # Enable editing to replace text
        if mode == "w":
            self.output_window.delete(1.0, ctk.END)  # Delete existing content
            self.output_window.insert(ctk.END, text + end)  # Insert new text
        else:
            self.output_window.insert(ctk.END, text + end)  # Append text
        self.output_window.configure(state=ctk.DISABLED)  # Disable editing again
        self.output_window.see(ctk.END)  # Scroll to the end


if __name__ == "__main__":
    root = ctk.CTk()
    app = SerialMonitor(root)
    root.mainloop()
