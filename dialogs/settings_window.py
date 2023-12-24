from os import path
from tkinter import filedialog

import customtkinter as ctk
from tktooltip import ToolTip

from libs.utils import get_formatted_date, get_icon
from libs import constants


class SettingsWindow:
    def __init__(self, parent, settings, on_distroy=None):
        self.parent = parent

        self.place_holder = "Optional suffix"
        settings_icon = get_icon(path.join(constants.ASSET_PATH, "Smallicon_help.ico"))
        self.settings = settings
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
            values=[i for i in constants.FILE_NAME_TEMPLATE.keys()],
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
            300, lambda: self.settings_window.iconphoto(False, settings_icon)
        ),

        self.load_settings()
        self.settings_window.focus()
        self.settings_window.wait_visibility()
        self.settings_window.grab_set()

    def combo_format_selected(self, choice):
        foramtted_date = get_formatted_date(
            constants.FILE_NAME_TEMPLATE.get(choice, choice)
        )
        if choice != "User Input":
            self.file_template_render.set(foramtted_date + "[Optional suffix].csv")
            self.place_holder = "Optional suffix"
        else:
            self.file_template_render.set(
                foramtted_date + "[User must input file name].csv"
            )

            self.place_holder = "Enter File Name"

        self.template_var.set(choice)
        self.settings["file_name_template"] = choice

    def load_settings(self):
        self.folder_var.set(self.settings["folder"])
        self.template_var.set(self.settings["file_name_template"])
        self.combo_format.set(self.settings["file_name_template"])
        foramtted_date = get_formatted_date(
            constants.FILE_NAME_TEMPLATE.get(
                self.settings["file_name_template"],
                self.settings["file_name_template"],
            )
        )
        if self.settings["file_name_template"] != "User Input":
            self.file_template_render.set(foramtted_date + "[Optional suffix].csv")
        else:
            self.file_template_render.set(foramtted_date + ".csv")

        self.template_var.set(self.settings["file_name_template"])
        self.buffer_var.set(self.settings["buffer_size"])

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if not folder_selected:
            folder_selected = self.settings["folder"]
        if folder_selected:
            self.folder_var.set(folder_selected)

    def settings_ok(self):
        self.settings["folder"] = self.folder_var.get()
        self.settings["file_name_template"] = self.combo_format.get()

        self.settings["buffer_size"] = self.buffer_var.get()
        if self.on_distroy:
            self.on_distroy()
        self.settings_window.destroy()
