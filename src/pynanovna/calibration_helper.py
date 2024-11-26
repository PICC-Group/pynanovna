# fmt: off
import time

from pynanovna import VNA

###################### Note ######################
# This script can be run as a calibration helper.
# It can also be used as an example on
# how to use the calibation functions.
##################################################

vna = VNA() #  Create a vna object.

if not vna.is_connected():
    print("No vna connected. Quitting.")
    quit()

print("Enter the frequency range and number of points to calibrate for.")
start = float(input("Enter minimum frequency as a float: "))
stop = float(input("Enter maximum frequency as a float: "))
points = int(input("Enter number of points as an int: "))

vna.set_sweep(start, stop, points) # It is important to perform the calibration in the frequency range you intend to measure in.

input(
    "Calibrate short.\n\nPlease connect the short standard to port 1 of the NanoVNA.\n\n Press enter when you are ready to continue."
)
vna.calibration_step("short") #  The calibration is done in several steps as usual.

input(
    "Calibrate open.\n\nPlease connect the open standard to port 1 of the NanoVNA.\n\nEither use a supplied open, or leave the end of the cable unconnected if desired.\n\nPress enter when you are ready to continue."
)
vna.calibration_step("open")

input(
    'Calibrate load.\nPlease connect the "load" standard to port 1 of the NanoVNA.\n\nPress enter when you are ready to continue.'
)
vna.calibration_step("load")

input(
    "Calibrate isolation\nPlease connect the load standard to port 2 of the NanoVNA.\n\n If available, also connect a load standard to port 1.\n\n Press enter when you are ready to continue."
)
vna.calibration_step("isolation")

input(
    'Calibrate through.\nPlease connect the "through" standard between port 1 and port 2 of the NanoVNA.\n\nPress enter when you are ready to continue.'
)
vna.calibration_step("through")

input(
    "Calibrate complete.\nThe calibration process is now complete. Press enter to apply the calibration parameters."
)
vna.calibrate() #  When all steps are done, run the calibrate function to calculate a calibration and enable it.

ans = input("Do you wish to save this calibration to a file? [y]/n: ")

if ans not in ["n", "N", "no", "No"]:
    filename = f"./Calibration_{time.time()}.cal"
    print(f"Saving calibration to {filename}.")
    vna.save_calibration(filename)
else:
    print("Discarding calibration.")
