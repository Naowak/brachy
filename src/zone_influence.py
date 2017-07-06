# -*- coding: utf-8 -*-
import sys
import os
import pylab
import dicom
import numpy as np
import matplotlib.pyplot as plt
from generate_multisource import *
from dose_parser import *


def get_domaine_minimal(sources, n_points, dimensions, maillage, zone_influence):
    """ """
    # Initialisation
    (lf, mf, nf) = n_points
    (Lx, Ly, Lz) = dimensions
    (maillage_x, maillage_y, maillage_z) = maillage
    x_min = lf - 1
    y_min = mf - 1
    x_max = 0
    y_max = 0

    # Recherche du domaine minimal a considerer
    for source in sources:        
        if maillage_x[x_min] - zone_influence > maillage_x[source[0]] - zone_influence:
            x_min = source[0]
            
        if maillage_y[y_min] - zone_influence > maillage_y[source[1]] - zone_influence:
            y_min = source[1]

        if maillage_x[x_max] + zone_influence < maillage_x[source[0]] + zone_influence:
            x_max = source[0]
            
        if maillage_y[y_max] + zone_influence < maillage_y[source[1]] + zone_influence:
            y_max = source[1]

    # On calcule a quoi correspond la zone d'influence en terme de coordonnees du maillage
    taille_maille_x = float(Lx) / lf
    x_influence = int(round(zone_influence / taille_maille_x))
    taille_maille_y = float(Ly) / mf
    y_influence = int(round(zone_influence / taille_maille_y))

    domaine_minimal = (max(0, x_min - x_influence),
                       max(0, y_min - y_influence),
                       min(lf-1, x_max + x_influence),
                       min(mf-1, y_max + y_influence))
    
    return domaine_minimal


def get_polygon_domaine_minimal(maillage, domaine_minimal):
    (x_min, y_min, x_max, y_max) = domaine_minimal
    (maillage_x, maillage_y, maillage_z) = maillage
    
    polygon_domaine_minimal = np.array([[maillage_x[x_min], maillage_y[y_min]],
                                        [maillage_x[x_min], maillage_y[y_max]],
                                        [maillage_x[x_max], maillage_y[y_max]],
                                        [maillage_x[x_max], maillage_y[y_min]],
                                        [maillage_x[x_min], maillage_y[y_min]]])

    return polygon_domaine_minimal
    
