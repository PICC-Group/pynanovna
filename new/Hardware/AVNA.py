import logging

from .Serial import Interface
from .VNABase import VNABase

logger = logging.getLogger(__name__)


class AVNA(VNABase):
    name = "AVNA"

    def __init__(self, iface: Interface):
        super().__init__(iface)
        self.sweep_max_freq_Hz = 40e3
        self.features.add("Customizable data points")

    def is_valid(self):
        return True

    def reset_sweep(self, start: int, stop: int):
        list(self.exec_command(f"sweep {start} {stop} {self.datapoints}"))
        list(self.exec_command("resume"))

    def set_sweep(self, start, stop):
        list(self.exec_command(f"sweep {start} {stop} {self.datapoints}"))
