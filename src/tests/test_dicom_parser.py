# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
from dicom_parser import *
from dose_parser import *
from merge_multisource import *


def test_1():
    """ Test affichage DICOM simple """
    # Parametres et instanciation
    DICOM_path = "/home/thibault/stage_CELIA/src/tests/data_tests/my_head"
    DP = DicomParser(DICOM_path)

    # Affichage
    DP.afficher_DICOM("Crane", 140)


def test_2():
    """ Test affichage DICOM et dose """
    # Parametres et instanciation
    DICOM_path = "/home/thibault/stage_CELIA/src/tests/data_tests/my_head"
    DP = DicomParser(DICOM_path)
    
    # Calcul de dose grossier
    dose_path = "/home/thibault/stage_CELIA/src/tests/data_tests/my_head_dose.dat"
    f = open(dose_path, "r")
    get_header_info(f) # On passe les informations du header
    dose_matrix = get_dose(f, DP.n_points)
    DP.afficher_DICOM("Crane + dose", dose_matrix=dose_matrix, slice_id=140)
    f.close()


def test_3():
    """ Test affichage DICOM simple """
    # Parametres et instanciation
    filename_header = "prostate"
    DICOM_path = "/home/thibault/stage_CELIA/src/tests/data_tests/prostate"
    RT_structure_id = 158
    DP = DicomParser(DICOM_path, RT_structure_id)

    # Affichage
    afficher_DICOM("Prostate", slice_id=149)


def test_4():
    """ Test affichage contourage prostate """
    # Parametres et instanciation
    filename_header = "prostate"
    DICOM_path = "/home/thibault/stage_CELIA/src/tests/data_tests/prostate"
    RT_structure_id = 158
    DP = DicomParser(DICOM_path, RT_structure_id)

    # Contourage prostate
    contourage_prostate = DP.get_DICOM_contourage(ROI_id=5, slice_id=149)

    # Affichage
    DP.afficher_DICOM("Contourage prostate", slice_id=149, contourage=contourage_prostate)


def test_5():
    """ Test affichage plusieurs organes """
    # Parametres et instanciation
    filename_header = "prostate"
    DICOM_path = "/home/thibault/stage_CELIA/src/tests/data_tests/prostate"
    RT_structure_id = 158
    DP = DicomParser(DICOM_path, RT_structure_id)
    
    # Contourage prostate
    contourages_array = []
    DP.add_contourage_plot(contourages_array, 149, 5, "green")

    # Contourage OAR
    DP.add_contourage_plot(contourages_array, 149, 6, "orange")
    DP.add_contourage_plot(contourages_array, 149, 7, "orange")
    DP.add_contourage_plot(contourages_array, 149, 8, "orange")

    # Affichage
    DP.afficher_DICOM("Contourage prostate (vert) + OAR (orange)", slice_id=149, contourages_array=contourages_array)

    
def test_6():
    """ Test generation à partir de DICOM """
    # Parametres et instanciation
    filename_header = "prostate"
    DICOM_path = "/home/thibault/stage_CELIA/src/tests/data_tests/prostate"
    RT_structure_id = 158
    DP = DicomParser(DICOM_path, RT_structure_id)
    zone_influence = 50 # 50 pixels ~ 50 mm ~ 5 cm

    # Contourage prostate
    contourage_prostate = DP.get_DICOM_contourage(ROI_id=5, slice_id=149)

    # Generation
    DP.generate_DICOM_don(filename_header, 149, contourage_prostate, zone_influence, affichage=True)


def test_7():
    """ Après avoir calculé la matrice des doses, on l'affiche """
    # Parametres et instanciation
    filename_header = "prostate"
    DICOM_path = "/home/thibault/stage_CELIA/src/tests/data_tests/prostate"
    RT_structure_id = 158
    DP = DicomParser(DICOM_path, RT_structure_id)
    slice_id=149
    zone_influence = 50 # 50 pixels ~ 50 mm ~ 5 cm
    granularite_source = 5
    (lf, mf, nf) = DP.n_points

    # Contourage prostate
    contourage = DP.get_DICOM_contourage(ROI_id=5, slice_id=149)

    # Densite
    HU_array = DP.get_DICOM_hounsfield(slice_id)
    densite = DP.get_DICOM_densite(slice_id)

    # Sources
    appartenance_contourage = get_appartenance_contourage(DP.n_points, DP.maillage, contourage)
    sources = get_sources(granularite_source, DP.n_points, appartenance_contourage, densite)

    # Domaine minimal
    domaine = get_domaine_minimal(sources, DP.n_points, DP.dimensions, DP.maillage, zone_influence)
    print domaine

    # Recuperation de la dose
    filename = "./data_tests/resultats_prostate/prostate_dose_source_001.dat"
    f = open(filename, "r")
    get_header_info(f)
    domaine_n_points = get_domaine_n_points(domaine, DP.n_points)
    domaine_dose_matrix = get_dose(f, domaine_n_points)
    #domaine_dose_matrix = np.fliplr(domaine_dose_matrix)
    #domaine_dose_matrix = np.flipud(domaine_dose_matrix)
    dose_matrix = np.zeros([lf, mf])
    dose_matrix = domaine_to_matrix(dose_matrix, domaine_dose_matrix, domaine)
    #dose_matrix = np.flipud(dose_matrix)
    #dose_matrix = np.fliplr(dose_matrix)

    # Affichage
    DP.afficher_DICOM("Affichage des doses", slice_id, dose_matrix=dose_matrix, contourage=contourage, sources=sources, domaine=domaine)


def test_8():
    """ Après avoir calculé la matrice des doses, on l'affiche """
    # Parametres et instanciation
    filename_header = "prostate"
    DICOM_path = "/home/thibault/stage_CELIA/src/tests/data_tests/prostate"
    RT_structure_id = 158
    DP = DicomParser(DICOM_path, RT_structure_id)
    slice_id=149
    zone_influence = 50 # 50 pixels ~ 50 mm ~ 5 cm
    granularite_source = 5
    (lf, mf, nf) = DP.n_points

    # Contourage prostate
    contourage = DP.get_DICOM_contourage(ROI_id=5, slice_id=149)

    # Densite
    HU_array = DP.get_DICOM_hounsfield(slice_id)
    densite = DP.get_DICOM_densite(slice_id)

    # Sources
    appartenance_contourage = get_appartenance_contourage(DP.n_points, DP.maillage, contourage)
    sources = get_sources(granularite_source, DP.n_points, appartenance_contourage, densite)

    # Domaine minimal
    domaine = get_domaine_minimal(sources, DP.n_points, DP.dimensions, DP.maillage, zone_influence)
    domaine_n_points = get_domaine_n_points(domaine, DP.n_points)
    
    # Recuperation et fusion de doses
    filename_head = "/home/thibault/stage_CELIA/src/tests/data_tests/resultats_prostate/prostate"
    vecteur_sources = [1, 2, 3]
    domaine_dose_matrix = get_dose_matrix_merged(filename_head, vecteur_sources, domaine_n_points)
    dose_matrix = np.zeros([lf, mf])
    dose_matrix = domaine_to_matrix(dose_matrix, domaine_dose_matrix, domaine)
    
    # Affichage
    DP.afficher_DICOM("Affichage des doses", slice_id, dose_matrix=dose_matrix, contourage=contourage, sources=sources, domaine=domaine)


def test_9():
    """ Test import """
    DICOM_path = "/home/thibault/stage_CELIA/src/tests/data_tests/prostate"
    DP = DicomParser(DICOM_path)
        

def main():
    #test_1()
    #test_2()
    #test_3()
    #test_4()
    #test_5()
    #test_6()
    #test_7()
    #test_8()
    #test_9()
    
if __name__ == "__main__":
    main()
