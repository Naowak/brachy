# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
from display_dose import *
from merge_multisource import *


def test_1():
    """ Trois sources placées manuellement """
    # On affiche les trois sources calculées indépendamment
    filename = "./data_tests/3_sources_dose_source_001.dat"
    lancer_affichage(filename)

    filename = "./data_tests/3_sources_dose_source_002.dat"
    lancer_affichage(filename)

    filename = "./data_tests/3_sources_dose_source_003.dat"
    lancer_affichage(filename)
    
    # Puis on affiche leur fusion (des 3)
    filename_head = "./data_tests/3_sources"
    vecteur_sources = [1, 2, 3]
    lancer_fusion(filename_head, vecteur_sources)
    filename = "./data_tests/3_sources_dose_fusion.dat"
    lancer_affichage(filename)

    # On n'en fusionne que 2
    vecteur_sources = [1, 2]
    lancer_fusion(filename_head, vecteur_sources)
    filename = "./data_tests/3_sources_dose_fusion.dat"
    lancer_affichage(filename)


def test_2():
    """ Sources issues de generate_multisource """
    filename_head = "/home/thibault/KIDS_4/workdir/multisource"
    vecteur_sources = [1, 2, 3]
    lancer_fusion(filename_head, vecteur_sources)


def main():
    test_1()


if __name__ == "__main__":
    main()
