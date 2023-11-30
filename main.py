from datetime import datetime
from kivy.config import Config

Config.set("graphics", "resizable", False)
Config.set("graphics", "width", "750")
Config.set("graphics", "height", "350")

Config.write()
from kivy.app import App
import csv
from kivy.properties import BooleanProperty,NumericProperty
import serial
import threading
import libs.utils

from kivy.lang import Builder

kv = '''
#:import utils libs.utils
#:set font_size 20
#:set padding 10


<CustomOption@SpinnerOption>:
    font_size: sp(font_size)

<CustomSpinner@Spinner>:
    disabled:True if app.is_logging else False
    font_size:sp(font_size)
    option_cls: "CustomOption"
    size_hint_y:None
    height:dp(50)

<CustomLabel@Label>:
    font_size:sp(font_size)
    size_hint: None, 1
    width:self.texture_size[0] + dp(padding)

<CustomBoxLayout@BoxLayout>:
    size_hint: 1, None
    height: self.minimum_height
    spacing: dp(padding)
    padding: [dp(padding),dp(padding),dp(padding),dp(padding)]

BoxLayout:
    orientation: 'vertical'
    spacing: 10
    padding: 10
    CustomBoxLayout:
        CustomLabel:
            text: "Com port"
        CustomSpinner:
            
            disabled:True if app.is_logging or chk_custom_port.active else False
            id:drp_ports
            values:utils.get_com_ports()
            text: "Select port" if self.values else "No port"
            on_text:app.drop_ports_text_changed(self)
        CustomLabel:
            text: "Baud Rate"
        CustomSpinner:
            id:drp_baudrate
            values:utils.get_standard_baud_rate()
            text:"9600"
    CustomBoxLayout:
        CheckBox:
            id:chk_custom_port
            size_hint:None,1
            width:dp(10)
            on_active:app.chk_custom_port_clicked(self,self.active)
            active:False

        CustomLabel:
            text:"Custom port"
        TextInput: 
            id:txt_custom_port
            on_text:app.txt_custom_port_on_text(self)
            disabled:True if app.is_logging or not chk_custom_port.active else False
            hint_text:"Custom com port"
            height:self.minimum_height
            size_hint:None,None
            font_size:sp(font_size)
            multiline:False
            width:dp(500)

    CustomBoxLayout:
        spacing:0 
        CustomLabel:
            text: "File Name:- " 

        CustomLabel:
            id:lbl_file_prefix
        TextInput:
            disabled:True if app.is_logging else False
            id:txt_suffix
            text: "data"
            size_hint:None,None
            height:self.minimum_height
            width:dp(200)
            hint_text:"suffix"
            font_size:sp(font_size)
            multiline:False
        Button:
            text:"Refresh"
            on_release:app.update_file_name_prefix()
    CustomLabel:
        id: lbl_filename
        text: lbl_file_prefix.text+txt_suffix.text+".csv"
        size_hint_x:1
    CustomLabel:
        text:"Total " + str(app.count) + " Rows written" if app.count else ""
        size_hint_x:1
        disabled: btn_logging.disabled
    Button:
        id:btn_logging

        disabled:True 
        font_size:sp(20)
        text:"Stop" if app.is_logging else "Start"
        size_hint_y:None
        height:50
        on_release:app.btn_logging_released(self)

'''

class COMLoggerApp(App):
    is_logging = BooleanProperty(False)
    count = NumericProperty(0)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_name_template = "%Y_%m_%d_%H.%M.%S.%f"
    def build(self):
        return Builder.load_string(kv)

    def update_file_name_prefix(self):
        self.root.ids.lbl_file_prefix.text = (
            self.filename_from_template(self.file_name_template) + "-"
        )

    def on_start(self):
        self.update_file_name_prefix()

    def filename_from_template(self, template):
        current_time = datetime.now()
        return current_time.strftime(template)[:-3]

    def create_logging_thread(self):
        self.stop_thread = False
        self.serial_thread = threading.Thread(target=self.serial_reader)
        self.serial_thread.start()

    def drop_ports_text_changed(self, instance):
        if instance.values:
            self.root.ids.btn_logging.disabled = False
        else:
            self.root.ids.btn_logging.disabled = True
    def txt_custom_port_on_text(self,instance):
        if len(instance.text) != 0:
            self.root.ids.btn_logging.disabled = False
        else:

            self.root.ids.btn_logging.disabled = True


        
    def chk_custom_port_clicked(self, instance, is_active):
        if is_active and self.root.ids.txt_custom_port.text:
            self.root.ids.btn_logging.disabled = False
        else:
            self.root.ids.btn_logging.disabled = True

    def stop_logging_thread(self):
        self.stop_thread = True
        self.serial_thread.join()

    def close_csv_file(self):
        self.csv_file.flush()
        self.csv_file.close()

    def open_csv_file(self):
        self.csv_file = open(self.root.ids.lbl_filename.text, "w")
        self.csv_writer = csv.writer(self.csv_file)

    def _open_serial_port(self, port, baudrate):
        try:
            ser = serial.Serial(port, baudrate, timeout=1)
            return ser
        except serial.SerialException as e:
            print(f"Error: {e}")
            import sys

            sys.exit()
            return None

    def close_serial_port(self, ser):
        if ser:
            ser.close()

    def open_serial_port(self):
        if self.root.ids.chk_custom_port.active:
            self.serial_port = self._open_serial_port(
                self.root.ids.txt_custom_port.text, self.root.ids.drp_baudrate.text
            )
        else:
            self.serial_port = self._open_serial_port(
                self.root.ids.drp_ports.text, self.root.ids.drp_baudrate.text
            )
    def on_stop(self):
        if self.is_logging:
            self.stop_logging()

    def stop_logging(self):
        self.is_logging = False
        self.update_file_name_prefix()
        self.stop_logging_thread()
        self.close_csv_file()
        self.close_serial_port(self.serial_port)

    def start_logging(self):
        self.is_logging = True
        self.open_serial_port()
        self.open_csv_file()
        self.create_logging_thread()

    def btn_logging_released(self, instance):
        if self.is_logging:
            self.stop_logging()
        else:
            self.start_logging()
        
    def serial_reader(self):
        self.count = 0
        while not self.stop_thread:
            if self.serial_port:
                data = self.serial_port.readline().decode('utf-8').strip()
                if data:
                    self.count += 1

                    now = datetime.now()
                    date = now.strftime("%Y-%m-%d")
                    time = now.strftime("%H:%M:%S.%f")[:-3]

                    data = [date,time] +  data.split(",")
                    
                    self.csv_writer.writerow(data)
                    if self.count%10 == 0:
                        self.csv_file.flush()


if __name__ == "__main__":
    COMLoggerApp().run()
