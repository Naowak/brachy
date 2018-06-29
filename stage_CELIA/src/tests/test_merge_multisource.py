# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
from dose_parser import *
from merge_multisource import *
from test_contourage import *


def test_1():
    """ Trois sources placées manuellement """
    # On affiche les trois sources calculées indépendamment
    filename = "./data_tests/resultats_3_sources/3_sources_dose_source_001.dat"
    afficher_dose(filename)

    filename = "./data_tests/resultats_3_sources/3_sources_dose_source_002.dat"
    afficher_dose(filename)

    filename = "./data_tests/resultats_3_sources/3_sources_dose_source_003.dat"
    afficher_dose(filename)
    
    # Puis on affiche leur fusion (des 3)
    filename_head = "./data_tests/resultats_3_sources/3_sources"
    vecteur_sources = [1, 2, 3]
    lancer_fusion(filename_head, vecteur_sources)
    filename = "./data_tests/resultats_3_sources/3_sources_dose_fusion.dat"
    afficher_dose(filename)

    # On n'en fusionne que 2
    vecteur_sources = [1, 2]
    lancer_fusion(filename_head, vecteur_sources)
    filename = "./data_tests/resultats_3_sources/3_sources_dose_fusion.dat"
    afficher_dose(filename)


def test_2():
    """ Sources placées dans un polygone convexe """
    contourage = pol_convexe
    
    # On affiche quelques sources calculées indépendamment
    filename = "./data_tests/resultats_multisource_convexe/multisource_convexe_dose_source_025.dat"
    afficher_dose(filename)

    filename = "./data_tests/resultats_multisource_convexe/multisource_convexe_dose_source_050.dat"
    afficher_dose(filename)

    filename = "./data_tests/resultats_multisource_convexe/multisource_convexe_dose_source_100.dat"
    afficher_dose(filename)

    filename = "./data_tests/resultats_multisource_convexe/multisource_convexe_dose_source_200.dat"
    afficher_dose(filename)

    # Fusion des sources
    filename_head = "./data_tests/resultats_multisource_convexe/multisource_convexe"
    vecteur_sources = [25, 50, 100, 200]
    lancer_fusion(filename_head, vecteur_sources)
    filename = "./data_tests/resultats_multisource_convexe/multisource_convexe_dose_fusion.dat"
    afficher_dose(filename, contourage=contourage)



def main():
    test_1()
    #test_2()


if __name__ == "__main__":
    main()
