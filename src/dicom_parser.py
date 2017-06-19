# -*- coding: utf-8 -*-
import sys
import os
import pylab
import dicom
import numpy as np
import matplotlib.pyplot as plt

# Useful help https://pyscience.wordpress.com/2014/09/08/dicom-in-python-importing-medical-image-data-into-numpy-with-pydicom-and-vtk/

#def get_DICOM_contourage():
# dataset.ROIContours[0].Contours[0].ContourData 


#def get_DICOM_densite():
# Normaliser par rapport a l'eau


def get_DICOM_files(DICOM_path):
    # On recupere l'ensemble des fichiers DICOM dans un tableau
    DICOM_files = []
    for (dir_name, sub_dir_list, file_list) in os.walk(DICOM_path):
        for filename in file_list:
            if ".dcm" in filename.lower():  
                DICOM_files.append(os.path.join(dir_name, filename))

    return DICOM_files


def get_DICOM_slice(DICOM_files, slice):
    return dicom.read_file(DICOM_files[slice])


def get_DICOM_npoints(DICOM_slice):
    x = int(DICOM_slice.Rows)
    y = int(DICOM_slice.Columns)
    z = 1
    n_points = (x, y, z)
    
    return n_points


def get_DICOM_dimensions(DICOM_slice):
    # Convertion de mm vers cm
    x = float(DICOM_slice.PixelSpacing[0]) * 10**-1
    y = float(DICOM_slice.PixelSpacing[1]) * 10**-1
    z = 1
    #z = float(DICOM_slice.SliceThickness)
    dimensions = (x, y, z)
    
    return dimensions


def afficher_DICOM(DICOM_slice):
    pixel_array = DICOM_slice.pixel_array
    pylab.imshow(pixel_array, cmap=pylab.cm.bone)
    pylab.show()

    
