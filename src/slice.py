# -*- coding: utf-8 -*-
import dicom
import numpy as np
import matplotlib.pyplot as plt

from contourage import *
from zone_influence import *
from generate_multisource import *
from merge_multisource import *

class Slice:
    def __init__(self, parent, slice_id):
        self.parent = parent
        self.slice_id = slice_id
        self.dicomparser = self.parent.dicomparser

        # Densite
        self.densite = self.dicomparser.get_DICOM_densite(self.slice_id)
        self.HU_array = self.dicomparser.get_DICOM_hounsfield(self.slice_id)

        # Contourage
        self.ROI_id = None
        self.contourage = None
        self.appartenance_contourage = None

        # Sources, domaine, matrice dose
        self.sources = None
        self.dic_sources_displayed = {}
        self.domaine = None
        self.dose_matrix = None


    def set_contourage(self, ROI_id):
        self.ROI_id = ROI_id
        self.contourage = self.dicomparser.get_DICOM_contourage(self.ROI_id, self.slice_id)
        self.appartenance_contourage = get_appartenance_contourage(self.dicomparser.n_points,
                                                                   self.dicomparser.maillage,
                                                                   self.contourage)
        self.sources = get_sources(self.dicomparser.granularite_source, self.dicomparser.n_points,
                                   self.appartenance_contourage, self.densite)
        self.domaine = get_domaine_minimal(self.sources, self.dicomparser.n_points,
                                           self.dicomparser.dimensions, self.dicomparser.maillage,
                                           self.dicomparser.zone_influence)
        self.domaine_n_points = get_domaine_n_points(self.domaine, self.dicomparser.n_points)


    def get_closest_source(self, point, seuil):
        closest_source_id = 1
        closest_source = self.sources[0]
        d_closest_source = distance(closest_source, point)

        for (id, source) in enumerate(self.sources, start=1):
            #print str((id, source)) + " ||| " + str(distance(source, point)) + "\n"
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
        if (source_id is not None):
            self.dic_sources_displayed[source_id] = point


    def remove_source_displayed(self, source_id):
        # None = source trop loin
        if (source_id is not None) and (source_id in self.dic_sources_displayed):
            del self.dic_sources_displayed[source_id]
            

    def update_dose_matrix(self):
        if is_empty(self.dic_sources_displayed):
            self.dose_matrix = None
            return

        (lf, mf, nf) = self.dicomparser.n_points
        vector_sources = self.dic_sources_displayed.keys()

        # Fusion des sources dans le vecteur
        domaine_dose_matrix = get_dose_matrix_merged(self.parent.filename_head,
                                                     vector_sources,
                                                     self.domaine_n_points)

        # On met la matrice de doses aux bonnes dimensions
        self.dose_matrix = np.zeros([lf, mf])
        self.dose_matrix = domaine_to_matrix(self.dose_matrix, domaine_dose_matrix, self.domaine)
        

    def update_DICOM_figure(self):
        # Get real sources points
        if is_empty(self.dic_sources_displayed):
            sources_points = None
        else:
            sources_points = self.dic_sources_displayed.values()
        
        self.dicomparser.update_DICOM_figure(self.parent.figure,
                                             self.parent.ax,
                                             "Test",
                                             self.slice_id,
                                             dose_matrix = self.dose_matrix,
                                             contourage = self.contourage,
                                             sources = self.sources,
                                             sources_points = sources_points, 
                                             domaine = self.domaine)

    def get_figure(self):
        return self.figure


    def get_ax(self):
        return self.ax
    


def distance(A, B):
    return np.linalg.norm(A - B)


def is_empty(array):
    return len(array) == 0
