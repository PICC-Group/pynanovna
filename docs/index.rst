.. PyNanoVNA documentation master file, created by
   sphinx-quickstart on Thu Jul 11 14:37:40 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyNanoVNA's documentation!
=====================================

This is a python module for using a NanoVNA. It has support for streaming, processing and plotting data from
various NanoVNAs. 

Installation
------------

Install with ``pip install pynanovna`` or ``pip3 install pynanovna``.

Example
-------

::

   import pynanovna

   worker = pynanovna.NanoVNAWorker()
   stream = worker.stream_data()
   for sweep in stream:
       print(sweep)


See ``src/pynanovna/example.py`` for a more detailed example on some use
cases of the project.

.. toctree::
   :hidden:

   Home page <self>
   API reference <_autosummary/pynanovna>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
