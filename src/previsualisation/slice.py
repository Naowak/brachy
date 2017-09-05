#!/usr/bin/env python
# -*- coding: utf-8 -*-
# slice.py
""" Classe permettant de gérer une slice """
# Author : Thibault PARPAITE, Cyrille BEAUCHESNE
# Copyright (c) 2017, CELIA Bordeaux
# This file is part of cythi, released under a BSD license.

import os
import dicom
import numpy as np
import matplotlib.pyplot as plt

from contourage import *
from zone_influence import *
from generate_multisource import *
from merge_multisource import *

class Slice:
    """
    Cette classe représente une slice
    Elle permet de garder en mémoire les informations propres à une slice après le parsing
    Elle permet également de gérer la prévisualisation faite depuis la GUI
    """
    def __init__(self, parent, dicom_slice, slice_id, dicomparser):
        self.parent = parent
        self.dicom_slice = dicom_slice
        self.slice_id = slice_id
        self.dicomparser = dicomparser
        self.initialize()


    def initialize(self):
        # Metadata
        self.position = self.dicom_slice.SliceLocation

        # Densite
        self.pixel_array = self.dicom_slice.pixel_array
        self.densite = None
        self.HU_array = None

        # Contourage
        self.ROI_id = None
        self.contourages = None
        self.appartenance_contourage_cible = None

        # Informations sur l'etat courant
        self.dose_mode = 0
        self.calculs_en_cours = 0

        # Sources, domaine, matrice dose
        self.sources = None
        self.slice_directory = None
        self.dic_sources_displayed = {}
        self.domaine = None
        self.dose_matrix = None


    def get_slice_id(self):
        return self.slice_id


    def get_pixel_array(self):
        return self.dicom_slice.pixel_array


    def get_HU_array(self):
        return self.HU_array


    def get_appartenance_contourage(self, ROI_id):
        return self.contourages[ROI_id]['appartenance_contourage']


    def get_dose_mode(self):
        return self.dose_mode
    

    def get_dose_matrix(self):
        return self.dose_matrix


    def get_densite(self):
        return self.densite


    def get_sources(self):
        return self.sources

    
    def get_dic_sources_displayed(self):
        return self.dic_sources_displayed


    def get_contourages(self):
        return self.contourages


    def get_domaine(self):
        return self.domaine


    def get_slice_directory(self):
        return self.slice_directory


    def get_calculs_en_cours(self):
        return self.calculs_en_cours


    def set_calculs_en_cours(self, value):
        self.calculs_en_cours = value
    

    def set_working_directory(self, working_directory):
        """ C'est le répertoire où sont stockés les calculs """
        self.slice_directory = working_directory + "/slice_" + str(self.slice_id).zfill(3)

        # Creation du repertoire pour la slice s'il n'existe pas deja
        if not os.path.exists(self.slice_directory):
            os.makedirs(self.slice_directory)
            os.makedirs(self.slice_directory + "/densite_constante")
            os.makedirs(self.slice_directory + "/densite_lu")
        

    def add_contourage(self, ROI_id, name, color, array):
        """ Ajouter un contourage s'il existe pour la slice donnée """
        # Cas du premier ajout de contourage
        if self.contourages is None:
            self.contourages = {}

        contourage = { 'name': name, 'color': color, 'array': array, 'appartenance_contourage': None }
        self.contourages[ROI_id] = contourage


    def remove_contourage(self, ROI_id):
        """ Supprimer un contourage s'il existe """
        del self.contourages[ROI_id]

        # Cas du dernier contourage retire
        if len(self.contourages) == 0:
            self.contourages = None


    def modifier_couleur_contourage(self, ROI_id, color):
        self.contourages[ROI_id]['color'] = color


    def compute_appartenance_contourage(self, ROI_id):
        """ Calcule la matrice booléenne qui dit si un point appartient au contourage ou non """
        # Si la matrice a déjà été calculée (cas ou on scroll puis on revient sur une slice)
        if self.contourages[ROI_id]['appartenance_contourage'] is not None:
            return
        
        # Calcul de la matrice booléenne
        appartenance_contourage = get_appartenance_contourage(
            self.dicomparser.n_points,
            self.dicomparser.maillage,
            self.contourages[ROI_id]['array'])
        
        self.contourages[ROI_id]['appartenance_contourage'] = appartenance_contourage         
        

    def preparatifs_precalculs(self, options):
        """
        Calcule les matrices de densité et densité HOUNSFIELD avant de lancer M1
        Si densite_constante on considère un fantome d'eau
        """
        densite_lu = options['densite_lu']

        if densite_lu == 1:
            self.densite = self.dicomparser.get_DICOM_densite(self.slice_id)
            self.HU_array = self.dicomparser.get_DICOM_hounsfield(self.slice_id)
        else:
            self.densite = get_densite_fantome_eau(self.dicomparser.n_points)
            self.HU_array = None

        self.appartenance_contourage_cible = get_appartenance_contourage(self.dicomparser.n_points, \
                                                                   self.dicomparser.maillage, \
                                                                   self.contourages[self.dicomparser.contourage_cible_id]['array'])
        
        self.sources = get_sources(self.dicomparser.granularite_source, self.dicomparser.n_points,
                                   self.appartenance_contourage_cible, self.densite)
        self.domaine = get_domaine_minimal(self.sources, self.dicomparser.n_points,
                                           self.dicomparser.dimensions, self.dicomparser.maillage,
                                           self.dicomparser.zone_influence)
        self.domaine_n_points = get_domaine_n_points(self.domaine, self.dicomparser.n_points)


    def refresh_sources(self):
        """ Calcule les sources en fonction du contourage cible et autres options de previsu """
        # First time
        if (self.densite is None or self.HU_array is None):
            self.densite = self.dicomparser.get_DICOM_densite(self.slice_id)
            self.HU_array = self.dicomparser.get_DICOM_hounsfield(self.slice_id)

        self.appartenance_contourage_cible = get_appartenance_contourage(
            self.dicomparser.n_points, \
            self.dicomparser.maillage, \
            self.contourages[self.dicomparser.get_contourage_cible_id()]['array'])

        self.sources = get_sources(self.dicomparser.granularite_source, self.dicomparser.n_points,
                                   self.appartenance_contourage_cible, self.densite)
        

    def refresh_domaine(self):
        """ Calcule le domaine minimal en fonction du placement des sources """
        self.domaine = get_domaine_minimal(self.sources, self.dicomparser.n_points,
                                           self.dicomparser.dimensions, self.dicomparser.maillage,
                                           self.dicomparser.zone_influence)
        
        
    def set_dose_mode_ON(self):
        """ Active le dose mode """
        self.dose_mode = 1


    def set_dose_mode_OFF(self):
        """ Désactive le dose mode """
        self.dose_mode = 0
    

    def dose_already_calculated(self):
        """ Permet de savoir si des resultats de calculs passés sont en mémoire """
        n_sources_calculated = 0

        if self.dicomparser.get_densite_lu() == 1:
            path = self.slice_directory + "/densite_lu"
        else:
            path = self.slice_directory + "/densite_constante"
        
        for (dir_name, sub_dir_list, file_list) in os.walk(path):
            for filename in file_list:
                if ".dat" in filename.lower():  
                    n_sources_calculated += 1

        return (n_sources_calculated == len(self.sources))
            

    def get_closest_source(self, point, seuil):
        """ Retourne l'identifiant de la source de previsualisation la plus proche du point donné """
        closest_source_id = 1
        closest_source = self.sources[0]
        d_closest_source = distance(closest_source, point)

        for (id, source) in enumerate(self.sources, start=1):
            if distance(source, point) < d_closest_source:
                closest_source_id = id
                closest_source = source
                d_closest_source = distance(closest_source, point)

        # Au cas ou on clique trop loin d'une source
        if d_closest_source <= seuil:
            return closest_source_id
        else:
            return None


    def add_source_displayed(self, point, source_id):
        """ Ajoute un point correspond à la source exacte placée par le médecin """
        # None = source trop loin
        if (source_id is None) or (source_id in self.dic_sources_displayed):
            return

        (lf, mf, nf) = self.dicomparser.n_points

        # Cas de la premiere source ajoutee (matrice nulle)
        if self.dose_matrix is None:
            self.dose_matrix = np.zeros([lf, mf])
        
        self.dic_sources_displayed[source_id] = point

        # Calcul de la nouvelle matrice de doses
        domaine_dose_matrix = matrix_to_domaine(self.dose_matrix, self.domaine)

        if self.dicomparser.get_densite_lu() == 1:
            path = self.slice_directory + "/densite_lu/"
        else:
            path = self.slice_directory + "/densite_constante/"

        domaine_merged_dose_matrix = dose_matrix_add_source(path,
                                                            domaine_dose_matrix,
                                                            source_id)
        
        # On met la matrice de doses aux bonnes dimensions
        self.dose_matrix = np.zeros([lf, mf])
        self.dose_matrix = domaine_to_matrix(self.dose_matrix, domaine_merged_dose_matrix, self.domaine)


    def remove_source_displayed(self, source_id):
        """ Retire une source exacte """
        # None = source trop loin
        if (source_id is None) or not(source_id in self.dic_sources_displayed):
            return

        (lf, mf, nf) = self.dicomparser.n_points
        
        del self.dic_sources_displayed[source_id]

        # Calcul de la nouvelle matrice de doses
        domaine_dose_matrix = matrix_to_domaine(self.dose_matrix, self.domaine)

        if self.dicomparser.get_densite_lu() == 1:
            path = self.slice_directory + "/densite_lu/"
        else:
            path = self.slice_directory + "/densite_constante/"

        domaine_merged_dose_matrix = dose_matrix_remove_source(path,
                                                               domaine_dose_matrix,
                                                               source_id)

        # Cas de la dernier source enlevee (matrice nulle)
        maxhom = np.amax(domaine_merged_dose_matrix)
        if (maxhom < 1): # 1 est choisi arbitrairement pour eviter les residus
            self.dose_matrix = None
            self.sources_points = None
            return

        # On met la matrice de doses aux bonnes dimensions
        self.dose_matrix = np.zeros([lf, mf])
        self.dose_matrix = domaine_to_matrix(self.dose_matrix, domaine_merged_dose_matrix, self.domaine)


    def add_all_sources(self):
        (lf, mf, nf) = self.dicomparser.n_points

        self.dic_sources_displayed = {}
        self.dose_matrix = None

        # Cas de la premiere source ajoutee (matrice nulle)
        if self.dose_matrix is None:
            self.dose_matrix = np.zeros([lf, mf])

        # Conversion aux bonnes dimensions (retrecissement)
        domaine_dose_matrix = matrix_to_domaine(self.dose_matrix, self.domaine)

        if self.dicomparser.get_densite_lu() == 1:
            path = self.slice_directory + "/densite_lu/"
        else:
            path = self.slice_directory + "/densite_constante/"

        # Ajout de toutes les sources
        for (id, source) in enumerate(self.sources, start=1):
            self.dic_sources_displayed[id] = source

            domaine_dose_matrix = dose_matrix_add_source(path,
                                                         domaine_dose_matrix,
                                                         id)
        
        # On met la matrice de doses aux bonnes dimensions (agrandissement)
        self.dose_matrix = np.zeros([lf, mf])
        self.dose_matrix = domaine_to_matrix(self.dose_matrix, domaine_dose_matrix, self.domaine)
            
        
    def remove_all_sources(self):
        self.dic_sources_displayed = {}
        self.dose_matrix = None

            
    def update_dose_matrix(self):
        """ Plus utilise car trop lent (calculait toute la dose à chaque ajout...) """
        if is_empty(self.dic_sources_displayed):
            self.dose_matrix = None
            return

        (lf, mf, nf) = self.dicomparser.n_points
        vector_sources = self.dic_sources_displayed.keys()

        # Fusion des sources dans le vecteur
        domaine_dose_matrix = get_dose_matrix_merged(self.slice_directory,
                                                     vector_sources,
                                                     self.domaine_n_points)

        # On met la matrice de doses aux bonnes dimensions
        self.dose_matrix = np.zeros([lf, mf])
        self.dose_matrix = domaine_to_matrix(self.dose_matrix, domaine_dose_matrix, self.domaine)
        

    def update_DICOM_figure(self, figure, ax, display_settings, vmin=None, vmax=None):
        """ Met à jour la figure avec les modifications apportées dans la GUI """
        # On regle l'affichage (car ou on cose puis decoche...)
        if display_settings["sources"] == 0:
            sources_displayed = None
        else:
            sources_displayed = self.sources

        if display_settings["domaine"] == 0:
            domaine_displayed = None
        else:
            domaine_displayed = self.domaine

        if self.dose_mode == 0:
            dose_matrix_displayed = None
            sources_points_displayed = None
        else:
            dose_matrix_displayed = self.dose_matrix
            sources_points_displayed = self.dic_sources_displayed.values()
            

        # Affichage
        self.dicomparser.update_DICOM_figure(figure,
                                             ax,
                                             "Affichage de la dose",
                                             self.slice_id,
                                             vmin = vmin,
                                             vmax = vmax,                                          
                                             dose_matrix = dose_matrix_displayed,
                                             contourages_array = self.contourages,
                                             sources = sources_displayed,
                                             sources_points = sources_points_displayed,
                                             domaine = domaine_displayed)

def distance(A, B):
    return np.linalg.norm(A - B)


def is_empty(array):
    return len(array) == 0
