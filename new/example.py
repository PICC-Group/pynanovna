from VNA import VNA

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


vna = VNA()

print(vna.info())

vna.set_sweep(2.9e9, 3.1e9, 11)

data0, data1, freq = vna.single_sweep() #  Run a single sweep 

for data0, data1, freq in vna.stream_data(): #  Let the NanoVNA run sweeps continuously and stream the data.
    #  Use the data.
    print(data0, data1, freq)
