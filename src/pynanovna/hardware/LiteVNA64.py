import logging
from struct import pack
from time import sleep
from typing import Optional

from serial import Serial

from .NanoVNA_V2 import (
    _ADDR_DEVICE_VARIANT,
    _ADDR_FW_MAJOR,
    _ADDR_FW_MINOR,
    _ADDR_HARDWARE_REVISION,
    _ADDR_RAW_SAMPLES_MODE,
    _ADF4350_TXPOWER_DESC_MAP,
    _CMD_READ,
    _CMD_READ2,
    _CMD_WRITE,
    NanoVNA_V2,
)
from .Serial import drain_serial
from .Version import Version

logger = logging.getLogger(__name__)

_ADDR_VBAT_MILIVOLTS = 0x5C

V2_DEVICE_VARIANT = 2
MIN_FW_VERSION = Version("2.2.0")
WRITE_SLEEP = 0.05
DETECT_TIMEOUT = 2.0


class LiteVNA64(NanoVNA_V2):
    name = "LiteVNA-64"
    valid_datapoints = (
        201,
        51,
        101,
        401,
        801,
        1024,
        1601,
        3201,
        4501,
        6401,
        12801,
        25601,
    )
    screenwidth = 480
    screenheight = 320
    sweep_points_max = 65535

    def read_version(self) -> "Version":
        with self.serial.lock:
            return LiteVNA64._read_version_registers(
                self.serial, _ADDR_FW_MAJOR, _ADDR_FW_MINOR
            )

    def read_features(self):
        self.features.add("Customizable data points")
        self.features.add("Multi data points")
        self.features.add("Set Average")
        self.features.add("Set TX power partial")
        self.sweep_max_freq_Hz = 6300e6
        self.txPowerRanges = [
            (
                (140e6, self.sweep_max_freq_Hz),
                [_ADF4350_TXPOWER_DESC_MAP[value] for value in (3, 2, 1, 0)],
            ),
        ]

    def get_features(self) -> set[str]:
        return self.features | {f"Vbat: {self.read_vbat()}V"}

    def read_vbat(self) -> str:
        with self.serial.lock:
            self.serial.write(pack("<BB", _CMD_READ2, _ADDR_VBAT_MILIVOLTS))
            sleep(self.wait)
            resp = self.serial.read(2)
        if len(resp) != 2:
            logger.warning("Timeout reading battery voltage. Got: %s", resp)
            return "unknown"
        vbat = int.from_bytes(resp, "little") / 1000.0
        logger.debug("Vbat: %sV", vbat)
        return f"{vbat}"

    def read_values(self, value, overwrite_wait: Optional[float] = None) -> list[str]:
        if value == "data 0":
            self._update_sweep()
        result = super().read_values(value, overwrite_wait)
        self._exit_usb_mode()
        return result

    def set_sweep(self, start, stop):
        self.sweep_start_Hz = start
        self.sweep_step_Hz = (stop - start) / (self.datapoints - 1)
        logger.debug(
            "LiteVNA64: set sweep start %d step %d",
            self.sweep_start_Hz,
            self.sweep_step_Hz,
        )
        self._update_sweep()

    def disconnect(self):
        if self.connected():
            self._exit_usb_mode()
        super().disconnect()

    def _exit_usb_mode(self):
        with self.serial.lock:
            self.serial.write(pack("<BBB", _CMD_WRITE, _ADDR_RAW_SAMPLES_MODE, 2))
            sleep(self.wait)

    @staticmethod
    def _read_version_registers(
        serial: Serial, addr_major: int, addr_minor: int
    ) -> "Version":
        serial.write(pack("<BBBB", _CMD_READ, addr_major, _CMD_READ, addr_minor))
        sleep(WRITE_SLEEP)
        resp = serial.read(2)
        if len(resp) != 2:
            logger.error("Timeout reading version registers. Got: %s", resp)
            raise IOError("Timeout reading version registers")
        return Version(f"{resp[0]}.{resp[1]}.0")

    @staticmethod
    def is_lite_vna_64(serial: Serial) -> bool:
        timeout = serial.timeout
        serial.timeout = DETECT_TIMEOUT
        try:
            hw_version = LiteVNA64._read_version_registers(
                serial, _ADDR_DEVICE_VARIANT, _ADDR_HARDWARE_REVISION
            )
            fw_version = LiteVNA64._read_version_registers(
                serial, _ADDR_FW_MAJOR, _ADDR_FW_MINOR
            )
        except IOError:
            logger.warning("Could not read V2 version registers, assuming NanoVNA V2.")
            return False
        finally:
            serial.timeout = timeout
            drain_serial(serial)
        logger.debug("V2 device: hardware %s, firmware %s", hw_version, fw_version)
        return hw_version.major == V2_DEVICE_VARIANT and fw_version >= MIN_FW_VERSION
