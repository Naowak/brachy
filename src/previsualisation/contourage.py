#!/usr/bin/env python
# -*- coding: utf-8 -*-
# contourage.py
""" Gestion des calculs de contourage """
# Author : Thibault PARPAITE, Cyrille BEAUCHESNE
# Copyright (c) 2017, CELIA Bordeaux
# This file is part of cythi, released under a BSD license.


import sys
import numpy as np
import matplotlib.path as mp
import matplotlib.pyplot as plt
import matplotlib.patches as patches


# Source : http://www.portailsig.org/content/sur-la-creation-des-enveloppes-concaves-concave-hull-et-les-divers-moyens-d-y-parvenir-forme

def get_appartenance_contourage(n_points, maillage, contourage):
    """ Regarde pour chaque point p dans points si le point appartient à la zone contourée
    [Return] Un tableau de booléen 2D qui précise pour chaque point s'il appartient au contourage

    [Params]
    - n_points : triplet (x, y, z) qui définit le nombre de points par axe
    - maillage : triplet (maillage_x, maillage_y, maillage_z) qui représente le maillage
    - contourage : sequence de points (x, y) representant un polygone

    [Complexité] O(n * logn)
    """
    # Recuperation parametres
    (lf, mf, nf) = n_points
    (maillage_x, maillage_y, maillage_z) = maillage
    contourage = contourage[:,(0,1)] # On garde seulement 2D pour utiliser mp.Path
    
    # Mise au format 1D pour traitement matplotlib.path
    points = np.zeros([(lf * mf), 2]) # Tableau 1D de points
    indice_points = 0
    
    for x in range(lf):
        for y in range(mf):
            points[indice_points] = (x, y)
            indice_points += 1

    # Calcul du contourage à proprement parler
    contourage_path = mp.Path(contourage)
    appartenance_contourage_1D = contourage_path.contains_points(points)

    # Mise au format 2D
    appartenance_contourage_2D = np.zeros([lf, mf])
    indice_1D = 0

    for x in range(lf):
        for y in range(mf):
            appartenance_contourage_2D[x, y] = appartenance_contourage_1D[indice_1D]
            indice_1D += 1

    return appartenance_contourage_2D

        
def in_contourage(appartenance_contourage, x, y):
    """ Indique si un point appartient au contourage ou nom
    [Return] True si point appartient au contourage, False sinon

    [Params]
        - appartenance_contourage : tableau de booleen 2D retourné par get_appartenance_contourage
    - x, y indiquant les coordonnées dans le maillage

    [Complexité] O(1)
    """
    return appartenance_contourage[x, y]


def plot_contourage(ax, contourage, color):
    """ Ajoute la visualisation du contourage sur la figure
    [Params]
    - ax : l'axe correspondant à la figure
    - contourage : une sequence de points representant un polygone fermé
    - color : couleur du contourage
    """
    contourage_2D = contourage[:,(0,1)] # On garde seulement 2D pour utiliser mp.Path
    contourage_path = mp.Path(contourage_2D)
    patch = patches.PathPatch(contourage_path, facecolor=color, linewidth=1)
    ax.add_patch(patch)


def plot_appartenance_contourage(n_points, dimensions, maillage, appartenance_contourage, contourage):
    """ Affiche l'appartenance d'un contourage sous forme graphique
    [Params]
    - n_points : triplet (x, y, z) qui définit le nombre de points par axe
    - dimensions : dimensions : triplet (x, y, z) qui définit les dimensions en cm
    - maillage : triplet (maillage_x, maillage_y, maillage_z) qui représente le maillage
    - appartenance_contourage : tableau de booleen 2D retourné par get_appartenance_contourage
    - contourage : sequence de points representant un polygone

    [Complexité] O(n)
    """
    # Recuperation parametres
    (lf, mf, nf) = n_points
    (Lx, Ly, Lz) = dimensions
    (maillage_x, maillage_y, maillage_z) = maillage

    fig, ax = plt.subplots()
    ax.set_xlim([0, Lx])
    ax.set_ylim([0, Ly])

    # Affichage du contourage
    plot_contourage(ax, contourage, 'orange')

    # Affichage de appartenance_contourage
    points_inside = []
    points_outside = []
    
    for x in range(lf):
        for y in range(mf):
            point = (maillage_x[x], maillage_y[y])
            if in_contourage(appartenance_contourage, x, y):
                points_inside.append(point)
            else:
                points_outside.append(point)

    points_inside = np.array(points_inside)
    points_outside = np.array(points_outside)

    plt.plot(points_inside[:,0], points_inside[:,1], color='g', marker='o', linestyle='None')
    plt.plot(points_outside[:,0], points_outside[:,1], color='r', marker='o', linestyle='None')
    plt.show()


def get_coord_contourage(contourage, maillage):
    """ Recuperation des coordonnees exactes d'un contourage a partir du maillage """
    # Recuperation parametres
    (maillage_x, maillage_y, maillage_z) = maillage

    # Recuperation des coordonnees exactes a partir du maillage
    coord_contourage = []
    
    for point in contourage:
        coord_point = (maillage_x[point[0]], maillage_y[point[1]])
        coord_contourage.append(coord_point)

    return np.array(coord_contourage)
