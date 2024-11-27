import logging
from time import sleep
from typing import Iterator

from .Version import Version
from .Serial import Interface, drain_serial

logger = logging.getLogger(__name__)

DISLORD_BW = {
    10: 363,
    33: 117,
    50: 78,
    100: 39,
    200: 19,
    250: 15,
    333: 11,
    500: 7,
    1000: 3,
    2000: 1,
    4000: 0,
}


def _max_retries(bandwidth: int, datapoints: int) -> int:
    return round(
        20 + 20 * (datapoints / 101) + (1000 / bandwidth) ** 1.30 * (datapoints / 101)
    )


class VNABase:
    name = "VNA"
    valid_datapoints = (101, 51, 11)
    SN = "NOT SUPPORTED"
    sweep_points_max = 101
    sweep_points_min = 11

    def __init__(self, iface: Interface):
        self.serial = iface
        self.version = Version("0.0.0")
        self.features = set()
        self.validate_input = False
        self.datapoints = self.valid_datapoints[0]
        self.bandwidth = 1000
        self.bw_method = "ttrftech"
        self.sweep_max_freq_Hz = None
        # [((min_freq, max_freq), [description]]. Order by increasing
        # frequency. Put default output power first.
        self.txPowerRanges = []
        self.wait = 0.05
        if self.connected():
            self.version = self.read_version()
            self.read_features()
            logger.debug("Features: %s", self.features)
            #  cannot read current bandwidth, so set to highest
            #  to get initial sweep fast
            if "Bandwidth" in self.features:
                self.set_bandwidth(self.get_bandwidths()[-1])

    def connect(self):
        logger.info("connect %s", self.serial)
        with self.serial.lock:
            self.serial.open()

    def disconnect(self):
        logger.info("disconnect %s", self.serial)
        with self.serial.lock:
            self.serial.close()

    def reconnect(self):
        self.disconnect()
        sleep(self.wait)
        self.connect()
        sleep(self.wait)

    def exec_command(self, command: str, overwrite_wait: float = 0.0) -> Iterator[str]:
        logger.debug("exec_command(%s)", command)
        with self.serial.lock:
            drain_serial(self.serial)
            self.serial.write(f"{command}\r".encode("ascii"))
            sleep(min(self.wait, overwrite_wait))
            retries = 0
            max_retries = _max_retries(self.bandwidth, self.datapoints)
            logger.debug("Max retries: %s", max_retries)
            while True:
                line = self.serial.readline()
                line = line.decode("ascii").strip()
                if not line:
                    retries += 1
                    if retries > max_retries:
                        raise IOError("too many retries")
                    sleep(min(self.wait, overwrite_wait))
                    continue
                if line == command:  # suppress echo
                    continue
                if line.startswith("ch>"):
                    logger.debug("Needed retries: %s", retries)
                    break
                yield line

    def read_features(self):
        result = " ".join(self.exec_command("help")).split()
        logger.debug("result:\n%s", result)
        if "sn:" in result:
            self.features.add("SN")
            self.SN = self.get_serial_number()
        if "bandwidth" in result:
            self.features.add("Bandwidth")
            result = " ".join(list(self.exec_command("bandwidth")))
            if "Hz)" in result:
                self.bw_method = "dislord"
        if len(self.valid_datapoints) > 1:
            self.features.add("Customizable data points")

    def get_bandwidths(self) -> list[int]:
        logger.debug("get bandwidths")
        if self.bw_method == "dislord":
            return list(DISLORD_BW.keys())
        result = " ".join(list(self.exec_command("bandwidth")))
        try:
            result = result.split(" {")[1].strip("}")
            return sorted([int(i) for i in result.split("|")])
        except IndexError:
            return [
                1000,
            ]

    def set_bandwidth(self, bandwidth: int):
        bw_val = DISLORD_BW[bandwidth] if self.bw_method == "dislord" else bandwidth
        result = " ".join(self.exec_command(f"bandwidth {bw_val}"))
        if self.bw_method == "ttrftech" and result:
            raise IOError(f"set_bandwith({bandwidth}: {result}")
        self.bandwidth = bandwidth

    def read_frequencies(self) -> list[int]:
        return [int(f) for f in self.read_values("frequencies")]

    def reset_sweep(self, start: int, stop: int):
        pass

    def _get_running_frequencies(self):
        """
        If possible, read frequencies already running
        if not return default values
        Overwrite in specific HW
        """
        return 27000000, 30000000

    def connected(self) -> bool:
        return self.serial.is_open

    def get_features(self) -> set[str]:
        return self.features

    def get_calibration(self) -> str:
        return " ".join(list(self.exec_command("cal")))

    def flush_serial_buffers(self):
        if not self.connected():
            return
        with self.serial.lock:
            self.serial.write("\r\n\r\n".encode("ascii"))
            sleep(0.1)
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            sleep(0.1)

    def read_firmware(self) -> str:
        result = "\n".join(list(self.exec_command("info")))
        logger.debug("result:\n%s", result)
        return result

    def read_values(self, value, overwrite_wait: float = 0.0) -> list[str]:
        logger.debug("VNA reading %s", value)
        result = list(self.exec_command(value, min(self.wait, overwrite_wait)))
        logger.debug("VNA done reading %s (%d values)", value, len(result))
        return result

    def read_version(self) -> "Version":
        result = list(self.exec_command("version"))
        logger.debug("result:\n%s", result)
        return Version(result[0])

    def set_sweep(self, start, stop):
        list(self.exec_command(f"sweep {start} {stop} {self.datapoints}"))

    def set_TX_power(self, freq_range, power_desc):
        raise NotImplementedError()

    def get_serial_number(self) -> str:
        return " ".join(list(self.exec_command("sn")))

    def set_wait(self, new_wait: float):
        if new_wait < 0.05:
            logger.critical(
                "Wait is set to lower than the standard 0.05 seconds, this might cause problems with the serial communication depending on how low it is set and what system you operate."
            )
        self.wait = new_wait
