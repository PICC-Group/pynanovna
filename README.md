# pynanovna
This is a python module for using a NanoVNA.

## Installation
Install with `pip install pynanovna` or `pip3 install pynanovna`.

## Example
```
import pynanovna

vna = pynanovna.VNA()
stream = vna.stream()
for s11, s21, frequencies in stream:
    print(s11, s21, frequencies)
```

See `src/pynanovna/example.py` for a more detailed example on some use cases of the project.

API Reference is available at [pynanovna.readthedocs.io](https://pynanovna.readthedocs.io/en/latest)


## History
Originally this was the fork [nanovna-saver-headless](https://github.com/PICC-Group/nanovna-saver-headless) from [nanovna-saver](https://github.com/NanoVNA-Saver/nanovna-saver) but when that project no longer shared much code with the original we decided to create a new project.
Versions 1.0.0 and higher only use the hardware functions from nanovna-saver. The rest was rewritten by Teo Bergkvist (tbergkvist).
