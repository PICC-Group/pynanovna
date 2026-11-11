import logging

from .NanoVNA import NanoVNA
from .Serial import Interface

logger = logging.getLogger(__name__)


class NanoVNA_F_V3(NanoVNA):
    name = "NanoVNA-F_V3"
    screenwidth = 800
    screenheight = 480
    valid_datapoints = (101, 11, 51, 201, 301, 401, 501, 601, 701, 801)
    sweep_points_min = 11
    sweep_points_max = 801

    def __init__(self, iface: Interface):
        super().__init__(iface)
        self.sweep_max_freq_Hz = 6.3e9

    def read_features(self):
        super().read_features()
        if "SN:" in " ".join(self.exec_command("help")).split():
            self.features.add("SN")
            self.SN = " ".join(self.exec_command("SN"))
