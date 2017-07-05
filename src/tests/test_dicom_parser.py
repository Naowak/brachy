# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
from dicom_parser import *
from dose_parser import *


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

    # Contourage prostate
    contourage_prostate = DP.get_DICOM_contourage(ROI_id=5, slice_id=149)

    # Generation
    DP.generate_DICOM_don(filename_header, 149, contourage_prostate)


def main():
    #test_1()
    #test_2()
    #test_3()
    #test_4()
    #test_5()
    #test_6()
    
    
if __name__ == "__main__":
    main()
