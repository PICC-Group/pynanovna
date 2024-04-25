from .NanoVNA import NanoVNA
from .Serial import Interface


class SV4401A(NanoVNA):
    name = "SV4401A"
    screenwidth = 1024
    screenheight = 600
    valid_datapoints = (501, 101, 1001)
    sweep_points_min = 101
    sweep_points_max = 1001

    def __init__(self, iface: Interface):
        super().__init__(iface)
        self.sweep_max_freq_Hz = 4.4e9

    def setSweep(self, start, stop):
        self.start = start
        self.stop = stop
        list(self.exec_command(f"scan {start} {stop} {self.datapoints}"))
