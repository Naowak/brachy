# -*- coding: utf-8 -*-
import sys
import scipy as sp
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
from matplotlib.collections import PolyCollection, LineCollection


# Source : https://stackoverflow.com/questions/16750618/whats-an-efficient-way-to-find-if-a-point-lies-in-the-convex-hull-of-a-point-cl/16898636#16898636?newreg=724ec04daade413a922214eb5341c352

def get_appartenance_contourage(n_points, maillage, contourage):
    """ Regarde pour chaque point p dans points si le point appartient à la zone contourée
    [Return] Un couple (appartenance_contourage, contourage_delaunay) 
    - Un tableau de booléen qui précise pour chaque point s'il appartient au contourage
    - Le resultat de la triangularisation de Delaunay

    [Params]
    - points : tableau de points
    - contourage : tableau de points représentant le contourage (polygone convexe)
    NB : un point est un vecteur [x, y]

    [Complexité]
    O(n * logn)
    """
    (lf, mf, nf) = n_points
    (maillage_x, maillage_y, maillage_z) = maillage
    
    # Mise au format pour traitement scipy
    points = [0] * (lf * mf)
    i_points = 0
    
    for x in range(lf):
        for y in range(mf):
            points[i_points] = (maillage_x[x], maillage_y[y])
            i_points += 1
            
    # On calcule l'enveloppe convexe (pas exactement, ie. triangularisation de Delaunay overkill)
    contourage_delaunay = Delaunay(contourage)
    appartenance_contourage_1D = contourage_delaunay.find_simplex(points) >= 0

    # Mise au format 2D classique
    appartenance_contourage_2D = np.zeros([lf, mf])
    indice_1D = 0

    for x in range(lf):
        for y in range(mf):
            appartenance_contourage_2D[x, y] = appartenance_contourage_1D[indice_1D]
            indice_1D += 1

    print appartenance_contourage_2D
    return (appartenance_contourage_2D, contourage_delaunay)

        
def in_contourage(x, y, appartenance_contourage):
    """ Indique si un point appartient au contourage ou nom
    [Return] True si point appartient au contourage, False sinon

    [Params]
    - point : vecteur [x, y]
    - appartenance_contourage : tableau de booleen retourné par get_appartenance_contourage
    - nb_vector : triplet  (nbx, nby, nbz) qui définit le nombre de points sur chaque axe

    [Complexité]
    O(1)
    """
    return appartenance_contourage[x, y]


def plot_appartenance_contourage(n_points, maillage, appartenance_contourage, contourage_delaunay):
    """ Affiche
    plot relative to `in_hull` for 2d data
    """
    # Recuperation des parametres et mise sous forme 2D
    (lf, mf, nf) = n_points
    (maillage_x, maillage_y, maillage_z) = maillage
    
    # Affichage enveloppe convexe
    edges = set()
    edge_points = []

    def add_edge(i, j):
        """Add a line between the i-th and j-th points, if not in the list already"""
        if (i, j) in edges or (j, i) in edges:
            # already added
            return
        edges.add((i, j))
        edge_points.append(contourage_delaunay.points[[i, j]])

    for ia, ib in contourage_delaunay.convex_hull:
        add_edge(ia, ib)

    lines = LineCollection(edge_points, color='b')
    plt.gca().add_collection(lines)
    plt.show()    

    # plot tested points `p` - black are inside contourage, red outside
    #plt.plot(points[appartenance_contourage, 0], points[ appartenance_contourage, 1],'.k')
    #plt.plot(points[-appartenance_contourage, 0], points[-appartenance_contourage, 1],'.r')
    points_inside = []
    points_outside = []
    
    for x in range(lf):
        for y in range(mf):
            point = (maillage_x[x], maillage_y[y])
            if in_contourage(x, y, appartenance_contourage):
                points_inside.append(point)
            else:
                points_outside.append(point)

    points_inside = np.array(points_inside)
    points_outside = np.array(points_outside)

    plt.plot(points_inside[:,0], points_inside[:,1], color='g', marker='o', linestyle='None')
    plt.plot(points_outside[:,0], points_outside[:,1], color='r', marker='o', linestyle='None')


def main():
    # Creation artificielle maillage et contourage
    points = np.random.rand(20, 3)
    maillage_x = np.linspace(0, 1, 10)
    maillage_y = np.linspace(0, 1, 10)
    maillage_z = np.linspace(0, 1, 1)
    maillage = (maillage_x, maillage_y, maillage_z)
    
    contourage  = np.random.rand(50, 2)

    n_points = (10, 10, 1)

    (appartenance_contourage, contourage_delaunay) = get_appartenance_contourage(n_points, maillage, contourage)
    plot_appartenance_contourage(n_points, maillage, appartenance_contourage, contourage_delaunay)


if __name__ == "__main__":
    main()
