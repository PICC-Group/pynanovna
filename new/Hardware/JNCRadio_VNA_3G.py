import logging

from .NanoVNA import NanoVNA
from .Serial import Interface

logger = logging.getLogger(__name__)


class JNCRadio_VNA_3G(NanoVNA):
    name = "JNCRadio_VNA_3G"
    screenwidth = 800
    screenheight = 480
    valid_datapoints = (501, 11, 101, 1001)
    sweep_points_min = 11
    sweep_points_max = 1001

    def __init__(self, iface: Interface):
        super().__init__(iface)
        self.sweep_max_freq_Hz = 3e9

    def set_sweep(self, start, stop):
        self.start = start
        self.stop = stop
        list(self.exec_command(f"scan {start} {stop} {self.datapoints}"))
