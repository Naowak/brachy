# -*- coding: utf-8 -*-
import sys
import scipy
import numpy as np
import matplotlib.pyplot as plt


# Paramètres globaux
DENSITE_SEUIL = 1.5


def get_maillage(n_points, dimensions):
    """ Fournit un maillage uniforme python en fonction des paramètres
    [Return] Un triplet de trois tableaux (xm, ym, zm) correspondant au maillage 

    [Params]
    n_points : triplet (x, y, z) qui définit le maillage
    dimensions : triplet (x, y, z) qui définit les dimensions
    """
    (lf, mf, nf) = n_points
    (Lx, Ly, Lz) = dimensions
    coord = np.array([0, Lx, 0, Ly, 0, Lz])

    xm = np.linspace(coord[0], coord[1], lf)
    ym = np.linspace(coord[2], coord[3], mf)
    zm = np.linspace(coord[4], coord[5], nf)

    return (xm, ym, zm)


def get_densite(x, y, z):
    """ Recupere la densite aux coordonnées x, y, z
    [Return] Un float correspond à la densité en un point
    (si le point précis n'est pas défini, on prend la densité la plus proche)

    [Params]
    x, y, z les coordonnées du point
    """

    return 1
    

def ajouter_header(f, n_points, dimensions):
    """ Ajoute le header au fichier de configuration passé en paramètres
    Précondition : 2D

    [Params]
    f : descripteur de fichier
    n_points : triplet (x, y) qui définit le maillage
    dimensions : triplet (x, y) qui définit les dimensions
    """
    (lf, mf, nf) = n_points
    (Lx, Ly, Lz) = dimensions
    
    res = "-M1\n"
    res += "-lf " + str(lf) + "\n"
    res += "-mf " + str(mf) + "\n" 
    res += "-Lx " + str(Lx) + "\n"
    res += "-Ly " + str(Ly) + "\n"
    res += "-2d\n"
    res += "-ordre 1\n"
    res += "-n_groupe_particules 2\n"
    res += "-group 1 e-\n"
    res += "-group 2 g\n"
    res += "-n_cycles 1200\n"
    res += "-seuil_residu 1.e-1\n"
    res += "-b_maximum\n"
    res += "-densite constante 1.0\n"

    f.write(res)


def ajouter_footer(f):
    """ Ajoute le footer au fichier de configuration passé en paramètres """
    res = "-GS_para_alea\n"
    res += "-python\n\n"
    res += "fin fichier KIDS\n\n"
    res += "title\n"
    res += "  cepxs regression test\n"
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

    # Quelques exemples de materiaux
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
    

def lancer_generation(filename, n_sources, n_points, dimensions):
    """ Lance la generation d'un fichier de configuration .don
    On place n_sources sources réparties uniformement sur le maillage
    (si n_sources ne permet pas une répartition uniforme on ajuste en conséquence,
     il peut donc y avoir une source en moins que prévue)

    [Params]
    filename : nom du fichier de configuration
    n_sources : nombre de sources
    n_points : triplet (x, y) qui définit le maillage
    dimensions : triplet (x, y) qui définit les dimensions
    """
    (lf, mf, nf) = n_points
    (Lx, Ly, Lz) = dimensions

    # Maillage
    (maillage_x, maillage_y, maillage_z) = get_maillage(n_points, dimensions)
    z = Lx/2.0

    # Calcul de la repartition (naive)
    nb_total_points = lf * mf
    pas_source = int(float(nb_total_points) / float(n_sources))
    groupe = 1
    index = 1

    # Ecriture du fichier de configuration .don
    f  = open(filename, "w")

    ajouter_header(f, n_points, dimensions)
    
    for y in maillage_y:
        for x in maillage_x:
            # On ajoute une source à chaque fois que le pas est atteint et densite coherente
            if (index >= pas_source and get_densite(x, y, z) <= DENSITE_SEUIL):
                ajouter_source(f, groupe, "g", (0., 0., 0.), (x, y, z, 0.1), (1e20, 0.03))
                groupe += 1
                index = 0
            else:
                index += 1
    
    ajouter_footer(f)

    f.close()


def usage(argv):
    if (len(sys.argv) != 3): 
        err_msg = "Usage : python generate_multisource.py filename n_sources\n"
        sys.stderr.write(err_msg)
        sys.exit(1)


def main():
    #usage(sys.argv)
    # Simulation d'appel (à supprimer après dev)
    filename = "multisources.don"
    n_sources = 50
    
    # Parametres
    lf = 50
    mf = 50
    nf = 1
    Lx = 5
    Ly = 5
    Lz = 1
    n_points = (lf, mf, nf)
    dimensions = (Lx, Ly, Lz)

    # Generation
    lancer_generation(filename, n_sources, n_points, dimensions)


if __name__ == "__main__":
    main()

    

    

