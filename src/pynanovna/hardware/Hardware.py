import logging
import platform
from collections import namedtuple
from time import sleep

import serial
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

from .VNABase import VNABase
from .AVNA import AVNA
from .NanoVNA import NanoVNA
from .NanoVNA_F import NanoVNA_F
from .NanoVNA_F_V2 import NanoVNA_F_V2
from .NanoVNA_H import NanoVNA_H
from .NanoVNA_H4 import NanoVNA_H4
from .NanoVNA_V2 import NanoVNA_V2
from .TinySA import TinySA, TinySA_Ultra
from .JNCRadio_VNA_3G import JNCRadio_VNA_3G
from .SV4401A import SV4401A
from .SV6301A import SV6301A
from .Serial import drain_serial, Interface

logger = logging.getLogger(__name__)

USBDevice = namedtuple("Device", "vid pid name")

USBDEVICETYPES = (
    USBDevice(0x0483, 0x5740, "NanoVNA"),
    USBDevice(0x16C0, 0x0483, "AVNA"),
    USBDevice(0x04B4, 0x0008, "S-A-A-2"),
)
RETRIES = 3
TIMEOUT = 0.2

NAME2DEVICE = {
    "S-A-A-2": NanoVNA_V2,
    "AVNA": AVNA,
    "H4": NanoVNA_H4,
    "H": NanoVNA_H,
    "F_V2": NanoVNA_F_V2,
    "F": NanoVNA_F,
    "NanoVNA": NanoVNA,
    "tinySA": TinySA,
    "tinySA_Ultra": TinySA_Ultra,
    "JNCRadio": JNCRadio_VNA_3G,
    "SV4401A": SV4401A,
    "SV6301A": SV6301A,
    "Unknown": NanoVNA,
}


def _fix_v2_hwinfo(device):
    """The USB Driver for NanoVNA V2 seems to deliver an incompatible
        hardware info like: 'PORTS\\VID_04B4&PID_0008\\DEMO'.
        This function will fix it.

    Args:
        device (serial.tools.list_ports.ListPortInfo): Serial portinfo object.

    Returns:
        serial.tools.list_ports.ListPortInfo: Modified serial portinfo object.
    """
    hwid = device.hwid
    vid_index = hwid.find("VID_")
    if vid_index != -1:
        device.vid = int(hwid[vid_index + 4 : vid_index + 8], 16)
    pid_index = hwid.find("PID_")
    if pid_index != -1:
        device.pid = int(hwid[pid_index + 4 : pid_index + 8], 16)
    return device


def usb_typename(device: ListPortInfo) -> str:
    return next(
        (t.name for t in USBDEVICETYPES if device.vid == t.vid and device.pid == t.pid),
        "",
    )


def get_interfaces() -> list[Interface]:
    """Get list of interfaces with VNAs connected.

    Returns:
        list[Interface]: List of different serial interfaces.
    """
    interfaces = []
    for d in list_ports.comports():
        if platform.system() == "Windows" and d.vid is None:
            d = _fix_v2_hwinfo(d)
        if not (typename := usb_typename(d)):
            continue
        logger.debug(
            "Found %s USB:(%04x:%04x) on port %s",
            typename,
            d.vid,
            d.pid,
            d.device,
        )
        iface = Interface("serial", typename)
        iface.port = d.device
        interfaces.append(iface)

    logger.debug("Interfaces: %s", interfaces)
    return interfaces


def get_VNA(iface: Interface) -> VNABase:
    # serial_port.timeout = TIMEOUT
    try:
        return NAME2DEVICE[get_comment(iface)](iface)
    except Exception as e:
        logger.critical("Could not get VNA device from serial interface. Error: %s", e)
        return None


def get_comment(iface: Interface) -> str:
    logger.debug("Finding correct VNA type...")
    with iface.lock:
        vna_version = detect_version(iface)

    if vna_version == "v2":
        return "S-A-A-2"

    logger.info("Finding firmware variant...")
    info = get_info(iface)
    for search, name in (
        ("AVNA + Teensy", "AVNA"),
        ("NanoVNA-H 4", "H4"),
        ("NanoVNA-H", "H"),
        ("NanoVNA-F_V2", "F_V2"),
        ("NanoVNA-F", "F"),
        ("NanoVNA", "NanoVNA"),
        ("tinySA4", "tinySA_Ultra"),
        ("tinySA", "tinySA"),
        ("JNCRadio_VNA_3G", "JNCRadio"),
        ("SV4401A", "SV4401A"),
        ("SV6301A", "SV6301A"),
    ):
        if info.find(search) >= 0:
            return name
    logger.warning("Did not recognize NanoVNA type from firmware.")
    return "Unknown"


def detect_version(serial_port: serial.Serial, wait: float = 0.05) -> str:
    data = ""
    for i in range(RETRIES):
        drain_serial(serial_port)
        serial_port.write("\r".encode("ascii"))
        # workaround for some UnicodeDecodeError ... repeat ;-)
        drain_serial(serial_port)
        serial_port.write("\r".encode("ascii"))
        sleep(wait)

        data = serial_port.read(128).decode("ascii")
        if data.startswith("ch> "):
            return "v1"
        # -H versions
        if data.startswith("\r\nch> "):
            return "vh"
        if data.startswith("\r\n?\r\nch> "):
            return "vh"
        if data.startswith("2"):
            return "v2"
        logger.debug("Retry detection: %s", i + 1)
    logger.error("No VNA detected. Hardware responded to CR with: %s", data)
    return ""


def get_info(serial_port: serial.Serial, wait: float = 0.05) -> str:
    for _ in range(RETRIES):
        drain_serial(serial_port)
        serial_port.write("info\r".encode("ascii"))
        lines = []
        retries = 0
        while True:
            line = serial_port.readline()
            line = line.decode("ascii").strip()
            if not line:
                retries += 1
                if retries > RETRIES:
                    return ""
                sleep(wait)
                continue
            if line == "info":  # suppress echo
                continue
            if line.startswith("ch>"):
                logger.debug("Needed retries: %s", retries)
                break
            lines.append(line)
        logger.debug("Info output: %s", lines)
        return "\n".join(lines)


def get_portinfos() -> list[str]:
    logger.critical(
        "The get_portinfos() function is deprecated and will be removed in the next major update (v2.0). Please use get_interfaces() and detect_version() functions instead."
    )
    portinfos = []
    for d in list_ports.comports():
        logger.debug("Found USB:(%04x:%04x) on port %s", d.vid, d.pid, d.device)
        iface = Interface("serial", "DEBUG")
        iface.port = d.device
        iface.open()
        version = detect_version(iface)
        iface.close()
        portinfos.append(version)
    return portinfos
