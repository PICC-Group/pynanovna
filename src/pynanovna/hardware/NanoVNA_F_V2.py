import logging

from .NanoVNA import NanoVNA
from .Serial import Interface
from .Version import Version

logger = logging.getLogger(__name__)


class NanoVNA_F_V2(NanoVNA):
    name = "NanoVNA-F_V2"
    screenwidth = 800
    screenheight = 480
    valid_datapoints = (101, 11, 51, 201, 301)
    sweep_points_min = 11
    sweep_points_max = 301

    def __init__(self, iface: Interface):
        super().__init__(iface)
        self.sweep_max_freq_Hz = 3e9
        if self.version < Version("0.2.0"):
            self.valid_datapoints = (101, 11, 51)
            self.sweep_points_max = 101
        elif self.version < Version("0.5.0"):
            self.valid_datapoints = (101, 11, 51, 201)
            self.sweep_points_max = 201
