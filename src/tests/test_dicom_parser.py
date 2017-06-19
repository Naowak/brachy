# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
from dicom_parser import *
from display_dose import *


def main():
    DICOM_path = "./data_tests/my_head"
    DICOM_files = get_DICOM_files(DICOM_path)
    DICOM_slice = get_DICOM_slice(DICOM_files, 140)
    afficher_DICOM(DICOM_slice)
    

if __name__ == "__main__":
    main()
