from .hardware import Hardware as hw
from .Calibration import Calibration
from .CalibrationGuide import CalibrationGuide
from .SweepWorker import SweepWorker
from .Touchstone import Touchstone
from .RFTools import Datapoint
from datetime import datetime
import threading
import csv
from time import sleep


class NanoVNAWorker:
    def __init__(self, vna_index=0, verbose=False):
        """Initialize a NanoVNA object.

        Args:
            vna_index (int): Number of NanoVNAs to connect, at the moment multiple VNAs are not supported. Defaults to 0.
            verbose (bool): Print information. Defaults to False.
        """
        self.verbose = verbose
        self.playback_mode = False
        try:
            self.iface = hw.get_interfaces()[vna_index]
        except IndexError:
            print("NanoVNA not found, is it connected? Entering playback mode.")
            self.playback_mode = True
        if not self.playback_mode:
            self.vna = hw.get_VNA(self.iface)
            self.calibration = Calibration()
            self.touchstone = Touchstone("./output") #  Fix this.
            self.worker = SweepWorker(
                self.vna, self.calibration, self.touchstone, verbose=verbose
            )
            self.CalibrationGuide = CalibrationGuide(
                self.calibration, self.worker, verbose
            )
            if self.verbose:
                print("VNA is connected: ", self.vna.connected())
                print("Firmware: ", self.vna.readFirmware())
                print("Features: ", self.vna.read_features())

    def calibrate(self, savefile=None, load_file=False):
        """Run the calibration guide and calibrate the NanoVNA.

        Args:
            savefile (path): Path to save the calibration. Defaults to None.
            load_file (bool, optional): Path to existing calibration. Defaults to False.
        """
        if self.playback_mode:
            print("Cannot calibrate in playback mode. Connect NanoVNA and restart.")
            return
        if load_file:
            self.CalibrationGuide.loadCalibration(load_file)
            return
        proceed = self.CalibrationGuide.automaticCalibration()
        while proceed:
            proceed = self.CalibrationGuide.automaticCalibrationStep()
        if savefile is None:
            savefile = f"./Calibration_file_{datetime.now()}.cal"
        self.CalibrationGuide.saveCalibration(savefile)

    def set_sweep(self, start, stop, segments, points):
        """Set the sweep parameters.

        Args:
            start (int): The start frequnecy.
            stop (int): The stop frequency.
            segments (int): Number of segments.
            points (int): Number of points.
        """
        if self.playback_mode:
            print("Cannot set sweep in playback mode. Connect NanoVNA and restart.")
            return
        self.worker.sweep.update(start, stop, segments, points)
        if self.verbose:
            print(
                "Sweep set from "
                + str(self.worker.sweep.start / 1e9)
                + "e9"
                + " to "
                + str(self.worker.sweep.end / 1e9)
                + "e9"
            )

    def single_sweep(self):
        if self.playback_mode:
            print("Cannot do a sweep in playback mode. Connect NanoVNA and restart.")
            return
        self.worker.sweep.set_mode("SINGLE")
        self.worker.run()
        return self._get_data()

    def stream_data(self, data_file=False):
        """Creates a data stream from the continuous sweeping. (Or a previously recorded file.)

        Args:
            data_file (string): Path to a previously recorded csv file to stream from. Defaults to False.

        Yields:
            list: Yields a list of data when new data is available.
        """
        if not data_file:
            self._stream_data()
        sleep(2)
        try:
            if not data_file:
                if self.playback_mode:
                    print("Cannot stream data from NanoVNA in playback mode. Connect NanoVNA and restart.")
                    return
                stream = self._access_data()
            else:
                stream = self._csv_streamer(data_file)

            for data in stream:
                yield data  # Yield each piece of data as it comes
        except Exception as e:
            if self.verbose:
                print("Exception in data stream: ", e)
        finally:
            if self.verbose:
                print("Stopping worker.")
            self._stop_worker()

    def _stream_data(self):
        """Starts a thread for the sweep workers run function."""
        self.worker.sweep.set_mode("CONTINOUS")
        # Start the worker in a new thread
        self.worker_thread = threading.Thread(target=self.worker.run)
        self.worker_thread.start()

    def _csv_streamer(self, filename, data_points=5):
        """Stream previously recorded data from a csv file.

        Args:
            filename (string): Path to the csv file.
            data_points (int): Number of lines that each sweep is stored as. Defaults to 5.

        Yields:
            list: [refl_re, refl_im, thru_re, thru_im, freq]
        """
        try:
            with open(filename) as f:
                data = f.readlines()
                for i, line in enumerate(data):
                    if i != 0:
                        data_vals = [float(val) for val in line.split(",")]
                        s11 = Datapoint(data_vals[-1], complex(data_vals[0]).real, complex(data_vals[0]).imag)
                        s12 = Datapoint(data_vals[-1], complex(data_vals[1]).real, complex(data_vals[1]).imag)
                        yield (s11, s12)
        except Exception as e:
            print(e)

    def _access_data(self):
        """Fetches the data from the sweep worker as long as it is running a sweep.

        Yields:
            list: List of data from the latest sweep.
        """
        # Access data while the worker is running
        while self.worker.running:
            yield self._get_data()

    def _stop_worker(self):
        """Stop the sweep worker and kill the stream."""
        if self.verbose:
            print("NanoVNASaverHeadless is stopping sweepworker now.")
        if not self.playback_mode:
            self.worker.running = False
            self.worker_thread.join()

    def _get_data(self):
        """Get data from the sweep worker.

        Returns:
            list: Real Reflection, Imaginary Reflection, Real Through, Imaginary Through, Frequency
        """
        return self.worker.data11, self.worker.data21

    def save_csv(self, filename, skip_start=5):
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
            counter = 0 #  Counter because NanoVNA sends out incorrect data the first few times.
            with open(file_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Refl", "Thru", "Freq"])
                data_stream = self.stream_data()
                for new_data in data_stream:
                    if new_data[0][0].im != old_data[0][0].im:
                        counter += 1  # Increment counter when new_data is different
                        if counter > skip_start:
                            for data_index in range(len(new_data)):
                                writer.writerow([new_data[0][data_index].z, new_data[1][data_index].z, new_data[0][data_index].freq])
                    old_data = (new_data[0].copy(), new_data[1].copy()) # Update old_data every iteration to the latest data

        except Exception as e:
            print("An error occurred: ", e)

    def kill(self):
        """Disconnect the NanoVNA.

        Raises:
            Exception: If the NanoVNA was not successfully disconnected.
        """
        if self.playback_mode:
            print("Cannot kill in playback mode. Connect NanoVNA and restart.")
            return
        self._stop_worker()
        self.vna.disconnect()
        if self.vna.connected():
            raise Exception("The VNA was not successfully disconnected.")
        else:
            if self.verbose:
                print("Disconnected VNA.")
            return
