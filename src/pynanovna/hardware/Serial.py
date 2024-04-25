from threading import Lock
import serial


def drain_serial(serial_port: serial.Serial):
    """drain up to 64k outstanding data in the serial incoming buffer"""
    # logger.debug("Draining: %s", serial_port)
    timeout = serial_port.timeout
    serial_port.timeout = 0.05
    for _ in range(512):
        cnt = len(serial_port.read(128))
        if not cnt:
            serial_port.timeout = timeout
            return
    serial_port.timeout = timeout
    print("Warning: Unable to drain all data")


class Interface(serial.Serial):
    def __init__(self, interface_type: str, comment, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert interface_type in {"serial", "usb", "bt", "network"}
        self.type = interface_type
        self.comment = comment
        self.port = None
        self.baudrate = 115200
        self.timeout = 0.05
        self.lock = Lock()

    def __str__(self):
        return f"{self.port} ({self.comment})"
