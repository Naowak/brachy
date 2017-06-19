# -*- coding: utf-8 -*-
import sys
import numpy as np
import matplotlib.pyplot as plt
from contourage import *


# Paramètres globaux
DENSITE_SEUIL = 1.5


def get_maillage(n_points, dimensions):
    """ Fournit un maillage uniforme python en fonction des paramètres
    [Return] Un triplet de trois tableaux (xm, ym, zm) correspondant au maillage 

    [Params]
    n_points : triplet (x, y, z) qui définit le nombre de points par axe
    dimensions : triplet (x, y, z) qui définit les dimensions en cm
    """
    (lf, mf, nf) = n_points
    (Lx, Ly, Lz) = dimensions
    coord = np.array([0, Lx, 0, Ly, 0, Lz])

    xm = np.linspace(coord[0], coord[1], lf)
    ym = np.linspace(coord[2], coord[3], mf)
    zm = np.linspace(coord[4], coord[5], nf)
    maillage = (xm, ym, zm)
    
    return maillage


def get_densite(n_points):
    """ Lit la densite dans le fichier DICOM
    [Return] Un tableau de float 2D qui indique la densite en chaque point du maillage

    [Params]
    - n_points : triplet (x, y, z) qui définit le nombre de points par axe
    NB : pour le moment on considere que la densite vaut 1 en chaque point

    [Complexite] O(n)
    """
    # Recuperation parametres
    (lf, mf, nf) = n_points

    # Recuperation de la densite
    densite = np.array([[1] * mf] * lf)

    return densite


def densite_valide(x, y, densite):
    """ Indique si la densite en un point est valide pour placer une source ou non
    [Return] True si densite valide, False sinon
    NB : la densite est considérée comme valide si elle est inferieure à DENSITE_SEUIL
    
    [Params]
    - x, y indiquant les coordonnées dans le maillage
    - densite : tableau de float 2D retourné par get_densite

    [Compllexité] O(1)
    """
    return densite[x, y] <= DENSITE_SEUIL


def get_sources(granularite_source, n_points, appartenance_contourage, densite):
    """ Retourne une séquence de points correspondant aux sources à positionner sur le maillage
    [Return] Une sequence de points (x, y)

    [Params]
    - granularite_source : nombre de mailles (pas) qu'on parcourt au mini entre chaque source
    - n_points : triplet (x, y, z) qui définit le nombre de points par axe
    - appartenance_contourage : tableau de booleen 2D retourné par get_appartenance_contourage
    - densite : tableau de float 2D retourné par get_densite
    
    [Complexite] O(n)
    """
    # Recuperation parametres
    (lf, mf, nf) = n_points
    sources = [] # Tableau 1D de points
    index_sources = 1

    # Calcul de la repartition (naive)
    sous_maillage_x = np.arange(0, lf, granularite_source)
    sous_maillage_y = np.arange(0, mf, granularite_source)
    
    # Repartition uniforme des sources
    for x in sous_maillage_x:
        for y in sous_maillage_y:
            # Ajout de source si dans contourage et densite valide
            if (in_contourage(x, y, appartenance_contourage) and densite_valide(x, y, densite)):
                sources.append([x, y])
                index_sources += 1

    return np.array(sources)


def plot_sources(n_points, dimensions, maillage, sources, contourage):
    """ Affiche les sources qui sont ajoutées dans le fichier de configuration
    [Params]
    - n_points : triplet (x, y, z) qui définit le nombre de points par axe
    - dimensions : dimensions : triplet (x, y, z) qui définit les dimensions en cm
    - maillage : triplet (maillage_x, maillage_y, maillage_z) qui représente le maillage
    - sources : tableau 1D retourné par get_sources
    - contourage : sequence de points representant un polygone

    [Complexité] O(n)
    """
    # Recuperation parametres
    (lf, mf, nf) = n_points
    (Lx, Ly, Lz) = dimensions
    (maillage_x, maillage_y, maillage_z) = maillage
    n_sources = len(sources)

    # Affichage du contourage
    contourage_path = mp.Path(contourage)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    patch = patches.PathPatch(contourage_path, facecolor='orange', lw=2)
    ax.set_xlim([0, Lx])
    ax.set_ylim([0, Ly])
    ax.add_patch(patch)

    # Recuperation des coordonnées associées
    coord_sources = np.zeros([n_sources, 2])

    for i in range(n_sources):
        (x, y) = sources[i]
        coord_sources[i] = (maillage_x[x], maillage_y[y])

    # Affichage des sources
    plt.plot(coord_sources[:,0], coord_sources[:,1], color='b', marker='o', linestyle='None')

    plt.show()
    

def ajouter_header(f, n_points, dimensions):
    """ Ajoute le header au fichier de configuration passé en paramètres
    Précondition : 2D

    [Params]
    f : descripteur de fichier
    n_points : triplet (x, y, z) qui définit le nombre de points par axe
    dimensions : triplet (x, y, z) qui définit les dimensions en cm
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
    

def lancer_generation(filename, granularite_source, contourage, n_points, dimensions, rayon, direction_M1, spectre_mono):
    """ Lance la generation d'un fichier de configuration .don
    On place n_sources sources réparties uniformement sur le maillage
    Une source est placée si elle est située dans la zone contourée avec une densité cohérente
    (si n_sources ne permet pas une répartition uniforme on ajuste en conséquence,
     il peut donc y avoir une source en moins que prévue)

    [Params]
    - filename : nom du fichier de configuration
    - granularite_source : nombre de mailles (pas) qu'on parcourt au mini entre chaque source
    - contourage : sequence de points (x, y) representant un polygone
    - n_points : triplet (x, y, z) qui définit le nombre de points par axe
    - dimensions : triplet (x, y, z) qui définit les dimensions en cm
    - direction_M1 : un triplet (x, y, z) avec f1 = f0 * [x, y, z]
    - spectre_mono : un couple (I0, espilon0) ; on injecte à l'énergie epsilon0 avec l'intensité I0

    [Complexité] O(n * log n)
    """
    # Recuperation parametres
    (Lx, Ly, Lz) = dimensions

    # Maillage
    maillage = get_maillage(n_points, dimensions)
    (maillage_x, maillage_y, maillage_z) = maillage
    z = Lx/2.0 # Choix arbitraire

    # Repartition des sources
    appartenance_contourage = get_appartenance_contourage(n_points, maillage, contourage)
    densite = get_densite(n_points)
    sources = get_sources(granularite_source, n_points, appartenance_contourage, densite)

    # Ecriture du fichier de configuration .don
    f  = open(filename, "w")

    ajouter_header(f, n_points, dimensions)

    # On ajoute les sources dans le fichier .don
    groupe = 1
    for source in sources:
        (x, y) = source
        volume_sphere = (maillage_x[x], maillage_y[y], z, rayon)
        ajouter_source(f, groupe, "g", direction_M1, volume_sphere, spectre_mono)
        groupe += 1
                    
    
    ajouter_footer(f)

    print filename + " successfully generated"

    f.close()


def usage(argv):
    if (len(sys.argv) != 3): 
        err_msg = "Usage : python generate_multisource.py filename granularite_source DICOM_path\n"
        sys.stderr.write(err_msg)
        sys.exit(1)


def main():
    #usage(sys.argv)
    # Pour lancer artificiellement avec des données cf. test_generate_multisource
    return 0

if __name__ == "__main__":
    main()

    

    

