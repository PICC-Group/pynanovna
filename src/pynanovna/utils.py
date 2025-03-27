"""
Utility functions for pynanovna.
"""

import logging
import time
import numpy as np
from .hardware import Hardware as hw


def stream_from_csv(
    filename: str, sweepdivider: str = "sweepnumber: ", delay: float = 0.1
) -> tuple[list[complex], list[complex], list[int]]:
    """Stream previously recorded data from a csv file.

    Args:
        filename (string): Path to the csv file.
        sweepdivider (string): Used to identify where sweeps end and start in the csv file.
        delay (float): Used to simulate the time it takes for the vna to sweep.

    Yields:
        tuple: (s11, s21, frequencies)
    """
    try:
        with open(filename) as f:
            data = f.readlines()
            package = (
                np.array([], dtype=np.complex128),
                np.array([], dtype=np.complex128),
                np.array([], dtype=np.int32),
            )
            for i, line in enumerate(data):
                if i != 0:
                    if sweepdivider in line:
                        if package[0].size > 0:
                            time.sleep(delay)
                            yield package
                        package = (
                            np.array([], dtype=np.complex128),
                            np.array([], dtype=np.complex128),
                            np.array([], dtype=np.int32),
                        )
                        continue
                    data_vals = line.split(",")
                    package = (
                        np.append(package[0], complex(data_vals[0])),
                        np.append(package[1], complex(data_vals[1])),
                        np.append(package[2], int(data_vals[-1])),
                    )

    except KeyboardInterrupt:
        logging.info("Killing csv stream because of keyboard interrupt.")
        return
    except Exception as e:
        logging.critical("Exception when streaming from csv file.", exc_info=e)
        return


def get_interfaces() -> object:
    """Get all available interfaces.

    Returns:
        list: Interface
    """
    return hw.get_interfaces()


def get_portinfos() -> list[str]:
    """This function is DEPRECATED and will be removed in v2.0.
        Get information about communication ports.
    Returns:
        list: Port information.
    """
    return hw.get_portinfos()
