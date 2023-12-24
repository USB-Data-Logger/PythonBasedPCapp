import serial


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
