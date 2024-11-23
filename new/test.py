import hardware.Hardware as hw
import logging
import matplotlib.pyplot as plt
import numpy as np



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# To get a list of the serial/usb interfaces available.
ifaces = hw.get_interfaces()
#print("Interfaces: ", ifaces)
iface = ifaces[0]

# Open the interface.
iface.open()
#print("Chosen interface: ", iface)

# Get VNA object.
#print("Getting VNA object from interface.")
vna = hw.get_VNA(iface)
#print("VNA object: ", vna)


# Connect to the VNA.
print("VNA is connected: ", vna.connected())
vna.datapoints = 51
vna.set_sweep(2.9e9, 3.1e9)
freq = vna.read_frequencies()
data0 = np.array([complex(*map(float, s.split())) for s in vna.read_values('data 0')]).real
data1 = np.array([complex(*map(float, s.split())) for s in vna.read_values('data 1')]).real
print(data0)


plt.plot(freq, data1)
plt.show()

