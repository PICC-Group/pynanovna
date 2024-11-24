from hardware import Hardware as hw

import logging
import numpy as np
import csv

class VNA:
    def __init__(self, vna_index=0, logging_level='info'):
        """Initialize a VNA object for the NanoVNA.

        Args:
            vna_index (int): If multiple NanoVNAs are connected you can specify which to use.
            verbose_level (str): The level of outputs. 'critical', 'info' or 'debug'. Defaults to 'info'.
        """
        logging_level = {'debug': logging.DEBUG, 'critical': logging.CRITICAL}.get(logging_level, logging.INFO)
        logging.basicConfig(level=logging_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging.debug("Initializing the VNA object.")
        try:
            self.iface = hw.get_interfaces()[vna_index]
            self.iface.open()
        except IndexError:
            logging.critical("NanoVNA not found, is it connected and turned on?")

        self.vna = hw.get_VNA(self.iface)
        self.sweep_interval = (None, None)
        self.sweep_points = None
        logging.debug("VNA object successfully initialized.")

    def set_sweep(self, start, stop, points):
        """Set the sweep parameters.

        Args:
            start (int): The start frequnecy.
            stop (int): The stop frequency.
            segments (int): Number of segments.
            points (int): Number of points.
        """
        self.vna.datapoints = points
        self.vna.set_sweep(start, stop)
        self.sweep_interval = (start, stop)
        self.sweep_points = points
        logging.debug("Sweep has been set from "
            + str(self.sweep_interval[0] / 1e9)
            + "e9"
            + " to "
            + str(self.sweep_interval[1] / 1e9)
            + "e9, with " + str(self.sweep_points) + " points."
        )

    def single_sweep(self):
        """Run a single sweep and return the data.

        Returns:
            tuple: s11, s21, frequencies
        """
        freq = np.array(self.vna.read_frequencies())
        data0 = np.array([complex(*map(float, s.split())) for s in self.vna.read_values('data 0')])
        data1 = np.array([complex(*map(float, s.split())) for s in self.vna.read_values('data 1')])
        return data0, data1, freq

    def stream_data(self):
        """Creates a data stream from the continuous sweeping. (Or a previously recorded file.)

        Args:
            data_file (string): Path to a previously recorded csv file to stream from. Defaults to False.
            start_delay (float): Time to wait for the stream to start before yielding values.

        Yields:
            list: Yields a list of data when new data is available.
        """
        freq = np.array(self.vna.read_frequencies())
        logging.debug("Frequencies read: %d values", len(freq))
        logging.debug("Starting stream.")

        while True:
            try:
                raw_data0 = self.vna.read_values('data 0')
                raw_data1 = self.vna.read_values('data 1')

                data0 = np.array([complex(*map(float, s.split())) for s in raw_data0]).copy()
                data1 = np.array([complex(*map(float, s.split())) for s in raw_data1]).copy()

                yield data0, data1, freq

            except KeyboardInterrupt:
                logging.debug("KeyboardInterrupt in stream, killing loop.")
                break
            except Exception as e:
                logging.critical("Exception in data stream: %s", e, exc_info=True)
                break

    def calibrate(
            self,
            load_file=False,
            savefile=None,
        ):
            """Run the calibration guide and calibrate the NanoVNA.

            Args:
                load_file (bool, optional): Path to existing calibration. Defaults to False.
                savefile (path): Path to save the calibration. Defaults to None.
            """



            # WIP



            pass

    def stream_to_csv(self, filename, nr_sweeps=float("INF"), skip_start=5, sweepdivider="sweepnumber: "):
        """Function to save the stream to a csv file.

        Args:
            filename (str): The filename to save to.
            nr_sweeps (int): Number of sweeps to run. Defaults to 10.
            skip_start (int): The NanoVNA usually gives bad data in the beginning, therefore this data can be skipped. Defaults to 5.

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
                for data in self.stream_data():
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
            logging.debug(f"KeyboardInterrupt in stream, killing loop.")
            return

        except Exception as e:
            logging.critical(f"Exception in data stream: ", exc_info=e)

    def info(self):
        specifications = {"Serial Number": self.vna.SN,
                          "Version": str(self.vna.version),
                          "Features":self.vna.features,
                          "Bandwidth Method": self.vna.bw_method,
                          "Bandwidth": self.vna.bandwidth,
                          "Valid Datapoints": self.vna.valid_datapoints,
                          "Minimum Sweep Points": self.vna.sweep_points_min,
                          "Interface": str(self.iface),
                          "Info": hw.get_info(self.iface)
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
        else:
            if self.verbose:
                print("Disconnected VNA.")
            return
