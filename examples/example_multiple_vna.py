# fmt: off
import pynanovna


############################ Note ############################
# This script demonstrates simultaneous usage of two NanoVNAs.
##############################################################


# First check that there are two devices connected by USB.abs
interfaces = pynanovna.utils.get_interfaces()
if len(interfaces) < 2:
    print("Could not find two connected devices. Quitting.")
    quit()

# Now create VNA objects for each connected NanoVNA. Use the vna_index argument.
vna0 = pynanovna.VNA(vna_index=0)
vna1 = pynanovna.VNA(vna_index=1)

# Perform calibration or load a calibration file to each VNA object.
# For this generic example, it is commented out.
#vna0.load_calibration("some_calibration_file.cal")
#vna1.load_calibration("some_other_calibration_file.cal")

# Set sweep ranges as usual for each VNA object.
# For this generic example, it is commented out.
#vna0.set_sweep(2.0e9, 2.8e9, 101)
#vna1.set_sweep(2.0e9, 2.8e9, 101)

# Perform sweeps as usual.
vna0_s11, vna0_s21, vna0_frequencies = vna0.sweep()
vna1_s11, vna1_s21, vna1_frequencies = vna1.sweep()
print(vna0_s11, vna1_s11)

# You can also run two streams simultaneously.
stream0 = vna0.stream()
stream1 = vna1.stream()

# It is helpful to use zip to iterate both streams at the same time.
for values0, values1 in zip(stream0, stream1):
    print(values0[0], values1[0])


# Note that if the NanoVNAs differ in model or setup values, there will probably be a time difference
# between sweeps. This might cause errors when iterating the streams at the same time.
