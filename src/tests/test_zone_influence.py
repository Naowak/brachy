# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
from zone_influence import *
from dicom_parser import *
from dose_parser import *


# Polygone regulier convexe
pol_convexe = np.array([[4.28, 2.28], [4.31, 2.63], [4.25, 2.98], [4.13, 3.31], [3.94, 3.61], \
                        [3.69, 3.86], [3.40, 4.05], [3.07, 4.18], [2.72, 4.24], [2.37, 4.22], \
                        [2.03, 4.14], [1.71, 3.98], [1.43, 3.76], [1.21, 3.49], [1.05, 3.17], \
                        [0.95, 2.83], [0.93, 2.48], [0.98, 2.13], [1.11, 1.80], [1.30, 1.50], \
                        [1.55, 1.25], [1.84, 1.06], [2.17, 0.93], [2.52, 0.87], [2.87, 0.88], \
                        [3.21, 0.97], [3.53, 1.13], [3.8, 1.35], [4.03, 1.62], [4.19, 1.94], \
                        [4.28,2.28]])


def test_1():
    """ Test cas academique avec contourage
    NB : les calculs sont réalisés plusieurs fois pour l'affichage des sources notamment
    """
    # Parametres
    lf = 50
    mf = 50
    nf = 1
    Lx = 5
    Ly = 5
    Lz = 1
    n_points = (lf, mf, nf)
    dimensions = (Lx, Ly, Lz)
    granularite_source = 2
    zone_influence = 0.6

    # Arbitrairement
    densite = get_densite_fantome_eau(n_points)
    contourage = pol_convexe

    # Calcul des sources
    maillage = get_maillage(n_points, dimensions)
    (maillage_x, maillage_y, maillage_z) = maillage
    appartenance_contourage = get_appartenance_contourage(n_points, maillage, contourage)
    sources = get_sources(granularite_source, n_points, appartenance_contourage, densite)

    # Calcul et affichage du domaine minimal
    domaine_minimal = get_domaine_minimal(sources, n_points, dimensions, maillage, zone_influence)
    polygon_domaine_minimal = get_polygon_domaine_minimal(maillage, domaine_minimal)

    # Affichage
    plot_sources(n_points, dimensions, maillage, sources, contourage, polygone_domaine=polygon_domaine_minimal)



def test_2():
    # Parametres et instanciation
    filename_header = "prostate"
    DICOM_path = "/home/thibault/stage_CELIA/src/tests/data_tests/prostate"
    RT_structure_id = 158
    DP = DicomParser(DICOM_path, RT_structure_id)
    granularite_source = 5
    zone_influence = 10 # 10 pixels ~ 10 mm

    # Contourage prostate
    contourage = DP.get_DICOM_contourage(ROI_id=5, slice_id=149)

    # Affichage des sources
    appartenance_contourage = get_appartenance_contourage(DP.n_points, DP.maillage, contourage)
    sources = get_sources(granularite_source, DP.n_points, DP.maillage, appartenance_contourage, densite)
    (x_min, y_min, x_max, y_max) = get_domaine_minimal(sources, DP.n_points, DP.dimensions, DP.maillage, zone_influence)

    contourages_array = []
    #DP.add_contourage_plot(contourages,array, 149,


def main():
    test_1()
    
    
if __name__ == "__main__":
    main()
