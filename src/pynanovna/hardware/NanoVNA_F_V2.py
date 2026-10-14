import logging

from .NanoVNA import NanoVNA
from .Serial import Interface

logger = logging.getLogger(__name__)


class NanoVNA_F_V2(NanoVNA):
    name = "NanoVNA-F_V2"
    screenwidth = 800
    screenheight = 480
    valid_datapoints = (201, 11, 51, 101)

    def __init__(self, iface: Interface):
        super().__init__(iface)
        self.sweep_max_freq_Hz = 3e9
