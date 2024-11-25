# fmt: off
from VNA import VNA
from utils import stream_from_csv
from vis import plot, polar


# Create a VNA object to control your NanoVNA.
vna = VNA()

# Get and print some information about your device.
print(vna.info())

# Set the sweep range and number of points to measure.
vna.set_sweep(2.2e9, 2.6e9, 101)

# Run a single sweep and retrieve the data.
data0, data1, freq = vna.single_sweep()
print("Single sweep done:", data0)

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
