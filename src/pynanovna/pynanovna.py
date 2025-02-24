"""
Main module for the pynanovna package.
"""

from .hardware import Hardware as hw
from .calibration import calibration

import logging
import numpy as np
import csv


class VNA:
    def __init__(self, vna_index: int = 0, logging_level: str = "info"):
        """Initialize a VNA object for the NanoVNA.

        Args:
            vna_index (int): If multiple NanoVNAs are connected you can specify which to use.
            logging_level (str): The level of outputs. 'critical', 'info' or 'debug'. Defaults to 'info'.
        """
        logging_level = {"debug": logging.DEBUG, "critical": logging.CRITICAL}.get(
            logging_level, logging.INFO
        )
        logging.basicConfig(
            level=logging_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logging.info("Initializing the VNA.")
        try:
            self.iface = hw.get_interfaces()[vna_index]
            self.iface.open()
            self.connected = True
        except IndexError:
            logging.critical("NanoVNA not found, is it connected and turned on?")
            self.connected = False
            return

        self.vna = hw.get_VNA(self.iface)
        self.sweep_interval = (None, None)
        self.sweep_points = None
        self.calibration = calibration.Calibration()
        self.offset_delay = 0
        logging.info("VNA successfully initialized.")

    def set_sweep(self, start: float, stop: float, points: int):
        """Set the sweep parameters.

        Args:
            start (int): The start frequnecy.
            stop (int): The stop frequency.
            points (int): Number of points in the sweep.
        """
        self.vna.datapoints = points
        self.vna.set_sweep(start, stop)
        self.sweep_interval = (start, stop)
        self.sweep_points = points
        logging.debug(
            "Sweep has been set from "
            + str(self.sweep_interval[0] / 1e9)
            + "e9"
            + " to "
            + str(self.sweep_interval[1] / 1e9)
            + "e9, with "
            + str(self.sweep_points)
            + " points."
        )

    def sweep(
        self,
        overwrite_wait: float = 0.05,
    ) -> tuple[list[complex], list[complex], list[int]]:
        """Run a single sweep and return the data.

        Args:
            overwrite_wait: Do not change if you don't know what youre doing.
                            This can be used to lower the wait in the hardware functions.

        Returns:
            tuple: s11, s21, frequencies
        """
        frequencies = np.array(self.vna.read_frequencies())
        data0 = np.array(
            [complex(*map(float, s.split())) for s in self.vna.read_values("data 0")]
        )
        data1 = np.array(
            [complex(*map(float, s.split())) for s in self.vna.read_values("data 1")]
        )
        s11, s21 = self._apply_calibration(data0, data1, frequencies)
        return s11, s21, frequencies

    def stream(
        self,
        overwrite_wait: float = 0.05,
    ) -> tuple[list[complex], list[complex], list[int]]:
        """Creates a data stream from the continuous sweeping.

        Args:
            overwrite_wait: Do not change if you don't know what youre doing.
                            This can be used to lower the wait in the hardware functions.

        Yields:
            tuple: Yields a list of data when new data is available. Each datapoint: (s11, s21, frequencies)
        """
        frequencies = np.array(self.vna.read_frequencies())
        logging.debug("Frequencies read: %d values", len(frequencies))
        logging.debug("Starting stream.")

        while True:
            try:
                raw_data0 = self.vna.read_values("data 0")
                raw_data1 = self.vna.read_values("data 1")

                data0 = np.array(
                    [complex(*map(float, s.split())) for s in raw_data0]
                ).copy()
                data1 = np.array(
                    [complex(*map(float, s.split())) for s in raw_data1]
                ).copy()

                s11, s21 = self._apply_calibration(data0, data1, frequencies)

                yield s11, s21, frequencies

            except KeyboardInterrupt:
                logging.debug("KeyboardInterrupt in stream, killing loop.")
                break
            except Exception as e:
                logging.critical("Exception in data stream: %s", e, exc_info=True)
                break

    def stream_to_csv(
        self,
        filename: str,
        nr_sweeps: int = float("INF"),
        skip_start: int = 5,
        sweepdivider: str = "sweepnumber: ",
    ):
        """Function to save the stream to a csv file.

        Args:
            filename (str): The filename to save to.
            nr_sweeps (int): Number of sweeps to run. Defaults to 10.
            skip_start (int): The NanoVNA usually gives bad data in the beginning, therefore this data can be skipped. Defaults to 5.
            sweepdivider (str): A string to write between every sweep data to divide.

        Raises:
            TypeError: If the filename is not a string.
        """
        try:
            if not isinstance(filename, str):
                raise TypeError("Filename must be a string")
            if not filename.endswith(".csv"):
                filename += ".csv"
            file_path = filename
            counter = 0
            with open(file_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["S11", "S21", "Freq"])
                logging.debug("File created, starting stream.")
                for data in self.stream():
                    if counter - skip_start > nr_sweeps:
                        break
                    writer.writerow([sweepdivider, counter])
                    counter += 1
                    if counter > skip_start:
                        for data_index in range(len(data[0])):
                            writer.writerow(
                                [
                                    data[:][0][data_index],
                                    data[:][1][data_index],
                                    data[:][2][data_index],
                                ]
                            )
        except KeyboardInterrupt:
            logging.debug("KeyboardInterrupt in stream, killing loop.")
            return

        except Exception as e:
            logging.critical("Exception in data stream: ", exc_info=e)

    def calibration_step(self, step: str):
        """Runs a sweep and uses the data for calibration.

        Args:
            step (str): The calibration step.
        """
        if step == "short":
            logging.info(
                "Make sure you set the sweep to the range you intend to measure in BEFORE calibration."
            )
        assert step in ["short", "open", "load", "isolation", "through"]
        s11, s21, frequencies = self.sweep()
        self.calibration.calibration_step(step, s11, s21, frequencies)
        if step == "through":
            logging.debug("Running through step. Here thrurefl is also run.")
            self.calibration.calibration_step("thrurefl", s11, s21, frequencies)
            logging.info(
                "If you have done all the steps correctly, run the calibrate() function to enable the calibration."
            )

    def calibrate(self):
        """Calculates a calibration from the steps.

        Raises:
            Exception: If the calibration is not successfully calculated.
        """
        self.calibration.cal_element.short_is_ideal = True
        self.calibration.cal_element.open_is_ideal = True
        self.calibration.cal_element.load_is_ideal = True
        self.calibration.cal_element.through_is_ideal = True

        try:
            self.calibration.calc_corrections()
            logging.info("Calibration successfully enabled.")
        except ValueError as e:
            raise Exception(
                f"Error applying calibration: {str(e)}\nApplying calibration failed."
            )

    def save_calibration(self, filename: str):
        """Save the current calibration.

        Args:
            filename (str): The filename for the calibration.
        """
        if not self.calibration.isCalculated:
            raise Exception("Cannot save an unapplied calibration state.")
        try:
            self.calibration.save(filename)
            return True
        except Exception as e:
            print("Save failed: ", e)
            return False

    def load_calibration(self, filename: str):
        """Load a previous calibration from a file.

        Args:
            filename (str): The file containing the previous calibration.
        """
        if filename:
            self.calibration.load(filename)
        if not self.calibration.is_valid_1_port():
            raise Exception("Not a valid port.")

        for i, name in enumerate(
            ("short", "open", "load", "through", "isolation", "thrurefl")
        ):
            if i == 2 and not self.calibration.is_valid_2_port():
                break
        self.calibrate()

    def _apply_calibration(
        self,
        raw_s11: list[complex],
        raw_s21: list[complex],
        frequencies: list[int],
    ) -> tuple[list[complex]]:
        """Apply calibration to raw data.

        Args:
            raw_s11 (np.array): s11 data.
            raw_s21 (np.array): s21 data.

        Returns:
            tuple: calibrated s-parameter data.
        """
        s11 = raw_s11.copy()
        s21 = raw_s21.copy()

        is_calculated = self.calibration.isCalculated
        is_valid_1port = self.calibration.is_valid_1_port()
        is_valid_2port = self.calibration.is_valid_2_port()

        if not is_calculated:
            logging.critical(
                "No calibration has been applied, it is strongly recommended to calibrate you NanoVNA."
            )

        if is_calculated and is_valid_1port:
            s11 = [
                self.calibration.correct11(datapoint, frequencies[i])
                for i, datapoint in enumerate(raw_s11)
            ]
        else:
            logging.critical(
                "1 port calibration not valid, it is recommended to re-calibrate."
            )

        if is_valid_2port:
            s21 = [
                self.calibration.correct21(datapoint, raw_s11[i], frequencies[i])
                for i, datapoint in enumerate(raw_s21)
            ]
        else:
            logging.critical(
                "2 port calibration not valid, it is recommended to re-calibrate."
            )

        # Apply offset delay if needed.
        if self.offset_delay != 0:
            s11 = [
                self.calibration.correct_delay(
                    datapoint, frequencies[i], self.offset_delay, reflect=True
                )
                for i, datapoint in enumerate(s11)
            ]
            s21 = [
                self.calibration.correct_delay(
                    datapoint, frequencies[i], self.offset_delay
                )
                for i, datapoint in enumerate(s21)
            ]

        return s11, s21

    def set_offset_delay(self, delay: float):
        """Manually set offset delay. This is used in calibration.

        Args:
            delay (float): The delay.
        """
        self.offset_delay = delay

    def set_vna_wait(self, wait: float):
        """There is a small sleep time in the communication with the NanoVNA, which is needed.
            You can change the sleep time in order to speed up the communication.
            Beware of unexpected errors if setting this to lower than 0.05.

        Args:
            wait (float): Time in seconds
        """
        self.vna.set_wait(wait)

    def is_connected(self) -> bool:
        """Check if the NanoVNA is connected.

        Returns:
            bool: If it is connected or not.
        """
        return self.vna.connected()

    def info(self) -> dict:
        """Get info about your NanoVNA and the connection to it.

        Returns:
            dict: A dictionary with the info.
        """
        specifications = {
            "Serial Number": self.vna.SN,
            "Version": str(self.vna.version),
            "Features": self.vna.features,
            "Bandwidth Method": self.vna.bw_method,
            "Bandwidth": self.vna.bandwidth,
            "Valid Datapoints": self.vna.valid_datapoints,
            "Minimum Sweep Points": self.vna.sweep_points_min,
            "Interface": str(self.iface),
            "Info": hw.get_info(self.iface),
            "Comment": hw.get_comment(self.iface),
        }
        return specifications

    def kill(self):
        """Disconnect the NanoVNA.

        Raises:
            Exception: If the NanoVNA was not successfully disconnected.
        """
        self.vna.disconnect()
        if self.vna.connected():
            raise Exception("The VNA was not successfully disconnected.")
        logging.debug("Disconnected VNA.")
