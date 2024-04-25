from time import sleep
from typing import Iterator

from .Version import Version
from .Serial import Interface, drain_serial

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
WAIT = 0.05


def _max_retries(bandwidth: int, datapoints: int) -> int:
    return round(
        20 + 20 * (datapoints / 101) + (1000 / bandwidth) ** 1.30 * (datapoints / 101)
    )


class VNA:
    name = "VNA"
    valid_datapoints = (101, 51, 11)
    wait = 0.05
    SN = "NOT SUPPORTED"
    sweep_points_max = 101
    sweep_points_min = 11

    def __init__(self, iface: Interface, verbose=False):
        self.serial = iface
        self.version = Version("0.0.0")
        self.features = set()
        self.validateInput = False
        self.datapoints = self.valid_datapoints[0]
        self.bandwidth = 1000
        self.bw_method = "ttrftech"
        self.sweep_max_freq_Hz = None
        self.verbose = verbose
        # [((min_freq, max_freq), [description]]. Order by increasing
        # frequency. Put default output power first.
        self.txPowerRanges = []
        if self.connected():
            self.version = self.readVersion()
            self.read_features()
            if self.verbose:
                print("Features: %s", self.features)
            #  cannot read current bandwidth, so set to highest
            #  to get initial sweep fast
            if "Bandwidth" in self.features:
                self.set_bandwidth(self.get_bandwidths()[-1])

    def connect(self):
        if self.verbose:
            print("connect %s", self.serial)
        with self.serial.lock:
            self.serial.open()

    def disconnect(self):
        if self.verbose:
            print("disconnect %s", self.serial)
        with self.serial.lock:
            self.serial.close()

    def reconnect(self):
        self.disconnect()
        sleep(WAIT)
        self.connect()
        sleep(WAIT)

    def exec_command(self, command: str, wait: float = WAIT) -> Iterator[str]:
        if self.verbose:
            print("exec_command(%s)", command)
        with self.serial.lock:
            drain_serial(self.serial)
            self.serial.write(f"{command}\r".encode("ascii"))
            sleep(wait)
            retries = 0
            max_retries = _max_retries(self.bandwidth, self.datapoints)
            if self.verbose:
                print("Max retries: %s", max_retries)
            while True:
                line = self.serial.readline()
                line = line.decode("ascii").strip()
                if not line:
                    retries += 1
                    if retries > max_retries:
                        raise IOError("too many retries")
                    sleep(wait)
                    continue
                if line == command:  # suppress echo
                    continue
                if line.startswith("ch>"):
                    if self.verbose:
                        print("Needed retries: %s", retries)
                    break
                yield line

    def read_features(self):
        result = " ".join(self.exec_command("help")).split()
        if self.verbose:
            print("result:\n%s", result)
        if "capture" in result:
            self.features.add("Screenshots")
        if "sn:" in result:
            self.features.add("SN")
            self.SN = self.getSerialNumber()
        if "bandwidth" in result:
            self.features.add("Bandwidth")
            result = " ".join(list(self.exec_command("bandwidth")))
            if "Hz)" in result:
                self.bw_method = "dislord"
        if len(self.valid_datapoints) > 1:
            self.features.add("Customizable data points")

    def get_bandwidths(self) -> list[int]:
        if self.verbose:
            print("get bandwidths")
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

    def readFrequencies(self) -> list[int]:
        return [int(f) for f in self.readValues("frequencies")]

    def resetSweep(self, start: int, stop: int):
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

    def getFeatures(self) -> set[str]:
        return self.features

    def getCalibration(self) -> str:
        return " ".join(list(self.exec_command("cal")))

    def flushSerialBuffers(self):
        if not self.connected():
            return
        with self.serial.lock:
            self.serial.write("\r\n\r\n".encode("ascii"))
            sleep(0.1)
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            sleep(0.1)

    def readFirmware(self) -> str:
        result = "\n".join(list(self.exec_command("info")))
        if self.verbose:
            print("result:\n%s", result)
        return result

    def readValues(self, value) -> list[str]:
        if self.verbose:
            print("VNA reading %s", value)
        result = list(self.exec_command(value))
        if self.verbose:
            print("VNA done reading %s (%d values)", value, len(result))
        return result

    def readVersion(self) -> "Version":
        result = list(self.exec_command("version"))
        if self.verbose:
            print("result:\n%s", result)
        return Version(result[0])

    def setSweep(self, start, stop):
        list(self.exec_command(f"sweep {start} {stop} {self.datapoints}"))

    def setTXPower(self, freq_range, power_desc):
        raise NotImplementedError()

    def getSerialNumber(self) -> str:
        return " ".join(list(self.exec_command("sn")))
