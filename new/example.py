from VNA import VNA
from utils import stream_from_csv
from vis import plot, polar

import matplotlib.pyplot as plt
import numpy as np


vna = VNA()

print(vna.info())

vna.set_sweep(2.2e9, 2.6e9, 101)

data0, data1, freq = vna.single_sweep()  #  Run a single sweep
print("Single sweep done: ", data0)


for (
    data0,
    data1,
    freq,
) in vna.stream():  #  Let the NanoVNA run sweeps continuously and stream the data.
    #  Use the data.
    print(data0, data1, freq)
    break


vna.stream_to_csv(".out", 10)  #  Stream data to a csv file.

for data0, data1, freq in stream_from_csv(
    ".out.csv"
):  #  Replay sweeps from a pre-recorded CSV file.
    #  Use the data.
    print(data0, data1, freq)
    break


stream = vna.stream()

plot(
    stream, axis_mode="fixed", fixed_limits=[1e-1, 2, 1e-7, 2]
)  #  Classic s-parameter magnitude plot.
polar(stream, normalize=True)  #  Plot the polar coordinates.
