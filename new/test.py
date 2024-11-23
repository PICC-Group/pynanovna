import Hardware.Hardware as hw
import logging



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
print(vna.get_calibration())



