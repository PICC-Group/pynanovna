from .Serial import Interface
from .VNA import VNA


class AVNA(VNA):
    name = "AVNA"

    def __init__(self, iface: Interface):
        super().__init__(iface)
        self.sweep_max_freq_Hz = 40e3
        self.features.add("Customizable data points")

    def isValid(self):
        return True

    def resetSweep(self, start: int, stop: int):
        list(self.exec_command(f"sweep {start} {stop} {self.datapoints}"))
        list(self.exec_command("resume"))

    def setSweep(self, start, stop):
        list(self.exec_command(f"sweep {start} {stop} {self.datapoints}"))
