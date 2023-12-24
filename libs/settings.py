import os
import json

default_setting = {
    "folder": os.getcwd(),
    "file_name_template": "Default (Date+time+Optional suffix)",
    "suffix": "",
    "baud_rate": "9600",
    "com_port": "COM7",
    "buffer_size": "10",
    "theme": "dark",
}


def load_settings(settings_path):
    if os.path.isfile(settings_path):
        with open(settings_path) as f:
            settings = json.load(f)
            if not os.path.isdir(settings["folder"]):
                settings["folder"] = os.getcwd()
            return settings
    return default_setting


def save_settings(settings_file, settings):
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=4)
