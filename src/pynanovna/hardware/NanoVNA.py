import logging
import struct

import numpy as np

from .Serial import drain_serial, Interface
from .VNABase import VNABase
from .Version import Version

logger = logging.getLogger(__name__)


class NanoVNA(VNABase):
    name = "NanoVNA"
    screenwidth = 320
    screenheight = 240

    def __init__(self, iface: Interface):
        super().__init__(iface)
        self.sweep_method = "sweep"
        self.read_features()
        logger.debug("Setting initial start,stop")
        self.start, self.stop = self._get_running_frequencies()
        self.sweep_max_freq_Hz = 300e6
        self._sweepdata = []

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
        list(self.exec_command(f"sweep {start} {stop} {self.datapoints}"))
        list(self.exec_command("resume"))

    def set_sweep(self, start, stop):
        self.start = start
        self.stop = stop
        if self.sweep_method == "sweep":
            list(self.exec_command(f"sweep {start} {stop} {self.datapoints}"))
        elif self.sweep_method == "scan":
            list(self.exec_command(f"scan {start} {stop} {self.datapoints}"))

    def read_features(self):
        super().read_features()
        if self.version >= Version("0.7.1"):
            logger.debug("Using scan mask command.")
            self.features.add("Scan mask command")
            self.sweep_method = "scan_mask"
        elif self.version >= Version("0.2.0"):
            logger.debug("Using new scan command.")
            self.features.add("Scan command")
            self.sweep_method = "scan"

    def read_frequencies(self) -> list[int]:
        logger.debug("readFrequencies: %s", self.sweep_method)
        if self.sweep_method != "scan_mask":
            return super().read_frequencies()
        return [
            int(line)
            for line in self.exec_command(
                f"scan {self.start} {self.stop} {self.datapoints} 0b001"
            )
        ]

    def read_values(self, value, overwrite_wait: float = 0.0) -> list[str]:
        if self.sweep_method != "scan_mask":
            return super().read_values(value)
        logger.debug("readValue with scan mask (%s)", value)
        # Actually grab the data only when requesting channel 0.
        # The hardware will return all channels which we will store.
        if value == "data 0":
            self._sweepdata = []
            for line in self.exec_command(
                f"scan {self.start} {self.stop} {self.datapoints} 0b110",
                min(self.wait, overwrite_wait),
            ):
                data = line.split()
                self._sweepdata.append((f"{data[0]} {data[1]}", f"{data[2]} {data[3]}"))
        if value == "data 0":
            return [x[0] for x in self._sweepdata]
        if value == "data 1":
            return [x[1] for x in self._sweepdata]
