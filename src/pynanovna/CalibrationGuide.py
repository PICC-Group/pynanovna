from .Calibration import Calibration
from .Sweep import SweepMode


class CalibrationGuide:  # renamed from CalibrationWindow since it is no longer a window.
    nextStep = -1

    def __init__(self, calibration, worker, verbose=False):
        self.calibration = calibration
        self.worker = worker
        self.vna = worker.vna
        self.data = worker.data
        self.verbose = verbose

    def cal_save(self, name: str):
        if name in {"through", "isolation"}:
            self.calibration.insert(name, self.data.s21)
        else:
            self.calibration.insert(name, self.data.s11)

    def manual_save(self, name: str):
        self.cal_save(name)

    def reset(self):
        self.calibration = Calibration()

        if len(self.worker.rawData11) > 0:
            # There's raw data, so we can get corrected data
            if self.verbose:
                print("Saving and displaying raw data.")
            self.worker.saveData(
                self.worker.rawData11,
                self.worker.rawData21,
            )

    def setOffsetDelay(self, value: float):
        if self.verbose:
            print("New offset delay value: %f ps", value)
        self.worker.offsetDelay = value / 1e12
        if len(self.worker.rawData11) > 0:
            # There's raw data, so we can get corrected data
            if self.verbose:
                print("Applying new offset to existing sweep data.")
            (self.worker.data11, self.worker.data21,) = self.worker.applyCalibration(
                self.worker.rawData11, self.worker.rawData21
            )
            if self.verbose:
                print("Saving and displaying corrected data.")
            self.worker.saveData(
                self.worker.data11,
                self.worker.data21,
            )

    def calculate(self):
        cal_element = self.calibration.cal_element
        if False:  # TODO ensure sweep is not currently running.
            print(
                "Unable to apply calibration while a sweep is running. Please stop the sweep and try again."
            )
            return

        cal_element.short_is_ideal = True
        cal_element.open_is_ideal = True
        cal_element.load_is_ideal = True
        cal_element.through_is_ideal = True

        try:
            self.calibration.calc_corrections()

            if self.worker.rawData11:
                # There's raw data, so we can get corrected data
                if self.verbose:
                    print("Applying calibration to existing sweep data.")
                (self.worker.data11, self.worker.data21) = self.worker.applyCalibration(
                    self.worker.rawData11, self.worker.rawData21
                )

                if self.verbose:
                    print("Saving and displaying corrected data.")

                self.worker.saveData(
                    self.worker.data11,
                    self.worker.data21,
                )
        except ValueError as e:
            raise Exception(
                f"Error applying calibration: {str(e)}\nApplying calibration failed."
            )

    def loadCalibration(self, filename):
        if filename:
            self.calibration.load(filename)
        if not self.calibration.isValid1Port():
            raise Exception("Not a valid port.")

        for i, name in enumerate(
            ("short", "open", "load", "through", "isolation", "thrurefl")
        ):
            if i == 2 and not self.calibration.isValid2Port():
                break
        self.calculate()

    def saveCalibration(self, filename):
        if not self.calibration.isCalculated:
            raise Exception("Cannot save an unapplied calibration state.")

        try:
            self.calibration.save(filename)
            return True
        except Exception as e:
            print("Save failed: ", e)
            return False

    def automaticCalibration(self):
        response = input(
            """Calibration assistant,
            
                This calibration assistant will help you create a calibration in the NanoVNASaver application. It will sweep the standards for you and guide you through the process.\n
                Before starting, ensure you have Open, Short and Load standards available and the cables you wish to have calibrated connected to the device.\n
                Make sure sweep is NOT in continuous mode.\n
                If you want a 2-port calibration, also have a through connector on hand.\n
                The best results are achieved by having the NanoVNA calibrated on-device for the full span of interest and stored in save slot 0 before starting.\n\n
                Once you are ready to proceed, press enter. (q to quit)."""
        )

        if response.lower() == "q":
            return False
        print("Starting automatic calibration assistant.")
        if not self.vna.connected():
            print(
                "NanoVNA not connected.\n\nPlease ensure the NanoVNA is connected before attempting calibration."
            )
            return False

        if self.worker.sweep.properties.mode == SweepMode.CONTINOUS:
            print("Please disable continuous sweeping before attempting calibration.")
            return False

        response = input(
            "Calibrate short.\n\nPlease connect the short standard to port 0 of the NanoVNA.\n\n Press enter when you are ready to continue. (q to quit)."
        )

        if response.lower() == "q":
            return False

        self.reset()
        self.calibration.source = "Calibration assistant"
        self.nextStep = 0
        self.worker.run()
        self.automaticCalibrationStep()
        return True

    def automaticCalibrationStep(self):
        if self.nextStep == -1:
            return False

        if self.nextStep == 0:
            # Short
            self.cal_save("short")
            self.nextStep = 1

            response = input(
                """Calibrate open.\n\nPlease connect the open standard to port 0 of the NanoVNA.\n\nEither use a supplied open, or leave the end of the cable unconnected if desired.\n\nPress enter when you are ready to continue. (q to quit)."""
            )

            if response.lower() == "q":
                self.nextStep = -1
                return False
            self.worker.run()
            return True

        if self.nextStep == 1:
            # Open
            self.cal_save("open")
            self.nextStep = 2
            response = input(
                """Calibrate load.\nPlease connect the "load" standard to port 0 of the NanoVNA.\n\nPress enter when you are ready to continue. (q to quit)."""
            )

            if response.lower() == "q":
                self.nextStep = -1
                return False
            self.worker.run()
            return True

        if self.nextStep == 2:
            # Load
            self.cal_save("load")
            self.nextStep = 3
            response = input(
                """1-port calibration complete.\nThe required steps for a 1-port calibration are now complete.\n\nDo you wish to continue and perform a 2-port calibration, enter Y.\nTo apply the 1-port calibration and stop, press q. Answer:"""
            )

            if response.lower() == "q":
                self.calculate()
                self.nextStep = -1
                return False
            if response.lower() == "y" or response.lower() == "yes" or response == "":
                self.nextStep = 3

            response = input(
                """Calibrate isolation\nPlease connect the load standard to port 1 of the NanoVNA.\n\n If available, also connect a load standard to port 0.\n\n Press enter when you are ready to continue. (q to quit)."""
            )

            if response.lower() == "q":
                self.nextStep = -1
                return False
            self.worker.run()
            return True

        if self.nextStep == 3:
            # Isolation
            self.cal_save("isolation")
            self.nextStep = 4
            response = input(
                """Calibrate through.\nPlease connect the "through" standard between port 0 and port 1 of the NanoVNA.\n\nPress enter when you are ready to continue. (q to quit)."""
            )

            if response.lower() == "q":
                self.nextStep = -1
                return False
            self.worker.run()
            return True

        if self.nextStep == 4:
            # Done
            self.cal_save("thrurefl")
            self.cal_save("through")
            response = input(
                """Calibrate complete.\nThe calibration process is now complete. Press enter to apply the calibration parameters. (q to quit)."""
            )

            if response.lower() == "q":
                self.nextStep = -1
                return False

            self.calculate()
            self.nextStep = -1
            return True
