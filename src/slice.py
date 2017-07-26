# -*- coding: utf-8 -*-
import dicom
import numpy as np
import matplotlib.pyplot as plt

from contourage import *
from zone_influence import *
from generate_multisource import *
from merge_multisource import *

class Slice:
    def __init__(self, parent, dicom_slice, slice_id, dicomparser, filename_head):
        self.parent = parent
        self.dicom_slice = dicom_slice
        self.slice_id = slice_id
        self.dicomparser = dicomparser
        self.filename_head = filename_head
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
        self.contourage = None
        self.appartenance_contourage = None

        # Sources, domaine, matrice dose
        self.sources = None
        self.dic_sources_displayed = {}
        self.domaine = None
        self.dose_matrix = None


    def set_contourages(self, contourages):
        if len(contourages) == 0:
            self.contourages = None
            return
        
        self.contourages = contourages

        # On lit les contourages
        for (ROI_id, contourage) in contourages.iteritems():
            contourage['array'] = self.dicomparser.get_DICOM_contourage(ROI_id, self.slice_id)
        #self.appartenance_contourage = get_appartenance_contourage(self.dicomparser.n_points, \
        #                                                           self.dicomparser.maillage, \
        #                                                           self.contourage)

    def preparatifs_precalculs(self):
        self.densite = self.dicomparser.get_DICOM_densite(self.dicom_slice)
        self.HU_array = self.dicomparser.get_DICOM_hounsfield(self.dicom_slice)
        
        self.sources = get_sources(self.dicomparser.granularite_source, self.dicomparser.n_points,
                                   self.appartenance_contourage, self.densite)
        self.domaine = get_domaine_minimal(self.sources, self.dicomparser.n_points,
                                           self.dicomparser.dimensions, self.dicomparser.maillage,
                                           self.dicomparser.zone_influence)
        self.domaine_n_points = get_domaine_n_points(self.domaine, self.dicomparser.n_points)


    def get_dose_matrix(self):
        return self.dose_matrix
    

    def get_closest_source(self, point, seuil):        
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
        domaine_merged_dose_matrix = dose_matrix_add_source(self.filename_head,
                                                            domaine_dose_matrix,
                                                            source_id)
        
        # On met la matrice de doses aux bonnes dimensions
        self.dose_matrix = np.zeros([lf, mf])
        self.dose_matrix = domaine_to_matrix(self.dose_matrix, domaine_merged_dose_matrix, self.domaine)


    def remove_source_displayed(self, source_id):
        # None = source trop loin
        if (source_id is None) or not(source_id in self.dic_sources_displayed):
            return

        (lf, mf, nf) = self.dicomparser.n_points
        
        del self.dic_sources_displayed[source_id]

        # Calcul de la nouvelle matrice de doses
        domaine_dose_matrix = matrix_to_domaine(self.dose_matrix, self.domaine)
        domaine_merged_dose_matrix = dose_matrix_remove_source(self.filename_head,
                                                               domaine_dose_matrix,
                                                               source_id)

        # Cas de la dernier source enlevee (matrice nulle)
        maxhom = np.amax(domaine_merged_dose_matrix)
        if (maxhom < 1): # 1 est choisi arbitrairement pour eviter les residus
            self.dose_matrix = None
            return

        # On met la matrice de doses aux bonnes dimensions
        self.dose_matrix = np.zeros([lf, mf])
        self.dose_matrix = domaine_to_matrix(self.dose_matrix, domaine_merged_dose_matrix, self.domaine)

            
    def update_dose_matrix(self):
        """ Plus utilise car trop lent """
        if is_empty(self.dic_sources_displayed):
            self.dose_matrix = None
            return

        (lf, mf, nf) = self.dicomparser.n_points
        vector_sources = self.dic_sources_displayed.keys()

        # Fusion des sources dans le vecteur
        domaine_dose_matrix = get_dose_matrix_merged(self.filename_head,
                                                     vector_sources,
                                                     self.domaine_n_points)

        # On met la matrice de doses aux bonnes dimensions
        self.dose_matrix = np.zeros([lf, mf])
        self.dose_matrix = domaine_to_matrix(self.dose_matrix, domaine_dose_matrix, self.domaine)
        

    def update_DICOM_figure(self, figure, ax):
        # Get real sources points
        if is_empty(self.dic_sources_displayed):
            sources_points = None
        else:
            sources_points = self.dic_sources_displayed.values()
        
        self.dicomparser.update_DICOM_figure(figure,
                                             ax,
                                             "Affichage de la dose",
                                             self.slice_id,
                                             dose_matrix = self.dose_matrix,
                                             contourages_array = self.contourages,
                                             sources = self.sources,
                                             sources_points = sources_points, 
                                             domaine = self.domaine)

def distance(A, B):
    return np.linalg.norm(A - B)


def is_empty(array):
    return len(array) == 0
