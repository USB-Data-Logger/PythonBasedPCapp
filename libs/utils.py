from serial.tools import list_ports


def get_com_ports():
    return [port.device for port in list_ports.comports()]


def get_standard_baud_rate():
    standard_baud_rate = (
        "110",
        "300",
        "600",
        "1200",
        "2400",
        "4800",
        "9600",
        "14400",
        "19200",
        "38400",
        "57600",
        "115200",
        "128000",
        "256000",
    )
    return standard_baud_rate


