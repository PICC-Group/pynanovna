import hardware.Hardware as hw
import logging
import matplotlib.pyplot as plt
import numpy as np
import time



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
vna.datapoints = 11
vna.set_sweep(2.9e9, 3.1e9)
freq = vna.read_frequencies()
t0 = time.time()
data0 = vna.read_values('data 0')
t1 = time.time()
print("Read sweep: ", t1 - t0)

data00 = np.array([complex(*map(float, s.split())) for s in vna.read_values('data 0')]).real
data01 = np.array([complex(*map(float, s.split())) for s in vna.read_values('data 1')]).real

print(vna.read_frequencies())
print("Do something")
time.sleep(5)

data10 = np.array([complex(*map(float, s.split())) for s in vna.read_values('data 0')]).real
data11 = np.array([complex(*map(float, s.split())) for s in vna.read_values('data 1')]).real

print(np.array_equal(data00, data10))
print(np.array_equal(data01, data11))


plt.plot(data00)
plt.plot(data10)
plt.show()




#### PLOTTING INTERACTIVE #########
plt.ion()
fig, ax = plt.subplots()

line1, = ax.plot([], [], label='Data 0')
line2, = ax.plot([], [], label='Data 1')
ax.legend()

while True:
    try:
        data0, data1, freq = next(vna.stream_data())
        
        line1.set_data(freq, np.abs(data0))
        line2.set_data(freq, np.abs(data1))
        
        ax.relim()
        ax.autoscale_view()
        
        plt.pause(0.001)
    except StopIteration:
        print("Stream ended.")
        break
    except KeyboardInterrupt:
        print("Plot interrupted by user.")
        break
plt.ioff()
plt.show()
