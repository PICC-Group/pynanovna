import logging
import struct

import numpy as np

from .Serial import drain_serial, Interface
from .VNABase import VNABase

logger = logging.getLogger(__name__)


class TinySA(VNABase):
    name = "tinySA"
    screenwidth = 320
    screenheight = 240
    valid_datapoints = (290,)

    def __init__(self, iface: Interface):
        super().__init__(iface)
        self.features = {"Screenshots"}
        logger.debug("Setting initial start,stop")
        self.start, self.stop = self._get_running_frequencies()
        self.sweep_max_freq_Hz = 950e6
        self._sweepdata = []
        self.validateInput = False

    def _get_running_frequencies(self):
        logger.debug("Reading values: frequencies")
        try:
            frequencies = super().read_values("frequencies")
            return frequencies[0], frequencies[-1]
        except Exception as e:
            logger.warning("%s reading frequencies", e)
            logger.info("falling back to generic")

        return VNABase._get_running_frequencies(self)

    def _capture_data(self) -> bytes:
        timeout = self.serial.timeout
        with self.serial.lock:
            drain_serial(self.serial)
            self.serial.write("capture\r".encode("ascii"))
            self.serial.readline()
            self.serial.timeout = 4
            image_data = self.serial.read(self.screenwidth * self.screenheight * 2)
            self.serial.timeout = timeout
        self.serial.timeout = timeout
        return image_data

    def _convert_data(self, image_data: bytes) -> bytes:
        rgb_data = struct.unpack(
            f">{self.screenwidth * self.screenheight}H", image_data
        )
        rgb_array = np.array(rgb_data, dtype=np.uint32)
        return (
            0xFF000000
            + ((rgb_array & 0xF800) << 8)
            + ((rgb_array & 0x07E0) << 5)
            + ((rgb_array & 0x001F) << 3)
        )

    def reset_sweep(self, start: int, stop: int):
        return

    def set_sweep(self, start, stop):
        self.start = start
        self.stop = stop
        list(self.exec_command(f"sweep {start} {stop} {self.datapoints}"))
        list(self.exec_command("trigger auto"))

    def read_frequencies(self) -> list[int]:
        logger.debug("readFrequencies")
        return [int(line) for line in self.exec_command("frequencies")]

    def read_values(self, value, overwrite_wait: float = 0.0) -> list[str]:
        def conv2float(data: str) -> float:
            try:
                return 10 ** (float(data.strip()) / 20)
            except ValueError:
                return 0.0

        logger.debug("Read: %s", value)
        if value == "data 0":
            self._sweepdata = [
                f"{conv2float(line)} 0.0"
                for line in self.exec_command("data 0", min(self.wait, overwrite_wait))
            ]
        return self._sweepdata


class TinySA_Ultra(TinySA):
    name = "tinySA Ultra"
    screenwidth = 480
    screenheight = 320
    valid_datapoints = (450, 51, 101, 145, 290)

    def __init__(self, iface: Interface):
        super().__init__(iface)
        self.features = {"Screenshots", "Customizable data points"}
        logger.debug("Setting initial start,stop")
        self.start, self.stop = self._get_running_frequencies()
        self.sweep_max_freq_Hz = 5.4e9
        self._sweepdata = []
        self.validateInput = False
