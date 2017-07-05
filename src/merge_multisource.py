# -*- coding: utf-8 -*-
import sys
import numpy as np
import matplotlib.pyplot as plt


def lancer_fusion(filename_head, vecteur_sources):
    """ Fusionne des fichiers de données .dat représentant des dépots de source

    [Params]
    filename_head : chaine de caractère représentant l'en-tete des sources à fusionner
    (les fichiers sources doivent etre generes avec l'option -nofusion
     de la forme filename_head_dose_source_xxx)
    vecteur_sources : vecteur dont les valeurs representent les sources à fusionner
    """
    # Premiere source
    current_filename = filename_head + "_dose_source_" + \
                       str(vecteur_sources[0]).zfill(3) + ".dat"
    res = np.genfromtxt(current_filename)
    sum_dose = res[:,3]

    # On parcourt les sources et on fait leur fusion
    for source_number in vecteur_sources[1:]:
        current_filename = filename_head + "_dose_source_" + \
                           str(source_number).zfill(3) + ".dat"
        sum_dose += np.genfromtxt(current_filename)[:,3]

    # Mise a jour avec la somme de dose de toutes les sources
    res[:,3] = sum_dose

    # Recuperation de l'en-tete
    fd_lecture = open(current_filename, "r")
    head = ""
    for i in range(10):
        head += fd_lecture.readline()
    head = head.rstrip() # Suppression du saut de ligne

    # Sauvegarde de la fusion
    filename = filename_head + "_dose_fusion.dat"
    np.savetxt(filename, res, header=head, footer='\n', comments='', newline='\n')

    print filename + " successfully generated"

    fd_lecture.close()
    

########################### Main ###########################


def usage(argv):
    if (len(sys.argv) != 3): 
        err_msg = "Usage : python generate_multisource.py filename_head vecteur_sources\n"
        err_msg += "filename_head : chaine de caractère représentant l'en-tete des sources à \
        fusionner (les fichiers sources doivent etre generes avec l'option -nofusion de la \
        forme filename_head_dose_source_xxx)"
        sys.stderr.write(err_msg)
        sys.exit(1)
    elif (len(vecteur_sources) < 2):
        err_msg = "Usage : python generate_multisource.py filename_head vecteur_sources\n"
        err_msg += "vecteur_sources doit etre de taille 2 au minimum"
        err_msg += "filename_head : chaine de caractère représentant l'en-tete des sources à \
        fusionner (les fichiers sources doivent etre generes avec l'option -nofusion de la \
        forme filename_head_dose_source_xxx)"
        sys.stderr.write(err_msg)
        sys.exit(1)


def main():
    usage(sys.argv)
    filename_head = sys.argv[1]
    vecteur_sources = sys.argv[2]
    lancer_fusion(filename_head, vecteur_sources)
    

if __name__ == "__main__":
    main()
