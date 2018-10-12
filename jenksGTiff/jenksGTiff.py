# -*- coding: utf-8 -*-
"""
Created on Fri May 11 15:01:39 2018

@author: nikhil.s.hubballi
"""
# import necessary packages
import gdal, osr
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib import colors
import jenkspy

# Clear the variables 
def clear_all():
    """Clears all the variables from the workspace of the spyder application."""
    gl = globals().copy()
    for var in gl:
        if var[0] == '_': continue
        if 'func' in str(globals()[var]): continue
        if 'module' in str(globals()[var]): continue

        del globals()[var]

# Implementing the Jenks algorithm on dataset with data preprocessing.
def importGTiff(filename):
    """ 
    Verifies the filename and its presence in the path before importing.
    """
    if isinstance(filename, str) and os.path.isfile(filename):
        return gdal.Open(filename)
    else:
        raise TypeError("Please Provide a valid path to the GTiff file")


def RemoveNoData(gtiff, NoDataVal):
    """ 
    Given the value for NoData pixels of the GTiff Image, this function 
    converts the imported GTiff object to array, before deleting the 
    NoData values from the array.
    """
    band =  gtiff.GetRasterBand(1)
    
    # Convert the GDAL dataset to an array
    array = band.ReadAsArray()
    
    NoData = band.GetNoDataValue()
    if NoData is None:
        NoData = NoDataVal
    
    # Delete all the NoData Values from the array
    return array[array != NoData]

def ReducedArray(array, sample_size_ratio):
    """
    Large dataset (array) can be reduced to small sample data representing their 
    parent distribution of data points (histogram), and then used for finding the 
    natural breaks. A sample size ratio can be fed in to determine the sample.
    """
    # Generating a small and random sample data from the larger input array
    numElements = int(sample_size_ratio*len(array))
    indices = np.random.permutation(len(array))
    if isinstance(numElements, int):
        indices = indices[0:numElements]
    else:
        raise TypeError("Please ensure the sample size is an integer.")
    
    # Use the identified indices to assign data values to a new list.
    array_short = []
    for i in indices:
        array_short.append(array[i])
        
    # Return the new array after conversion.
    # The Data can now be used to feed to the Jenks Natural Breaks algorithm.
    return np.array(array_short)

def JenksGTiff(filename, n_classes, NoDataVal = 0, sample_size_ratio = 0.1):
    """
    Performs the pre-processing functions on the input GTiff file.
    1. Convert to array, Remove NoDataValues
    2. Reduces the dataset to a desirable and efficient sample size to be 
        used for Jenks algorithm.
    After preprocessing the array dataset is fed to jenks_breaks function from
    jenkspy python module, to calculate the natural breaks.
    """
    # import the GTiff image
    gtiff = importGTiff(filename)
    
    # Remove NoData values from the dataset
    gtiff_arr = RemoveNoData(gtiff, NoDataVal)
      
    # Reduce the dataset size
    gtiff_short_arr = ReducedArray(gtiff_arr, sample_size_ratio)
    
    # Calculate the Jenks Natural Breaks
    breaks = jenkspy.jenks_breaks(gtiff_short_arr, nb_class=n_classes)
    
    return breaks, gtiff_arr, gtiff_short_arr
    
# Data Statistics and Visualization 

def DataStats(array):
    """
    Creates a dictionary of simple statistics measurements for the supplied
    array.
    """
    stats = {}
    stats['DataCount'] = len(array)
    stats['Minimum'] = min(array)
    stats['Maximum'] = max(array)
    stats['Sum'] = sum(array)
    stats['Mean'] = array.mean()
    stats['Median'] = np.median(array)
    stats['StandardDeviation'] = array.std()    
    return stats

def compareStats(array, sample_array):
    """
    Prints out the statistics of the mentioned dataset.
    """
    stats_arr = DataStats(array)
    stats_sample_arr = DataStats(sample_array)
    print ("Stats Measures - Value (original dataset) - Value (Sample dataset) \n")
    for key in stats_arr:
        print (key + ' : ' + str(stats_arr[key]) + ' : ' + str(stats_sample_arr[key]))   

def histogram(array, title, filename, bins=134):
    """
    Color-coded histograms by height is generated for the array supplied for the
    given bin size.
    """
    fig = plt.figure()
    
    # N is the count in each bin, bins is the lower-limit of the bin
    N, bins, patches = plt.hist(array, bins=bins)
    
    # color code by height
    fracs = N / N.max()
    
    # normalize the data to 0..1 for the full range of the colormap
    norm = colors.Normalize(fracs.min(), fracs.max())
    
    # loop through objects and set the color of each accordingly
    for thisfrac, thispatch in zip(fracs, patches):
        color = plt.cm.viridis(norm(thisfrac))
        thispatch.set_facecolor(color)
        
    # Plot configuration
    plt.title(title)
    plt.xlabel('Data values')
    plt.ylabel('Counts')
    plt.savefig(filename+'_'+title+'.png')
    plt.show()

# Save the output GTiff with application of Jenks breaks 
# Preserve the metadata, projection, format and other data for the GTiff
def exportGTiff(filename, output, breaks, NoDataVal=0.0):
    """
    Export the GTiff image after applying the natural breaks to the file
    """
    # Import GTiff and get the properties
    raster = importGTiff(filename)
    band = raster.GetRasterBand(1)
    array = band.ReadAsArray()
    meta = raster.GetMetadata()
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    pixelWidth = geotransform[1]
    originY = geotransform[3]
    pixelHeight = geotransform[5]
    rows, cols = array.shape
    NoDataVal = band.GetNoDataValue()
    
    paddock_indexs = np.where(array != NoDataVal)
    jenks_data = array[paddock_indexs]
    
    n_classes = len(breaks) - 1
    class_data_flat = np.ones(jenks_data.shape, dtype=np.int16)
    class_avg = np.zeros(n_classes, dtype=np.float32)
    class_bounds = np.zeros((n_classes, 2), dtype=np.float32)
    
    for i in range(1, len(breaks)):
        class_bounds[i-1, :] = [breaks[i-1], breaks[i]]
        
    for i in range(0, n_classes):
        indices = np.where(np.logical_and(jenks_data >= class_bounds[i, 0], jenks_data <= class_bounds[i, 1]))
        
        class_avg[i] = (class_bounds[i, 0] + class_bounds[i, 1]) / 2
        
        class_data_flat[indices] = i + 1
        
    class_data = np.ones(array.shape, dtype=np.int8) * (-1)  
    class_data[paddock_indexs] = class_data_flat
        
    # Generate the output raster GTiff with properties        
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(output, cols, rows, 1, gdal.GDT_Byte)
    outRaster.SetMetadata(meta)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromWkt(raster.GetProjectionRef())
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.WriteArray(class_data)
    outband.FlushCache()
    
    return class_data