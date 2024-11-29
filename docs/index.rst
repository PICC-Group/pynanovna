.. PyNanoVNA documentation master file, created by
   sphinx-quickstart on Thu Jul 11 14:37:40 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyNanoVNA's documentation!
=====================================

# *pynanovna*
![PyPI - Version](https://img.shields.io/pypi/v/pynanovna)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pynanovna)
![PyPI - License](https://img.shields.io/pypi/l/pynanovna)
![GitHub Repo stars](https://img.shields.io/github/stars/PICC-Group/pynanovna)
[![DOI](https://zenodo.org/badge/791647347.svg)](https://doi.org/10.5281/zenodo.14231110)


This is a python module for using a NanoVNA.


## 🌟 Features
    ✅ Supporting almost all NanoVNAs.
    📶 Run single sweeps of s11 & s21 data.
    🔄 Stream continuous sweeps.
    🛠️ Calibrate your NanoVNA.
    📊 Interactive, real-time plots of data.
    📁 Record to CSV files.


## 🛠️ Installation
Install with `pip install pynanovna`.

## 🚀 Example
```
import pynanovna

vna = pynanovna.VNA()

vna.set_sweep(2.0e9, 2.6e9, 101)

stream = vna.stream()
for s11, s21, frequencies in stream:
    print(s11, s21, frequencies)
```

See `examples/example.py` for a more detailed example on some use cases of the project.

See `examples/example_calibration.py` for details on how to calibrate you NanoVNA.

.. toctree::
   :hidden:

   Home page <self>
   API reference <_autosummary/src.pynanovna>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`