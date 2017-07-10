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
    """ Test cas academique contourage + source + domaine """
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

    # Domaine minimal
    domaine_minimal = get_domaine_minimal(sources, n_points, dimensions, maillage, zone_influence)
    polygon_domaine_minimal = get_polygon_domaine_minimal(maillage, domaine_minimal)

    # Affichage
    plot_sources(n_points, dimensions, maillage, sources, contourage, polygon_domaine=polygon_domaine_minimal)



def test_2():
    """ Test sur DICOM prostate """
    # Parametres et instanciation
    filename_header = "prostate"
    DICOM_path = "/home/thibault/stage_CELIA/src/tests/data_tests/prostate"
    RT_structure_id = 158
    DP = DicomParser(DICOM_path, RT_structure_id)
    zone_influence_prostate = 50 # 50 pixels ~ 50 mm ~ 5 cm

    # Contourage prostate
    contourage_prostate = DP.get_DICOM_contourage(ROI_id=5, slice_id=149)

    # Generation
    DP.generate_DICOM_don(filename_header, 149, contourage_prostate, zone_influence=zone_influence_prostate, affichage=True)


def test_3():
    """ Test matrix_to_domaine """
    # Matrice
    matrix = np.array([[ 0.,  0.,  0.,  0.,  0.],
                       [ 0.,  0.,  4.,  2.,  0.],
                       [ 0.,  0.,  6.,  9.,  0.],
                       [ 0.,  0.,  0.,  0.,  0.],
                       [ 0.,  0.,  0.,  0.,  0.]])
    print "=== Matrice ===\n" + str(matrix) + "\n"

    print "=== Split ==="
    print "On garde seulement la sous-matrice contenant les valeurs"
    domaine = (1, 2, 2, 3)
    print matrix_to_domaine(matrix, domaine)


def test_4():
    """ Test reconstituion de matrix à partir d'une sous-matrix + domaine """
    # Matrice
    matrix = np.zeros([5, 5])
    print "=== Matrice ===\n" + str(matrix) + "\n"

    # Sous-matrice
    sous_matrix = np.array([[4., 2.],
                            [6., 9.]])
    print "=== Sous-matrice ===\n" + str(sous_matrix) + "\n"
    domaine = (1, 2, 2, 3)

    # Fusion
    print "=== Fusion ==="
    print "On met à jour la matrice principale avec la sous-matrice"
    matrix = domaine_to_matrix(matrix, sous_matrix, domaine)
    print matrix


def test_5():
    """ Test sur DICOM prostate """
    # Parametres et instanciation
    filename_header = "prostate"
    DICOM_path = "/home/thibault/stage_CELIA/src/tests/data_tests/prostate"
    RT_structure_id = 158
    DP = DicomParser(DICOM_path, RT_structure_id)
    zone_influence = 50 # 50 pixels ~ 50 mm ~ 5 cm
    slice_id = 149
    granularite_source = 5

    # Contourage prostate
    contourage = DP.get_DICOM_contourage(ROI_id=5, slice_id=149)

    densite = DP.get_DICOM_densite(slice_id)

    # Sources
    appartenance_contourage = get_appartenance_contourage(DP.n_points, DP.maillage, contourage)
    sources = get_sources(granularite_source, DP.n_points, appartenance_contourage, densite)

    # Domaine minimal
    domaine = get_domaine_minimal(sources, DP.n_points, DP.dimensions, DP.maillage, zone_influence)

    # Calculs des nouveaux parametres du domaine
    domaine_n_points = get_domaine_n_points(domaine, DP.n_points)
    domaine_dimensions = get_domaine_dimensions(domaine, DP.dimensions, DP.maillage)
    domaine_sources = get_domaine_sources(domaine, sources)

    print domaine_n_points
    print domaine_dimensions
    print domaine_sources

    


def main():
    #test_1()
    #test_2()
    test_3()
    test_4()
    #test_5()
    
if __name__ == "__main__":
    main()
