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





def get_com_port(settings):
    com_ports = [f"COM{i}" for i in range(10)]
    if not settings["com_port"] in com_ports:
        com_ports.append(settings["com_port"])
    return com_ports


def get_formatted_date(format_str, suffix=""):
    format_str = format_str.replace("%o", suffix)
    return datetime.now().strftime(format_str)


def get_icon(icon_path):
    return ImageTk.PhotoImage(Image.open(resource_path(icon_path)))

def filter_digit(data):
    for i in data:
        if not i.isdigit():
            return False
    return True
