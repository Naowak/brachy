# -*- coding: utf-8 -*-
import sys
import numpy as np
import matplotlib.pyplot as plt

from dose_parser import *

def get_merged_file(filename_header, vecteur_sources):    
    # Premiere source
    current_filename = filename_header + "dose_source_" + \
                       str(vecteur_sources[0]).zfill(4) + ".dat"
    res = np.genfromtxt(current_filename)
    sum_dose = res[:,3]

    # On parcourt les sources et on fait leur fusion
    for source_number in vecteur_sources:
        current_filename = filename_head + "dose_source_" + \
                           str(source_number).zfill(4) + ".dat"
        sum_dose += np.genfromtxt(current_filename)[:,3]

    # Mise a jour avec la somme de dose de toutes les sources

    res[:,3] = sum_dose

    return res


def get_dose_matrix_merged(filename_head, vecteur_sources, n_points):
    merged_file = get_merged_file(filename_head, vecteur_sources)
    
    (lf, mf, nf) = n_points
    dose_matrix = np.zeros([lf, mf])
    index_merged_file = 0

    for i in range (lf):
        
        d = np.zeros([mf])

        for j in range (mf):
            a = merged_file[index_merged_file]
            d[j] = a[3]
            index_merged_file += 1

        dose_matrix[i,:] = d[:]

    return dose_matrix


def dose_matrix_add_source(filename_head, dose_matrix, source_id):    
    # On recupere la matrice des doses de la source a ajouter
    filename_dose = filename_head + "dose_source_" + str(source_id).zfill(4) + ".dat"
    f = open(filename_dose, "r")
    (coord, dim_vector, n_points, maillage) = get_header_info(f)
    dose_matrix_toadd = get_dose(f, n_points)

    # Fusion a proprement parler (ajout de la source a dose_matrix)
    merged_dose_matrix = dose_matrix + dose_matrix_toadd

    return merged_dose_matrix


def dose_matrix_remove_source(filename_head, dose_matrix, source_id):
    # On recupere la matrice des doses de la source a ajouter
    filename_dose = filename_head + "dose_source_" + str(source_id).zfill(4) + ".dat"
    f = open(filename_dose, "r")
    (coord, dim_vector, n_points, maillage) = get_header_info(f)
    dose_matrix_toremove = get_dose(f, n_points)

    # On retire la source de dose_matrix
    merged_dose_matrix = dose_matrix - dose_matrix_toremove

    return merged_dose_matrix


def lancer_fusion(filename_head, vecteur_sources):
    """ Fusionne des fichiers de données .dat représentant des dépots de source

    [Params]
    filename_head : chaine de caractère représentant l'en-tete des sources à fusionner
    (les fichiers sources doivent etre generes avec l'option -nofusion
     de la forme filename_head_dose_source_xxx)
    vecteur_sources : vecteur dont les valeurs representent les sources à fusionner
    """
    # On fusionne les matrices correspondant aux sources dans vecteur sources
    merged_file = get_merged_file(filename_head, vecteur_sources)

    # Recuperation de l'en-tete
    fd_lecture = open(current_filename, "r")
    head = ""
    for i in range(10):
        head += fd_lecture.readline()
    head = head.rstrip() # Suppression du saut de ligne

    # Sauvegarde de la fusion
    filename = filename_head + "_dose_fusion.dat"
    np.savetxt(filename, merged_file, header=head, footer='\n', comments='', newline='\n')

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
