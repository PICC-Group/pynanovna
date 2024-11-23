from hardware import Hardware as hw

import logging
import numpy as np

class VNA:
    def __init__(self, vna_index=0, verbose='info'):
        """Initialize a VNA object for the NanoVNA.

        Args:
            vna_index (int): If multiple NanoVNAs are connected you can specify which to use.
            verbose_level (str): The level of outputs. 'critical', 'info' or 'debug'. Defaults to 'info'.
        """
        logging_level = {'debug': logging.DEBUG, 'critical': logging.CRITICAL}.get(verbose, logging.INFO)
        logging.basicConfig(level=logging_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging.debug("Initializing the VNA object.")
        try:
            self.iface = hw.get_interfaces()[vna_index]
            self.iface.open()
        except IndexError:
            logging.critical("NanoVNA not found, is it connected and turned on?")

        self.vna = hw.get_VNA(self.iface)
        logging.debug("VNA object successfully initialized.")

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
        logging.debug("Sweep has been set from "
            + str(self.worker.sweep.start / 1e9)
            + "e9"
            + " to "
            + str(self.worker.sweep.end / 1e9)
            + "e9, with " + str(points) + "points."
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

    def stream_data(self, data_file=False, start_delay=2.0):
        """Creates a data stream from the continuous sweeping. (Or a previously recorded file.)

        Args:
            data_file (string): Path to a previously recorded csv file to stream from. Defaults to False.
            start_delay (float): Time to wait for the stream to start before yielding values.

        Yields:
            list: Yields a list of data when new data is available.
        """



        # WIP



        try:
            if not data_file:
                if self.playback_mode:
                    print(
                        "Cannot stream data from NanoVNA in playback mode. Connect NanoVNA and restart."
                    )
                    return

                self._stream_data()
                sleep(start_delay)

                stream = self._access_data()
            else:
                stream = self._csv_streamer(data_file)

            for data in stream:
                yield data  # Yield each piece of data as it comes

        except KeyboardInterrupt:
            self._stop_worker()
        except Exception as e:
            if self.verbose:
                print("Exception in data stream: ", e)
        finally:
            if self.verbose:
                print("Stopping worker.")
            self._stop_worker()

    def _stream_data(self):



        # WIP



        """Starts a thread for the sweep workers run function."""
        self.worker.sweep.set_mode("CONTINOUS")
        # Start the worker in a new thread
        self.worker_thread = threading.Thread(target=self.worker.run)
        self.worker_thread.start()

    def _csv_streamer(self, filename, sweepdivider="Sweepno"):



        # WIP



        """Stream previously recorded data from a csv file.

        Args:
            filename (string): Path to the csv file.
            sweepdivider (string): Used to identify where sweeps end and start in the csv file.

        Yields:
            tuple: ([s11], [s21])
        """
        try:
            with open(filename) as f:
                data = f.readlines()
                package = ([], [])
                for i, line in enumerate(data):
                    if i != 0:
                        if sweepdivider in line:
                            if package != ([], []):
                                yield package
                            package = ([], [])
                            continue
                        data_vals = [complex(val) for val in line.split(",")]
                        package[0].append(
                            Datapoint(
                                data_vals[-1].real,
                                data_vals[0].real,
                                data_vals[0].imag,
                            )
                        )
                        package[1].append(
                            Datapoint(
                                data_vals[-1].real,
                                data_vals[1].real,
                                data_vals[1].imag,
                            )
                        )
        except KeyboardInterrupt:
            return
        except Exception as e:
            print(e)

    def _access_data(self):



        # WIP



        """Fetches the data from the sweep worker as long as it is running a sweep.

        Yields:
            list: List of data from the latest sweep.
        """
        while self.worker.running:
            yield self._get_data()

    def _stop_worker(self):



        # WIP



        """Stop the sweep worker and kill the stream."""
        if self.verbose:
            print("NanoVNASaverHeadless is stopping sweepworker now.")
        if not self.playback_mode:
            self.worker.running = False
            self.worker_thread.join()

    def _get_data(self):



        # WIP



        """Get data from the sweep worker.

        Returns:
            list: Real Reflection, Imaginary Reflection, Real Through, Imaginary Through, Frequency
        """
        return self.worker.data11, self.worker.data21

    def save_csv(self, filename, skip_start=5, sweepdivider="Sweepno"):



        # WIP



        """Function to save the stream to a csv file.

        Args:
            filename (str): The filename to save to.
            nr_sweeps (int): Number of sweeps to run. Defaults to 10.
            skip_start (int): The NanoVNA usually gives bad data in the beginning, therefore this data can be skipped. Defaults to 5.

        Raises:
            TypeError: If the filename is not a string.
        """
        if self.playback_mode:
            print("Cannot run sweeps in playback mode. Connect NanoVNA and restart.")
            return
        try:
            if not isinstance(filename, str):
                raise TypeError("Filename must be a string")
            if not filename.endswith(".csv"):
                filename += ".csv"
            file_path = filename
            old_data = [[Datapoint(1, 1.0, 1.0)]]
            counter = 0  #  Counter because NanoVNA sends out incorrect data the first few times.
            with open(file_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Refl", "Thru", "Freq"])
                data_stream = self.stream_data()
                for new_data in data_stream:
                    if new_data[0][0].im != old_data[0][0].im:
                        writer.writerow([sweepdivider, counter])
                        counter += 1  # Increment counter when new_data is different
                        if counter > skip_start:
                            for data_index in range(len(new_data[0])):
                                writer.writerow(
                                    [
                                        new_data[:][0][data_index].z,
                                        new_data[:][1][data_index].z,
                                        new_data[:][0][data_index].freq,
                                    ]
                                )
                    old_data = (
                        new_data[0].copy(),
                        new_data[1].copy(),
                    )  # Update old_data every iteration to the latest data

        except KeyboardInterrupt:
            return

        except Exception as e:
            print("An error occurred: ", e)

    def kill(self):



        # WIP



        """Disconnect the NanoVNA.

        Raises:
            Exception: If the NanoVNA was not successfully disconnected.
        """
        if self.playback_mode:
            print("Cannot kill in playback mode. Connect NanoVNA and restart.")
            return
        if self.worker.running:
            self._stop_worker()
        self.vna.disconnect()
        if self.vna.connected():
            raise Exception("The VNA was not successfully disconnected.")
        else:
            if self.verbose:
                print("Disconnected VNA.")
            return
