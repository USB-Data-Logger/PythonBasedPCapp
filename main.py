from datetime import datetime
import csv
import threading
import serial
from kivy.app import App
from kivy.properties import BooleanProperty, NumericProperty



class SerialCommunicator:
    def __init__(self):
        self.serial_port = None
        self.stop_thread = False

    def open_serial_port(self, port, baudrate):
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=1)
        except serial.SerialException as e:
            raise RuntimeError(f"Error opening serial port: {e}")

    def close_serial_port(self):
        if self.serial_port:
            self.serial_port.close()

    def read_line(self):
        if self.serial_port:
            return self.serial_port.readline().decode("utf-8").strip()
        return ""


class COMLoggerApp(App):
    is_logging = BooleanProperty(False)
    count = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.serial_communicator = SerialCommunicator()
        self.file_name_template = "%Y_%m_%d_%H.%M.%S.%f"

    def update_file_name_prefix(self):
        self.root.ids.lbl_file_prefix.text = (
            self.filename_from_template(self.file_name_template) + "-"
        )

    def on_start(self):
        self.update_file_name_prefix()

    def filename_from_template(self, template):
        current_time = datetime.now()
        return current_time.strftime(template)[:-3]

    def drop_ports_text_changed(self, instance):
        if instance.values:
            self.root.ids.btn_logging.disabled = False
        else:
            self.root.ids.btn_logging.disabled = True

    def txt_custom_port_on_text(self, instance):
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
        self.serial_communicator.stop_thread = True
        self.serial_thread.join()

    def close_csv_file(self):
        self.csv_file.flush()
        self.csv_file.close()

    def open_csv_file(self):
        self.csv_file = open(self.root.ids.lbl_filename.text, "w")
        self.csv_writer = csv.writer(self.csv_file)

    def open_serial_port(self):
        if self.root.ids.chk_custom_port.active:
            self.serial_communicator.open_serial_port(
                self.root.ids.txt_custom_port.text, self.root.ids.baudrate_spinner.text
            )
        else:
            self.serial_communicator.open_serial_port(
                self.root.ids.port_spinner.text, self.root.ids.baudrate_spinner.text
            )

    def on_stop(self):
        if self.is_logging:
            self.stop_logging()

    def stop_logging(self):
        self.is_logging = False
        self.update_file_name_prefix()
        self.stop_logging_thread()
        self.close_csv_file()
        self.serial_communicator.close_serial_port()

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

    def create_logging_thread(self):
        self.serial_communicator.stop_thread = False
        self.serial_thread = threading.Thread(target=self.serial_reader)
        self.serial_thread.start()

    def get_formated_date_time(self):
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S.%f")[:-3]
        return [date,time]


    def serial_reader(self):
        self.count = 0
        while not self.serial_communicator.stop_thread:
            line = self.serial_communicator.read_line()
            if line:
                self.count += 1

                data = self.get_formated_date_time()
                data.extend( line.split(","))

                self.csv_writer.writerow(data)
                if self.count % 10 == 0:
                    self.csv_file.flush()


if __name__ == "__main__":
    COMLoggerApp().run()
