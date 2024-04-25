from .NanoVNA import NanoVNA
from .Serial import Interface


class NanoVNA_F(NanoVNA):
    name = "NanoVNA-F"
    screenwidth = 800
    screenheight = 480

    def __init__(self, iface: Interface):
        super().__init__(iface)
        self.sweep_max_freq_Hz = 1500e6
