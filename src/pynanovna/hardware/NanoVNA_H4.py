from .Serial import Interface
from .NanoVNA_H import NanoVNA_H


class NanoVNA_H4(NanoVNA_H):
    name = "NanoVNA-H4"
    screenwidth = 480
    screenheight = 320
    valid_datapoints = (101, 11, 51, 201, 401)

    def __init__(self, iface: Interface):
        super().__init__(iface)
        self.sweep_max_freq_Hz = 1500e6
        self.sweep_method = "scan"
        if "Scan mask command" in self.features:
            self.sweep_method = "scan_mask"
