import logging

from .NanoVNA import NanoVNA
from .Serial import Interface

logger = logging.getLogger(__name__)


class NanoVNA_H(NanoVNA):
    name = "NanoVNA-H"

    def __init__(self, iface: Interface):
        super().__init__(iface)
        self.sweep_max_freq_Hz = 1500e6
