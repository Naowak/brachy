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

    domaine_minimal = [[max(0, x_min - x_influence), max(0, y_min - y_influence)],
                       [min(lf-1, x_max + x_influence), min(mf-1, y_max + y_influence)]]
    
    return domaine_minimal


def matrix_to_domaine(matrix, domaine):
    # Recuperation des informations
    (x_min, y_min) = domaine[0]
    (x_max, y_max) = domaine[1]

    # Decoupage de la sous-matrice
    sous_matrix = matrix[x_min:x_max+1, y_min:y_max+1]
    return sous_matrix


def domaine_to_matrix(matrix, sous_matrix, domaine):
    """ NB modifie par reference (retour inutile donc) """
    # Recuperation des informations
    (x_min, y_min) = domaine[0]
    (x_max, y_max) = domaine[1]

    # Fusion de la sous-matrice avec la matrice complète
    matrix[x_min:x_max+1, y_min:y_max+1] = sous_matrix[:]
    return matrix


def get_domaine_n_points(domaine, old_n_points):
    # Recuperation des informations
    (x_min, y_min) = domaine[0]
    (x_max, y_max) = domaine[1]

    # +1 car c'est le nombre de points entre deux points inclus
    lf = (x_max - x_min) + 1
    mf = (y_max - y_min) + 1
    nf = old_n_points[2]
    n_points = (lf, mf, nf)

    return n_points


def get_domaine_dimensions(domaine, old_dimensions, old_maillage):
    # Recuperation des informations
    (x_min, y_min) = domaine[0]
    (x_max, y_max) = domaine[1]
    (old_maillage_x, old_maillage_y, old_maillage_z) = old_maillage

    # Calcul des dimensions
    Lx = old_maillage_x[x_max] - old_maillage_x[x_min]
    Ly = old_maillage_y[y_max] - old_maillage_y[y_min]
    Lz = old_dimensions[2]
    dimensions = (Lx, Ly, Lz)

    return dimensions


def get_domaine_sources(domaine, sources):
    # Recuperation des informations
    (x_min, y_min) = domaine[0]
    (x_max, y_max) = domaine[1]

    # Convertion du sous-vecteur des sources
    domaine_sources = []
    
    for source in sources:
        domaine_sources.append([source[0] - x_min, source[1] - y_min])

    return np.array(domaine_sources)


def get_domaine_HU_array(domaine, old_HU_array):
    return matrix_to_domaine(old_HU_array, domaine)


def get_coord_domaine(domaine, maillage):
    # Recuperation des informations
    (x_min, y_min) = domaine[0]
    (x_max, y_max) = domaine[1]    
    (maillage_x, maillage_y, maillage_z) = maillage

    return [[maillage_x[x_min], maillage_y[y_min]],
            [maillage_x[x_max], maillage_y[y_max]]]
                                        
    
                                
        
        



    
