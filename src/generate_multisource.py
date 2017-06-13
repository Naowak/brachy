# -*- coding: utf-8 -*-
import sys
import scipy
import numpy as np
import matplotlib.pyplot as plt



def ajouter_header(f, n_points, dimension):
    """ Ajoute une source au fichier de configuration passé en paramètres
    Précondition : 2D

    """
    res = "-M1\n"
    res += "-lf " + str(n_points[0]) + "\n"
    res += "-mf " + str(n_points[1]) + "\n" 
    res += "-Lx " + str(dimension[0]) + "\n"
    res += "-Ly " + str(dimension[1]) + "\n"
    res += "-2d\n"
    res += "-ordre 1\n"
    res += "-n_groupe_particules 2\n"
    res += "-group 1 e-\n"
    res += "-group 2 g\n"
    res += "-n_cycles 1200\n"
    res += "-seuil_residu 1.e-1\n"
    res += "-b_maximum\n"
    res += "-densite spheroid 1 2.5 2.5 0.1 0.2 1\n"

    f.write(res)


def ajouter_footer(f):
    """ Todo : parametres en option """
    res = "fin fichier KIDS"
    res += "\n\ntitle\n"
    res += " cepxs regression test\n"
    res += "first-order\n"
    res += "energy 0.035\n"
    res += "cutoff 0.001\n"
    res += "legendre 8\n"
    res += "electron-source\n"
    res += " full-coupling\n"
    res += "electrons\n"
    res += " linear 30\n"
    res += "photons\n"
    res += " linear 30\n"
    res += " no-lines\n"
    res += "material H .1111 O .8889\n"
    res += " density 1.\n"
    res += "material Ti 1.0\n"
    res += " density 4.507\n"
    res += "material N 1.0\n"
    res += " density 0.001\n"
    res += "material Ag 1.0\n"
    res += " density 10.490\n"
    res += "material Ti .282 N .082 Ag .635\n"
    res += " density 3.5832\n"
    res += "material H .1111 O .8889\n"
    res += " density 4.507\n"

    f.write(res)


def ajouter_source(f, groupe, type_particule, direction_M1, volume_sphere, spectre_mono):
    """ Ajoute une source au fichier de configuration passé en paramètres

    [Params]
    f : descripteur de fichier
    groupe : numéro du groupe de calcul
    direction_M1 : un triplet (x, y, z) avec f1 = f0 * [x, y, z]
    volume_shere : un quadruplet (x, y, z, r) avec r le rayon de la sphère
    spectre_mono : un couple (I0, espilon0) ; on injecte à l'énergie epsilon0 avec l'intensité I0
    """
    res = "-frontiere groupe " + str(groupe) + "\n"
    res += "-frontiere type_de_particule " + str(type_particule) + "\n"
    res += "-frontiere direction_M1 " + str(direction_M1[0]) + " " + str(direction_M1[1]) + \
           " " +  str(direction_M1[2]) + "\n"
    res += "-frontiere volume_sphere " + str(volume_sphere[0]) + " " + str(volume_sphere[1]) + \
           " " + str(volume_sphere[2]) + " " + str(volume_sphere[3]) + "\n"
    res += "-frontiere spectre_mono " + str(spectre_mono[0]) + " " + str(spectre_mono[1]) + "\n"

    f.write(res)
    


def lancer_generation(filename, n_sources):
    """ Lance la generation d'un fichier .don
    On place n_sources sources réparties uniformement sur le maillage

    n_sources : nombre de sources
    (si n_sources ne permet pas une répartition uniforme on le modifie en conséquence)
    """
    # Params
    lf = 50
    mf = 50
    Lx = 5
    Ly = 5

    # Calcul de la repartition
    # Todo

    
    f  = open(filename, "w")

    ajouter_header(f, (lf, mf), (Lx, Ly))
    ajouter_source(f, 1, "g", (0., 0., 0.), (1.5, 1.5, 1.5, 0.1), (1e20, 0.03))
    ajouter_footer(f)

    f.close()


def usage(argv):
    if (len(sys.argv) != 2): 
        err_msg = "Usage : python generate_multisource.py n_sources\n"
        sys.stderr.write(err_msg)
        sys.exit(1)


def main():
    #usage(sys.argv)
    lancer_generation("toto.don", 10)


if __name__ == "__main__":
    main()

    

    

