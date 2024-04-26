from pynanovna import *

worker = pynanovna.NanoVNAWorker(verbose=True)

datafile = False #  Set this to a path if you want to play a previously recorded file.

stream = worker.stream_data(datafile)

for data in stream:
    print(data)
