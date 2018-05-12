# JenksGTiff
Apply Jenks Natural Breaks on Geotiff files and outputs image with graduated symbology

Compute "natural breaks" (Jenks algorithm) on list/tuple/numpy.ndarray of integers/floats.

Intented compatibility: CPython 2.7+ and 3.4+

Usage :
-------
.. code:: python

    >>> import jenksGTiff
    >>> breaks, array, array_short = jenksGTiff.JenksGTiff('\pwd\input.tif', n_classes, NoDataVal=0, sample_size_ratio=0.1)
    >>> breaks
    [-0.9921568632125854, -0.37254902720451355, -0.05882352963089943, 0.13725490868091583, 0.26274511218070984, 0.40392157435417175]
  
Since the image dataset was reduced to a small sample dataset, we compare both the stats and plot histograms.

.. code:: python

    >>> jenksGTiff.compareStats(array, array_short)
    Stats Measures - Value (original dataset) - Value (Sample dataset) 
    
    DataCount : 393868 : 39387
    Minimum : -0.99215686 : -0.99215686
    Maximum : 0.40392157 : 0.40392157
    Sum : 102931.59580400819 : 10252.694481091574
    Mean : 0.26133528 : 0.26030654
    Median : 0.29411766 : 0.29411766
    StandardDeviation : 0.11551328 : 0.117199086
    
    >>> jenksGTiff.histogram(array, 'Image Dataset', bins=134)
    ![Alt text](https://raw.githubusercontent.com/nsh-764/JenksGTiff/blob/master/array_hist.png)



