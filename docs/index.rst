.. PyNanoVNA documentation master file, created by
   sphinx-quickstart on Thu Jul 11 14:37:40 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the pynanovna documentation!
=======================================

This is a Python module for using a NanoVNA. It supports streaming, saving, calibrating, and plotting data from various NanoVNAs. 

Installation
------------

Install with ``pip install pynanovna``.

Example
-------

::

   import pynanovna

   vna = pynanovna.VNA()

   vna.set_sweep(start_frequency, end_frequency, number_of_points)

   stream = vna.stream()

   for s11, s21, frequencies in stream:
      print(s11, s21, frequencies)


See ``examples/example.py`` for a more detailed example on using pynanovna.

See ``examples/example_calibration.py`` for an example on how to calibrate using pynanovna.

.. toctree::
   :hidden:

   Home page <self>
   API reference <_autosummary/src.pynanovna>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
