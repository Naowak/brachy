# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
from contourage import *
from generate_multisource import *
from test_contourage import *

def get_no_contourage(n_points):
    """ Retourne un contourage correspondant au maillage complet
    [Return] Une sequence de points (polygone) qui fait le tour complet du maillage

    [Params]
    - n_points : triplet (x, y, z) qui définit le nombre de points par axe

    [Complexité] O(n * log n)
    """
    # Recuperation parametres
    (lf, mf, nf) = n_points
    contourage = [(0, 0), (0, mf), (lf, mf), (lf, 0)]
    return np.array(contourage)


def test_1():
    """ Test cas academique sans contourage
    """
    # Parametres d'appel
    filename = "./data_tests/multisource_no_contourage.don"
    granularite_source = 2
    
    # Parametres fichier .don
    n_points = (50, 50, 1)
    dimensions = (5, 5, 1)
    rayon = (0.1, 0.1, 0.1)
    direction_M1 = (0., 0., 0.)
    spectre_mono = (1e20, 0.03)
    densite = get_densite_fantome_eau(n_points)
    contourage = get_no_contourage(n_points)

    # Sources
    maillage = get_maillage(n_points, dimensions)
    print maillage
    appartenance_contourage = get_appartenance_contourage(n_points, maillage, contourage)
    sources = get_sources(granularite_source, n_points, appartenance_contourage, densite)
    plot_sources(n_points, dimensions, maillage, sources, contourage)

    # Generation
    lancer_generation(filename, sources, n_points, dimensions, rayon, direction_M1, spectre_mono)


def test_2():
    """ Test cas academique avec contourage """
    # Parametres d'appel
    filename = "./data_tests/multisource_contourage_convexe.don"
    granularite_source = 2
    
    # Parametres
    lf = 50
    mf = 50
    nf = 1
    Lx = 5
    Ly = 5
    Lz = 1
    n_points = (lf, mf, nf)
    dimensions = (Lx, Ly, Lz)
    rayon = (0.1, 0.1, 0.1)
    direction_M1 = (0., 0., 0.)
    spectre_mono = (1e20, 0.03)
    densite = get_densite_fantome_eau(n_points)
    contourage = pol_convexe

    # Affichage des sources
    maillage = get_maillage(n_points, dimensions)
    appartenance_contourage = get_appartenance_contourage(n_points, maillage, contourage)
    sources = get_sources(granularite_source, n_points, appartenance_contourage, densite)
    plot_sources(n_points, dimensions, maillage, sources, contourage)

    # Generation
    lancer_generation(filename, sources, n_points, dimensions, rayon, direction_M1, spectre_mono)


def main():
    test_1()
    test_2()
    

if __name__ == "__main__":
    main()
