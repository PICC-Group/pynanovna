import pynanovna

worker = pynanovna.NanoVNAWorker(verbose=True)

# If you want to play a previously recorded file:
datafile = "path/to/saved/recording.csv"

# If NanoVNA is connected:
datafile = False
worker.calibrate(load_file="path/to/saved/calibrationfile.cal")
worker.set_sweep(2.9e9, 3.1e9, 1, 101)

# Create a stream:
stream = worker.stream_data(datafile)

# Plot functions:
pynanovna.vis.plot(stream)
pynanovna.vis.polar(stream, normalize=True)

# Print the streamed data:
for data in stream:
    print(data)

# If NanoVNA is connected you can run this to save a stream:
worker.save_csv("./save.csv")

# Kill the worker when done:
worker.kill()
