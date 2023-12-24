import sys
import os
from datetime import datetime
from PIL import Image
from PIL import ImageTk


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_formatted_date(format_str, suffix=""):
    format_str = format_str.replace("%o", suffix)
    return datetime.now().strftime(format_str)

def get_icon(icon_path):
    return ImageTk.PhotoImage(Image.open(resource_path(icon_path)))
