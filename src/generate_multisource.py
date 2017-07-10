# -*- coding: utf-8 -*-
import sys
import numpy as np
import matplotlib.pyplot as plt
from contourage import *


# Paramètres globaux
DENSITE_SEUIL = 1.8


###########################  Repartition des sources ###########################


def get_maillage(n_points, dimensions):
    """ Fournit un maillage uniforme en fonction des paramètres
    [Return] Un triplet de trois tableaux (xm, ym, zm) correspondant au maillage 

    [Params]
    n_points : triplet (x, y, z) qui définit le nombre de points par axe
    dimensions : triplet (x, y, z) qui définit les dimensions (cm/mm)
    """
    # Recuperation des informations
    (lf, mf, nf) = self.n_points
    (Lx, Ly, Lz) = self.dimensions
    taille_maille_x = Lx / lf
    taille_maille_y = Ly / mf

    # Les coordonnees du maillage "pointent" le centre chaque maille (taille_maill/2)
    xm = np.linspace(0 + taille_maille_x/2.0, Lx - taille_maille_x/2.0, lf)
    ym = np.linspace(0 + taille_maille_y/2.0, Ly - taille_maille_y/2.0, mf)
    zm = np.linspace(0, Lz, nf)
    maillage = (xm, ym, zm)
    
    return maillage


def get_densite_fantome_eau(n_points):
    """ Retourne la densite d'un fantome d'eau (1 partout)
    [Return] Un tableau de float 2D qui indique la densite en chaque point du maillage

    [Params]
    - n_points : triplet (x, y, z) qui définit le nombre de points par axe

    [Complexite] O(n)
    """
    # Recuperation parametres
    (lf, mf, nf) = n_points

    # Recuperation de la densite
    densite = np.array([[1] * mf] * lf)

    return densite


def densite_valide(densite, x, y):
    """ Indique si la densite en un point est valide pour placer une source ou non
    [Return] True si densite valide, False sinon
    NB : la densite est considérée comme valide si elle est inferieure à DENSITE_SEUIL
    
    [Params]
    - densite : tableau de float 2D retourné par get_densite
    - x, y indiquant les coordonnées dans le maillage

    [Compllexité] O(1)
    """
    return densite[x, y] <= DENSITE_SEUIL


def get_sources(granularite_source, n_points, appartenance_contourage, densite):
    """ Retourne une séquence de points correspondant aux sources à positionner sur le maillage
    [Return] Une sequence de points (x, y) qui correspond aux coordoonees des sources dans le maillage

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

    # Calcul de la repartition (naive)
    sous_maillage_x = np.arange(0, lf, granularite_source)
    sous_maillage_y = np.arange(0, mf, granularite_source)
    
    # Repartition uniforme des sources
    for x in sous_maillage_x:
        for y in sous_maillage_y:
            # Ajout de source si dans contourage et densite valide
            if (in_contourage(appartenance_contourage, x, y) and densite_valide(densite, x, y)):
                sources.append([x, y])

    return np.array(sources)


def get_coord_sources(sources, maillage):
    """ Recupere les coordoonnees reelles des sources """
    # Recuperation parametres
    (maillage_x, maillage_y, maillage_z) = maillage
    
    # Recuperation des coordonnees exactes a partir du maillage
    coord_sources = []
    
    for source in sources:
        coord_source = (maillage_x[source[0]], maillage_y[source[1]])
        coord_sources.append(coord_source)

    return np.array(coord_sources)
    

########################### Mise en forme .don ###########################


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

    f.write(res)


def ajouter_densite(f, filename_header="constante"):
    if (filename_header == "constante"):
        res = "-densite constante 1.0\n"
    else:
        res = "-densite lu_HU " + "densite_hu_" + filename_header + ".don\n"

    f.write(res)


def ajouter_footer(f):
    """ Ajoute le footer au fichier de configuration passé en paramètres """
    res = "-GS_para_alea\n"
    res += "-python\n"
    res += "-nofusion\n\n"
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
    volume_shere : un octuplet (x, y, z, rx, ry, rz) avec r_ le rayon de la sphère selon les axes
    spectre_mono : un couple (I0, espilon0) ; on injecte à l'énergie epsilon0 avec l'intensité I0
    """
    res = "-frontiere groupe " + str(groupe) + "\n"
    res += "-frontiere type_de_particule " + str(type_particule) + "\n"
    res += "-frontiere direction_M1 " + str(direction_M1[0]) + " " + str(direction_M1[1]) + \
           " " +  str(direction_M1[2]) + "\n"
    res += "-frontiere volume_sphere " + str(volume_sphere[0]) + " " + str(volume_sphere[1]) + \
           " " + str(volume_sphere[2]) + " " + str(volume_sphere[3]) + " " + \
           str(volume_sphere[4]) + " " + str(volume_sphere[5]) + "\n" 
    res += "-frontiere spectre_mono " + str(spectre_mono[0]) + " " + str(spectre_mono[1]) + "\n"

    f.write(res)
    

def lancer_generation(filename_header, sources, n_points, dimensions, rayon, direction_M1, spectre_mono, densite_lu=False):
    """ Lance la generation d'un fichier de configuration .don
    On place n_sources sources réparties uniformement sur le maillage
    Une source est placée si elle est située dans la zone contourée avec une densité cohérente
    (si n_sources ne permet pas une répartition uniforme on ajuste en conséquence,
     il peut donc y avoir une source en moins que prévue)

    [Params]
    - filename_header : nom du fichier de configuration
    - n_points : triplet (x, y, z) qui définit le nombre de points par axe
    - dimensions : triplet (x, y, z) qui définit les dimensions en cm
    - rayon : triplet (rx, ry, rz) qui indique le rayon des volumes selon chaque axe
    - direction_M1 : un triplet (x, y, z) avec f1 = f0 * [x, y, z]
    - spectre_mono : un couple (I0, espilon0) ; on injecte à l'énergie epsilon0 avec l'intensité I0

    [Complexité] O(n * log n)
    """
    # Recuperation parametres
    (lf, mf, nf) = n_points
    (Lx, Ly, Lz) = dimensions
    (rx, ry, rz) = rayon

    # ID slice (choix arbitraire)
    z = Lx/2.0

    # Ecriture du fichier de configuration .don
    f  = open(filename_header + ".don", "w")

    ajouter_header(f, n_points, dimensions)

    if (densite_lu):
        ajouter_densite(f, filename_header=filename_header)
    else:
        ajouter_densite(f, filename_header="constante")

    # On ajoute les sources dans le fichier .don
    groupe = 1
    for source in sources:
        volume_sphere = (source[0], source[1], z, rx, ry, rz)
        ajouter_source(f, groupe, "g", direction_M1, volume_sphere, spectre_mono)
        groupe += 1
                    
    ajouter_footer(f)

    print filename_header + ".don successfully generated"
    f.close()


########################### Affichage ###########################


def plot_sources(n_points, dimensions, maillage, sources, contourage, polygon_domaine=None):
    """ Affiche les sources qui sont ajoutées dans le fichier de configuration
    [Params]
    - n_points : triplet (x, y, z) qui définit le nombre de points par axe
    - dimensions : dimensions : triplet (x, y, z) qui définit les dimensions en cm
    - maillage : triplet (maillage_x, maillage_y, maillage_z) qui représente le maillage
    - sources : tableau 1D retourné par get_sources
    - contourage : sequence de points representant un polygone
    - polygon_domaine : une sequence de cinq points (rectangle) representant le domaine minimal
                        (les coordonnees doivent etre reelles et pas les indices de maillage)

    [Complexité] O(n)
    """
    # Recuperation parametres
    (lf, mf, nf) = n_points
    (Lx, Ly, Lz) = dimensions
    n_sources = len(sources)
    contourage = contourage[:,(0,1)] # On garde seulement 2D pour utiliser mp.Path

    # Affichage du contourage
    contourage_path = mp.Path(contourage)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    patch = patches.PathPatch(contourage_path, facecolor='orange', lw=2)
    ax.set_xlim([0, Lx])
    ax.set_ylim([0, Ly])
    ax.add_patch(patch)

    coord_sources = get_coord_sources(sources, maillage)

    # Affichage des sources
    plt.plot(coord_sources[:,0], coord_sources[:,1], color='b', marker='o', linestyle='None')

    # Affichage du domaine
    if (polygon_domaine is not None):
        domaine_path = mp.Path(polygon_domaine)
        patch_domaine = patches.PathPatch(domaine_path, facecolor='None', lw=3)
        ax.add_patch(patch_domaine)

    plt.show()


########################### Main ###########################


def usage(argv):
    if (len(sys.argv) != 3): 
        err_msg = "Usage : python generate_multisource.py filename_header granularite_source DICOM_path\n"
        sys.stderr.write(err_msg)
        sys.exit(1)


def main():
    #usage(sys.argv)
    # Pour lancer artificiellement avec des données cf. test_generate_multisource
    return 0

if __name__ == "__main__":
    main()

    

    

