from serial.tools import list_ports


def get_com_ports():
    com_ports = []
    for i in list_ports.comports():
        com_ports.append(i.device)
    return com_ports


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

def get_file_name_template():
    templates = [
            "%Y-%m-%d_%H-%M-%S",
            "%d-%m-%Y_%H-%M-%S",
            "%d-%B-%Y_%H-%M-%S"]
    return templates
