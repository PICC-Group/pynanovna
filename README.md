# pynanovna
This is a python module for using a NanoVNA.

## Installation
Install with `pip install pynanovna` or `pip3 install pynanovna`.

## Example
```
import pynanovna

worker = pynanovna.NanoVNAWorker()
stream = worker.stream_data(datafile)
for sweep in stream:
    print(sweep)
```

See `src/pynanovna/example.py` for a more detailed example on some use cases of the project.


## History
Originally this was the fork [nanovna-saver-headless](https://github.com/PICC-Group/nanovna-saver-headless) from [nanovna-saver](https://github.com/NanoVNA-Saver/nanovna-saver) but when that project no longer shared much code with the original we decided to create a new project.
