#!/usr/bin/env python
# -*- coding: utf-8 -*-
# dicom_parser.py
""" Parsing du fichier DICOM """
# Author : Thibault PARPAITE, Cyrille BEAUCHESNE
# Copyright (c) 2017, CELIA Bordeaux
# This file is part of cythi, released under a BSD license.

import sys
import os
import pylab
import dicom
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mpc

from generate_multisource import *
from dose_parser import *
from zone_influence import *
from slice import *

# Useful help https://pyscience.wordpress.com/2014/09/08/dicom-in-python-importing-medical-image-data-into-numpy-with-pydicom-and-vtk/


class DicomParser:
    """ DicomParser est une classe permettant de manipuler (parser) un fichier DICOM
    Ses champs initialisés lors de l'instanciation de l'objet sont :
    - DICOM_files : un tableau de fichiers DICOM
    - slices : l'ensemble des coupes
    - n_points : un triplet (lf, mf, nf) qui represente le nombre de points par axe
    - dimensions : un triplet (Lx, Ly, Lz) qui définit les dimensions en mm
    - maillage : un triplet de trois tableaux (xm, ym, zm) correspondant au maillage 
    - RT_structure : un fichier DICOM (RS_xxxxx) representant les infos des slices
    - set_ROI : un ensemble de contourages (prostate, vessie...)
    [Complexité] O(n * log(n))
    """

    def __init__(self, DICOM_path):        
        # Lecture des fichiers DICOM
        self.DICOM_files = self.get_DICOM_files(DICOM_path)

        # Lecture des metadatas
        self.slices_info = self.get_slices_info()
        self.n_points = self.get_DICOM_npoints()
        self.n_points_raffines = None
        self.dimensions = self.get_DICOM_dimensions()
        self.maillage = self.get_DICOM_maillage()
        self.is_prone = 'p' in self.slices_info.PatientPosition.lower()
        self.is_feetfirst = 'ff' in self.slices_info.PatientPosition.lower()

        # Slices
        self.slices = self.get_slices()
        self.n_slices = len(self.slices)
        self.UID_to_sliceid_LUT = self.get_UID_to_sliceid_LUT()

        # Fichier RT (RT_structure, RS_xxxx)
        self.RT_structure = self.get_RT_structure()
        
        if (self.RT_structure):
            # Lecture de l'ensemble des contourages (prostate, vessie, ...)
            self.set_ROI = self.get_DICOM_set_ROI()
        else:
            print "RT_structure file wasn't found"
            self.RT_structure = None
            self.set_ROI = None

        # Matrice de convertion pixel -> coordinate
        self.patient_to_pixel_LUT = self.get_patient_to_pixel_LUT()

        # Placement sources
        self.granularite_source = None
        self.zone_influence = None
        self.contourage_cible_id = None

        # Options isodoses
        self.isodose_values = None
        

########################### Metadata ###########################

    def set_granularite_source(self, granularite_source):
        self.granularite_source = granularite_source


    def set_zone_influence(self, zone_influence):
        self.zone_influence = zone_influence


    def set_contourage_cible_id(self, contourage_cible_id):
        self.contourage_cible_id = contourage_cible_id


    def get_contourage_cible_id(self):
        return self.contourage_cible_id


    def set_raffinement(self, raffinement):
        """ Utilisé lorsqu'on change le raffinement """
        (lf, mf, nf) = self.n_points
        self.n_points_raffines = (raffinement * lf, raffinement * mf, nf)


    def set_isodose_values(self, isodose_values):
        """ Isodoses à prendre en compte pour l'affichage """
        self.isodose_values = isodose_values
        

    def get_DICOM_files(self, DICOM_path):
        """ Permet de recuperer l'ensemble des fichiers DICOM (slices) dans un tableau
        [Return] Un tableau contenant les fichiers DICOM du repertoire passé en param
        [Params] DICOM_path : le chemin vers le repertoire à parser
        [Complexité] O(n)   
        """
        DICOM_files = []
        for (dir_name, sub_dir_list, file_list) in os.walk(DICOM_path):
            for filename in sorted(file_list):
                if ".dcm" in filename.lower():  
                    DICOM_file = dicom.read_file(os.path.join(dir_name, filename))
                    DICOM_files.append(DICOM_file)
            
        return DICOM_files


    def get_RT_structure(self):
        for file in self.DICOM_files:
            if self.get_SOP_classUID(file) == 'rtss':
                return file
        return None


    def get_slices_info(self):
        # Arbitrairement la premiere
        for file in self.DICOM_files:
            if self.get_SOP_classUID(file) == 'ct':
                return file


    def get_slices(self):
        # On recupere les fichiers CT (slices)
        slices = []

        for file in self.DICOM_files:
            if self.get_SOP_classUID(file) == 'ct':
                slices.append(file)

        # Tri des indices
        unsorted_id = []
        
        for slice in slices:
            unsorted_id.append(slice.ImagePositionPatient[2])

        if ('hf' in slices[0].PatientPosition.lower()):
            # Head-first : tri decroissant
            sorted_id = sorted(unsorted_id, reverse=True)
        else:
            # Feet-first : tri croissant
            sorted_id = sorted(unsorted_id)


        # Tri des slices et instanciation
        sorted_slices = []
        
        for (slice_id, ind) in enumerate(sorted_id):
            for slice in slices:
                if (ind == slice.ImagePositionPatient[2]):
                    object = Slice(self, slice, slice_id, self)
                    sorted_slices.append(object)

        return sorted_slices


    def get_slice(self, slice_id):
        return self.slices[slice_id]


    def get_DICOM_npoints(self):
        """ Recupere les metadata (on prend la premiere slice arbitrairement)
        [Return] un triplet (lf, mf, nf) qui represente le nombre de points par axe
        """
        lf = int(self.slices_info.Rows)
        mf = int(self.slices_info.Columns)
        nf = 1
        # nf = len(DICOM_files - 1)
        n_points = (lf, mf, nf)
    
        return n_points
 

    def get_DICOM_dimensions(self):
        """ Recupere les metadata (on prend la premiere slice arbitrairement)
        [Return] un triplet (Lx, Ly, Lz) qui définit les dimensions en mm
        """
        n_points = self.get_DICOM_npoints()
        (lf, mf, nf) = n_points

        # Dimensions qu'on convertit de mm vers cm
        Lx = float(self.slices_info.PixelSpacing[0]) * lf * 10E-1
        Ly = float(self.slices_info.PixelSpacing[1]) * mf * 10E-1
        Lz = 1
        # Lz = float(DICOM_slice.SliceThickness)
        
        dimensions = (Lx, Ly, Lz)
    
        return dimensions


    def get_DICOM_maillage(self):
        """ Fournit un maillage uniforme en fonction des paramètres
        [Return] Un triplet de trois tableaux (xm, ym, zm) correspondant au maillage 
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


    def get_SOP_classUID(self, dicom_file):
        """Determine the SOP Class UID of the current file."""
        if (dicom_file.SOPClassUID == '1.2.840.10008.5.1.4.1.1.481.2'):
            return 'rtdose'
        elif (dicom_file.SOPClassUID == '1.2.840.10008.5.1.4.1.1.481.3'):
            return 'rtss'
        elif (dicom_file.SOPClassUID == '1.2.840.10008.5.1.4.1.1.481.5'):
            return 'rtplan'
        elif (dicom_file.SOPClassUID == '1.2.840.10008.5.1.4.1.1.2'):
            return 'ct'
        else:
            return None


########################### Convertion densité et HU ###########################


    def convert_pixel_to_densite(self, pixel):
        """ Convertit la valeur d'un pixel d'une image DICOM en une densité
        [Return] Un float representant densité associée
        [Params] pixel : un entier qui indique la valeur du pixel
        """
        # Table de correspondance trouvée dans densite.f90
        association_pixel_densite = [(-1000, 1e-3), (-985, 1e-3), (-660, 0.320), (-485, 0.480), \
                                     (-86, 0.945), (-35, 0.980), (12, 1.019), (29, 1.052), \
                                     (83, 1.094), (243, 1.157), (465, 1.335), (841, 1.561), \
                                     (1243, 1.824), (6800, 4.590), (15000, 8.639)]

        # Rercherche dichotomique approchee
        ig = 0
        id = len(association_pixel_densite)
        
        while (id - ig) > 1:
            im = (ig + id) / 2

            if (association_pixel_densite[im][0] <= pixel):
                ig = im
            else:
                id = im

                id = ig + 1

        # Interpolation
        return (association_pixel_densite[id][1] - association_pixel_densite[ig][1]) / \
               (association_pixel_densite[id][0] - association_pixel_densite[ig][0]) * \
               (pixel - association_pixel_densite[ig][0]) + association_pixel_densite[ig][1]
    

    def get_DICOM_densite(self, slice_id):
        """ Permet de recuperer les informations sur la densité d'une image DICOM
        [Return] Une matrice 2D indiquant la densité en chaque point
        [Params] dicom_slice_id : identifiant de la coupe
        """
        dicom_slice = self.slices[slice_id].dicom_slice
        pixel_array = dicom_slice.pixel_array
        (lf, mf, nf) = self.n_points
        
        densite = np.zeros([lf, mf])

        for x in range(lf):
            for y in range(mf):
                densite[x,y] = self.convert_pixel_to_densite(pixel_array[x, y])
            
        return densite


    def get_DICOM_hounsfield(self, slice_id):
        """ Permet de convertir la matrice de pixels au format Hounsfield Unit
        [Return] Une matrice 2D indiquant la valeur sur l'échelle de hounsfield en chaque point
        [Params] - dicom_slice_id : identifiant de la coupe
        [NB] Formule : hu = pixel_value * slope + intercept
        """
        # Recuperation des informations
        dicom_slice = self.slices[slice_id].dicom_slice
        pixel_array = dicom_slice.pixel_array
        slope = dicom_slice.RescaleSlope
        intercept = dicom_slice.RescaleIntercept
        (lf, mf, nf) = self.n_points
        HU_array = np.zeros([lf, mf])

        # Convertion de pixel vers hounsfield unit (HU)
        for x in range(lf):
            for y in range(mf):
                pixel_value = pixel_array[x, y]
                HU_array[x, y] = int(pixel_value * slope + intercept)

        return HU_array


########################### Contourage ###########################


    def get_DICOM_set_ROI(self):
        """ Permet de récupérer un ensemble de contourages
        [Return] Un dictionnaire indexé par le ROI_id du type et les différents contourages
        ex. : {'1': {'name' : 'CONTOUR EXTERNE', 'contours': 'array' ...}, ... }
        
        [Complexité] O(n)
        """
        set_ROI = {}

        for (contours_info, contourages) in zip(self.RT_structure.StructureSetROIs, self.RT_structure.ROIContours):
            if hasattr(contourages, 'Contours'):
                ROI_id = contours_info.ROINumber
                name = contours_info.ROIName
                contourages_dict = { 'name': name, 'contours': contourages.Contours }
                set_ROI[ROI_id] = contourages_dict
    
        return set_ROI


    def get_DICOM_ROI(self, ROI_id):
        """ Permet de récupérer les informations relatives a un type de contourage sur un fichier DICOM
        [Return] Un dictionnaire indexé par le UID (identifiant unique d'une coupe) et contenant
        les informations relatives au contourage ROI_id pour chaque coupe (correspondant à UID)
        ex. : {'1.2.840.113619.2.278.3.176243969.786.1462166632.515.88': array([[x1, y1, z1], [x2....}
        
        [Params] ROI_id : l'identifiant du contourage (par exemple prostate, vessie)
        [Complexité] O(n)
        """
        if not(ROI_id in self.set_ROI):
            msg = "Erreur : ROI_id invalide (" + str(ROI_id) + ")\n"
            sys.stderr.write(msg)
            afficher_setROI_names(set_ROI)
            sys.exit(1)
    
        contourages = {}
    
        for polygone in self.set_ROI[ROI_id]["contours"]:
            UID = polygone.ContourImages[0].ReferencedSOPInstanceUID
            # NB : On considere que polygone.ContourGeometric = CLOSED_PLANAR
            contourage_coordinate = self.get_contour_points(polygone.ContourData)
            contourage_pixel = self.convert_coord_to_pixel_contourage(contourage_coordinate)
            contourages[UID] = contourage_pixel

        return contourages
    

    def get_DICOM_contourage(self, ROI_id, slice_id):
        """ Recupere le contourage ROI_id d'une coupe s'il existe
        [Return] Un tableau de points (x, y, z) correspondant à une sequence (contourage)
        [Params]
        - ROI_id : identifiant du type de contourage
        - slice_id : identifiant de la coupe
        [Complexité] O(n)
        """
        UID = self.slices[slice_id].dicom_slice.SOPInstanceUID
        DICOM_ROI = self.get_DICOM_ROI(ROI_id)
    
        if not(UID in DICOM_ROI):
            msg = "Erreur : la coupe " + str(UID) + " ne possède pas d'informations pour le "
            msg += "contourage choisi\n"
            sys.stderr.write(msg)
            #sys.exit(1)

        return DICOM_ROI[UID]


    def get_UID_to_sliceid_LUT(self):
        """ Dictionnaire permettant d'associer à un UID un ID de slice """
        UID_to_sliceid_LUT = {}

        for slice in self.slices:
            UID = slice.dicom_slice.SOPInstanceUID
            UID_to_sliceid_LUT[UID] = slice.get_slice_id()

        return UID_to_sliceid_LUT
        

    def get_contour_points(self, array):
        """ Convertit un tableau de la forme [x1, y1, z1...] en tableau [(x1, y1, z1), (x2, y2, z2)...]
        [Return] Un tableau de points correspondant à une sequence (contourage)
        [Params] array : un tableau de points dont les coordonnées sont à plat
        [Complexité] O(n)
        [NB]
        - Les coordonnées des points sont données en fonction de la position relative (mm)
        - Utilisé dans get_DICOM_contourage
        - Un point 3D est représenté par un triplet (x, y, z)
        - Meme s'il y a trois dimensions le contourage est supposé 2D car z est constant (coupe)
        """
        array_3D = zip(*[iter(array)]*3) # Tricky
        array_3D.append(array_3D[0]) # Pour fermer le polygone (on relie le dernier et le premier point)
        array_3D = np.array(array_3D)
        return array_3D


    def get_DICOM_appartenance_contourage_ROI(self, ROI_id):
        """ Retourne un dictionnaire de matrices d'appartenance à un contourage pour un ROI donné
        [Return] Un dictionnaire dont l'indexation correspond aux UID des slices contourées pour cet ROI
        ex. : {'1.2.840.113619.2.278.3.176243969.786.1462166632.515.88': matrice2D_appartenance_contourage, ... }
        [Params] ROI_id : identifiant du type de contourage
        [Complexité] O(n)
        """
        contourages = self.get_DICOM_ROI(ROI_id)

        dic_appartenances_contourages = {}

        for (UID, contourage) in contourages.iteritems():
            appartenance_contourage = get_appartenance_contourage(self.n_points, self.maillage, contourage)
            dic_appartenances_contourages[UID] = appartenance_contourage

        return dic_appartenances_contourages


###################### Pixel to patient coordinate (Part 3 - C.7.6.2.1) ######################
# Useful help : http://nipy.org/nibabel/dicom/dicom_orientation.html

    def get_patient_to_pixel_LUT(self):
        """ Permet d'obtenir la matrice de transformation faisant le lien entre les pixels et
        les coordonnées du patient (translation + rotation + pixel_space)
        
        [Return] La matrice de transormation permettant pixel -> coordinate
        NB : la première slice est prise arbitrairement (toutes les slices ont mm metadata)"""

        dx = self.slices_info.PixelSpacing[0]
        dy = self.slices_info.PixelSpacing[1]
        orientation = self.slices_info.ImageOrientationPatient
        position = self.slices_info.ImagePositionPatient

        m = np.matrix(
            [[orientation[0]*dx, orientation[3]*dy, 0, position[0]],
             [orientation[1]*dx, orientation[4]*dy, 0, position[1]],
             [orientation[2]*dx, orientation[5]*dy, 0, position[2]],
             [0, 0, 0, 1]])

        # On applique la transformation pour chaque coordonnée du maillage afin d'avoir une LUT
        (lf, mf, nf) = self.n_points

        x = []
        y = []
        
        for i in range(0, lf):
            imat = m * np.matrix([[i], [0], [0], [1]])
            x.append(float(imat[0]))
            
        for j in range(0, mf):
            jmat = m * np.matrix([[0], [j], [0], [1]])
            y.append(float(jmat[1]))

        patient_to_pixel_LUT = (np.array(x), np.array(y))
        
        return patient_to_pixel_LUT


    def convert_coord_to_pixel(self, point):
        """
        """
        # Recuperation des informations
        prone = self.is_prone
        feetfirst = self.is_feetfirst
        
        # On cherche les coordonnees du maillage (pixel) associees aux coord reelles
        for (x, x_val) in enumerate(self.patient_to_pixel_LUT[0]):
            if (x_val > point[0] and not prone and not feetfirst):
                break
            elif (x_val < point[0]):
                if feetfirst or prone:
                    break

        for (y, y_val) in enumerate(self.patient_to_pixel_LUT[1]):
            if (y_val > point[1] and not prone):
                break
            elif (y_val < point[1] and prone):
                break
            
        coord_pixel = (x, y)
        
        return coord_pixel
        

    def convert_coord_to_pixel_contourage(self, contourage_coordinate):
        """ Convertit un contourage avec coordonnees exactes vers contourage pixel """
        contourage_pixel = []
        
        for point in contourage_coordinate:
            coord_pixel = self.convert_coord_to_pixel(point)
            contourage_pixel.append(coord_pixel)

        return np.array(contourage_pixel)

    

###################### Generation des fichiers pour le calcul de dose ######################


    def generate_DICOM_hounsfield(self, filename_hounsfield, HU_array):
        """ Permet la génération du fichier coeff_name.don contenant les données HU lues par KIDS
        [Params]
        - filename_header : le nom du cas traité
        - HU_array : matrice 2D retournée par get_DICOM_hounsfield
        """
        np.savetxt(filename_hounsfield, HU_array,  fmt='%i')
        print filename_hounsfield + " successfully generated"

    
    def generate_DICOM_don_old(self, slice_id, contourage, zone_influence, affichage=True):
        """ Lance la generation d'un fichier .don pour un fichier DICOM avec contourage donné
        [Params]
        - filename_header : le nom du cas traité
        - slice_id : identifiant de la coupe
        - contourage : une sequence de points representant un polygone ferme
        """
        # Parametres arbitraires (a changer)
        granularite_source = 5
        rayon = (0.6, 0.6, 0.6)
        direction_M1 = (0., 0., 0.)
        spectre_mono = (1e20, 0.03)

        # Densite
        HU_array = self.get_DICOM_hounsfield(slice_id)
        densite = self.get_DICOM_densite(slice_id)

        # Sources
        appartenance_contourage = get_appartenance_contourage(self.n_points, self.maillage, contourage)
        sources = get_sources(granularite_source, self.n_points, appartenance_contourage, densite)

        # Domaine minimal
        domaine = get_domaine_minimal(sources, self.n_points, self.dimensions, self.maillage, zone_influence)

        # Affichage des sources et du domaine
        if (affichage):
            self.afficher_DICOM("Placement des sources", slice_id, contourage=contourage, sources=sources, domaine=domaine)
            
        # Reduction des calculs sur le domaine        
        domaine_n_points = get_domaine_n_points(domaine, self.n_points)
        domaine_dimensions = get_domaine_dimensions(domaine, self.dimensions, self.maillage)
        domaine_sources = get_domaine_sources(domaine, sources)
        domaine_HU_array = get_domaine_HU_array(domaine, HU_array)

        # Generation (coefficients HU et fichier de config .don)
        self.generate_DICOM_hounsfield(domaine_HU_array)
        filename = self.working_directory + "/slice_" + str(slice_id).zfill(3) + "/KIDS.don"
        lancer_generation(filename, domaine_sources, domaine_n_points, domaine_dimensions, rayon, direction_M1, spectre_mono, densite_lu=True)


    def generate_DICOM_previsualisation(self, slice_id, working_directory, options):
        """ Lance la generation d'un fichier .don pour un fichier DICOM avec contourage donné
        [Params]
        - filename_header : le nom du cas traité
        - slice_id : identifiant de la coupe
        - contourage : une sequence de points representant un polygone ferme
        """
        slice = self.slices[slice_id]

        # Densite
        HU_array = slice.get_HU_array()

        # Sources
        sources = slice.get_sources()

        # Domaine minimal
        domaine = slice.get_domaine()
            
        # Reduction des calculs sur le domaine        
        domaine_n_points = get_domaine_n_points(domaine, self.n_points_raffines)
        domaine_dimensions = get_domaine_dimensions(domaine, self.dimensions, self.maillage)
        domaine_sources = get_domaine_sources(domaine, sources)
        domaine_HU_array = get_domaine_HU_array(domaine, HU_array)

        # Generation du fichier correspondant a la densite HU
        filename_hounsfield = working_directory + "/slice_" + str(slice_id).zfill(3) + "/densite_hu.don"
        self.generate_DICOM_hounsfield(filename_hounsfield, domaine_HU_array)

        # Generation fichier configuration DON
        filename = working_directory + "/slice_" + str(slice_id).zfill(3) + "/config_KIDS.don"
        lancer_generation(filename, domaine_sources, domaine_n_points, domaine_dimensions, options, densite_lu=True)


    def generate_DICOM_calculs_finaux(self, slice_id, working_directory, options):
        slice = self.slices[slice_id]

        # Densite
        HU_array = slice.get_HU_array()

        # Sources reelles activees (arrondies a la maillage la plus proche)
        sources = slice.get_dic_sources_displayed().values()
        for source in sources:
            source[0] = int(np.round(source[0]))
            source[1] = int(np.round(source[1]))

        # Domaine minimal (TODO : a optimiser avec les nouvelles sources)
        domaine = slice.get_domaine()
            
        # Reduction des calculs sur le domaine        
        domaine_n_points = get_domaine_n_points(domaine, self.n_points_raffines)
        domaine_dimensions = get_domaine_dimensions(domaine, self.dimensions, self.maillage)
        domaine_sources = get_domaine_sources(domaine, sources)
        domaine_HU_array = get_domaine_HU_array(domaine, HU_array)

        # Generation fichier configuration DON
        filename = working_directory + "/slice_" + str(slice_id).zfill(3) + "/config_KIDS_calculs_finaux.don"
        lancer_generation(filename, domaine_sources, domaine_n_points, domaine_dimensions, options, densite_lu=True, calculs_finaux=True)


    


########################### Affichage ###########################
        
    def add_contourage_plot(self, contourages_array, slice_id, ROI_id, color):
        """ Ajoute un contourage au tableau de contourages passé en paramètre (pour l'afficher ensuite)
        [Params]
        - contourages_array : un tableau de contourages
        - slice_id : identifiant de la coupe
        - ROI_id : identifiant du type de contourage
        - color : couleur du contourage
        """
        contourage = self.get_DICOM_contourage(ROI_id, slice_id)
        contourage_info = { 'name': self.set_ROI[ROI_id]['name'], 'array': contourage, 'color': color }
    
        contourages_array.append(contourage_info)
        

    def afficher_setROI_names(self):
        """ Affiche les couples (ROI_id, type_contourage) """
        for (ROI_id, contourages) in self.set_ROI.iteritems():
            print (ROI_id, contourages['name'])


    def get_set_ROI(self):
        return self.set_ROI


    def afficher_DICOM_files(self):
        """ Affiche les couples (slice_id, file) """
        n_slices = len(self.DICOM_files)
        for (i, file) in zip(range(n_slices), self.DICOM_files):
            print (i, file)



    def get_DICOM_figure(self):
        (lf, mf, nf) = self.n_points
        
        fig, ax = plt.subplots(facecolor="black")
        ax.set_xlim([0, lf])
        ax.set_ylim([mf, 0])
        fig.tight_layout() 
        
        return (fig, ax)


    def update_DICOM_figure(self, fig, ax, title, slice_id, vmin=None, vmax=None, dose_matrix=None, contourage=None, contourages_array=None, sources=None, sources_points=None, domaine=None, details=False):
        """ Trace une figure representant un fichier DICOM avec eventuellement des doses et contourages
        [Params]
        - title : titre de la figure
        - slice_id : identifiant de la coupe
        - dose_matrix : une matrice 2D correspondant à la répartition de la dose
        - contourage : une sequence de points representant un polygone ferme
        - contourages_array : un tableau de contourage
        - coord_sources : les coordonnees reelles des sources
        """
        # Preservation du zoom (1)
        x_lim = ax.get_xlim()
        y_lim = ax.get_ylim()
        
        # On nettoie le graphe
        ax.clear()

        # Preservation du zoom (2)
        ax.set_xlim(x_lim)
        ax.set_ylim(y_lim)

        # Affichage des details
        if details:
            depth = self.slices[slice_id].SliceLocation
            title = title + " - Depth (mm) : " + str(depth)
            (lf, mf, nf) = self.n_points
            ax.set_title(title, fontsize=15, y=1.07)
            ax.set_xlabel("x (pixels)", fontsize=12)
            ax.set_ylabel("y (pixels)", fontsize=12)
            ax.xaxis.set_label_position('top')
            ax.xaxis.tick_top()
        else:
            plt.axis('off')
            
        pixel_array = self.slices[slice_id].pixel_array
        plot_DICOM_pixel_array(ax, pixel_array, vmin, vmax)

        if (dose_matrix is not None):
            plot_DICOM_dose(ax, dose_matrix, self.n_points, self.isodose_values)

        if (contourages_array is not None):
            plot_DICOM_contourages_array(ax, contourages_array)
        elif (contourage is not None):
            plot_DICOM_contourage(ax, contourage, 'orange')
        
        if (sources is not None):
            plot_DICOM_sources(ax, sources)

        if (sources_points is not None):
            plot_DICOM_sources_points(ax, sources_points)

        if (domaine is not None):
            plot_DICOM_domaine(ax, domaine)

        #DEBUG

        # Affichage source
        point_source = (51+179, 61+194)
        #ax.plot(point_source[0], point_source[1], 'bo', zorder=3)

        point_source_2 = (51+179, 66+194)
        #ax.plot(point_source_2[0], point_source_2[1], 'go', zorder=3)

        # Affichage points min/max
        point_min = (179, 194)
        #ax.plot(point_min[0], point_min[1], 'ro')

        point_max = (326, 336)
        #ax.plot(point_max[0], point_max[1], 'go')
        #ENDDEBUG


    def afficher_DICOM(self, title, slice_id, dose_matrix=None, contourage=None, contourages_array=None, sources=None, domaine=None):
        (fig, ax) = self.get_DICOM_figure()
        self.update_DICOM_figure(fig, ax, title, slice_id, dose_matrix=dose_matrix, contourage=contourage, contourages_array=contourages_array, sources=sources, domaine=domaine)
        fig.show()
    

###################### Plot informations  ######################


def plot_DICOM_pixel_array(ax, pixel_array, vmin=None, vmax=None):
    """ Ajoute l'image DICOM à la figure
    [Params]
    - ax : l'axe correspondant à la figure
    - pixel_array : un tableau de pixel obtenu grace à DICOM_slice.pixel_array
    """
    ax.imshow(pixel_array, origin='upper', cmap=plt.cm.bone, vmin=vmin, vmax=vmax)


def plot_DICOM_dose(ax, dose_matrix, n_points, isodose_values):
    """ Ajoute la visualisation de la dose sur la figure
    [Params]
    - ax : l'axe correspondant à la figure
    - dose_matrix : une matrice 2D correspondant à la répartition de la dose
    """
    (lf, mf, nf) = n_points
    dose_matrix = dose_matrix.T
    maxhom = np.amax(dose_matrix)

    # Calcul des limites d'isodoses
    # levelsXZ = (0.05, 0.25, 0.5, 0.85, 0.95)
    #min = options_isodoses['isodose_min']
    #max = options_isodoses['isodose_max']
    #step = (max - min) / 4
    #levelsXZ = (min, min + step, min + (2 * step), min + (3 * step), max)

    #isodose = dose_matrix/maxhom
    #print isodose[179+51, 194+61]
    #ax.imshow(dose_matrix, origin='upper', zorder=2, cmap='hot')
    
    CS = ax.contour(dose_matrix/maxhom, isodose_values, origin='upper', extent=[0, lf, mf, 0], linewidths=2, zorder=3)
    #ax.clabel(CS, inline=1, fontsize=15, inline_spacing=0, linestyles='dashed', zorder=3)


def plot_DICOM_contourage(ax, contourage, color):
    """ Ajoute la visualisation du contourage sur la figure
    [Params]
    - ax : l'axe correspondant à la figure
    - contourage : une sequence de points representant un polygone fermé
    - color : couleur du contourage
    """
    # Creation du polygone
    contourage_2D = contourage[:,(0,1)] # On garde seulement 2D pour utiliser mp.Path
    contourage_path = mp.Path(contourage_2D)

    # Opacite differente entre face et edge
    rgb_face = mpc.colorConverter.to_rgba(color, alpha=0.2)
    rgb_edge = mpc.colorConverter.to_rgba(color, alpha=1)

    patch = patches.PathPatch(contourage_path, facecolor=rgb_face, edgecolor=rgb_edge, linewidth=1)

    # Affichage
    ax.add_patch(patch)


def plot_DICOM_contourages_array(ax, contourages_array):
    """ Ajoute la visualisation de plusieurs contourages sur la figure
    [Params]
    - ax : l'axe correspondant à la figure
    - contourages_array : un tableau de contourages
    """
    for (ROI_id, contourage) in contourages_array.iteritems():
        plot_DICOM_contourage(ax, contourage['array'], contourage['color'])


def plot_DICOM_sources(ax, sources):
    """ Ajoute la visualisation des sources sur la figure
    [Params]
    - ax : l'axe correspondant à la figure
    - sources : un tableau de points indiquant le positionnement des sources (coord maillage)
    """
    ax.plot(sources[:,0], sources[:,1], color='red', marker=',', linestyle='None')


def plot_DICOM_sources_points(ax, sources_points):
    for point in sources_points:
        ax.plot(point[0], point[1], 'ro')


def plot_DICOM_domaine(ax, domaine):
    """ Ajoute la visualisation du domaine sur la figure
    [Params]
    - ax : l'axe correspondant à la figure
    - domaine : quadruplet (x_min, y_min, x_max, y_max) representant le domaine
    """
    # Recuperation des informations
    (x_min, y_min) = domaine[0]
    (x_max, y_max) = domaine[1]    

    # Creation du polygone
    polygone_domaine = np.array([[x_min, y_min],
                                 [x_min, y_max],
                                 [x_max, y_max],
                                 [x_max, y_min],
                                 [x_min, y_min]])

    domaine_path = mp.Path(polygone_domaine)
    patch_domaine = patches.PathPatch(domaine_path, facecolor='none', edgecolor='white', lw=2)

    # Affichage
    ax.add_patch(patch_domaine)


# Useless now
def get_point_upper(point, n_points):
    (lf, mf, nf) = n_points
    (x, y) = point
    point_upper = (x, mf - y)

    return point_upper


def set_origin_upper(sequence_point, n_points):
    sequence_upper = []

    for point in sequence_point:
        point_upper = get_point_upper(point, n_points)
        sequence_upper.append(point_upper)

    return np.array(sequence_upper)

    


    
