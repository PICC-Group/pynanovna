# fmt: off
import pynanovna
from pynanovna.utils import stream_from_csv
from pynanovna.vis import plot, polar

############################ Note ############################
# This script shows different ways to use pynanovna.
# The script is not intended to be run as it is, instead:  
# use comments to run only the part you are interested in.
##############################################################


#### SETUP ####

# Create a VNA object to control your NanoVNA.
vna = pynanovna.VNA()


# Get and print some information about your device.
print(vna.info())


# Load a premade calibration file. See example_calibration.py for info on calibration.
#vna.load_calibration("./Calibration_file.cal")


# Set the sweep range and number of points to measure.
vna.set_sweep(2.0e9, 2.8e9, 101)


#### USAGE ####

# Run a single sweep and retrieve the data.
data0, data1, freq = vna.sweep()
print("Single sweep done:", data0)

quit()
# Stream continuous sweeps and process the data.
for data0, data1, freq in vna.stream():
    # Use the streamed data inside this loop.
    print(data0, data1, freq)
    break  # Break the loop when done to close the stream.


# Stream data to a CSV file for a specified number of sweeps.
vna.stream_to_csv(".out", 10)


# Replay sweeps from a pre-recorded CSV file and process the data.
for data0, data1, freq in stream_from_csv(".out.csv"):
    # Use the replayed data inside this loop.
    print(data0, data1, freq)
    break


# Store the stream in a variable for further usage.
stream = vna.stream()


# Generate a classic s-parameter magnitude plot.
plot(stream, axis_mode="dynamic")


# You can also plot with fixed axis.
plot(stream, axis_mode="fixed", fixed_limits=[1e-1, 2, 1e-7, 2])


# Plot the data in polar coordinates, with normalization.
polar(stream, normalize=True)
