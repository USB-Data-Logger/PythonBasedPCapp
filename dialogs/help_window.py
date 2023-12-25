

from os import path

import customtkinter as ctk
from PIL import Image

from libs import constants
from libs.utils import get_icon,resource_path

class HelpWindow:
    def __init__(self,parent):
        self.help_window = ctk.CTkToplevel(parent)
        help_icon_path = get_icon(path.join(constants.ASSET_PATH, "Smallicon_help.ico"))

        # Load the PNG file
        image = Image.open(
            resource_path(path.join(constants.ASSET_PATH, "HelpImage.png"))
        )
        # Convert the image to a format which Tkinter can use
        photo = ctk.CTkImage(light_image=image, size=image.size)

        # Create a new window or Use an existing widget to disply the image
        self.help_window.transient(parent)
        self.help_window.title("Help Image")
        self.help_window.wm_iconbitmap()

        # Set the help window icon
        # https://github.com/TomSchimansky/CustomTkinter/issues/2160
        self.help_window.after(300, lambda: self.help_window.iconphoto(False, help_icon_path))
        self.help_window.wait_visibility()
        self.help_window.grab_set()

        # Create a label in the new window to display the image
        image_label = ctk.CTkLabel(self.help_window, image=photo, text="")

        image_label.pack(fill=ctk.BOTH, expand=True)

