# -*- coding: utf-8 -*-
import sys
import os
import pylab
import dicom
import numpy as np
import matplotlib.pyplot as plt

from generate_multisource import *
from dose_parser import *
from zone_influence import *

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

    def __init__(self, DICOM_path, RT_structure_id=None):
        # Lecture de toutes les slices
        self.DICOM_files = self.get_DICOM_files(DICOM_path)
        n_slices = len(self.DICOM_files)
    
        self.slices = []
        for slice in self.DICOM_files:
            self.slices.append(dicom.read_file(slice))
            
        self.slices = np.array(self.slices)

        # Lecture des metadatas
        self.n_points = self.get_DICOM_npoints()
        self.dimensions = self.get_DICOM_dimensions()
        self.maillage = self.get_DICOM_maillage()

        # Lecture du fichier RT (RT_structure, RS_xxxx)
        if (RT_structure_id is not None):
            self.RT_structure = self.slices[RT_structure_id]
            # Lecture de l'ensemble des contourages (prostate, vessie, ...)
            self.set_ROI = self.get_DICOM_set_ROI()
        else:
            self.RT_structure = None
            self.set_ROI = None

        # Matrice de convertion pixel -> coordinate
        self.patient_to_pixel_LUT = self.get_patient_to_pixel_LUT()
        

########################### Metadata ###########################

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
                    DICOM_files.append(os.path.join(dir_name, filename))
                
        return sorted(DICOM_files)


    def get_DICOM_npoints(self):
        """ Recupere les metadata (on prend la premiere slice arbitrairement)
        [Return] un triplet (lf, mf, nf) qui represente le nombre de points par axe
        """
        lf = int(self.slices[0].Rows)
        mf = int(self.slices[0].Columns)
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
        Lx = float(self.slices[0].PixelSpacing[0]) * lf * 10E-1
        Ly = float(self.slices[0].PixelSpacing[1]) * mf * 10E-1
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
        [Params] slice_id : identifiant de la coupe
        """
        pixel_array = self.slices[slice_id].pixel_array
        (lf, mf, nf) = self.n_points
        
        densite = np.zeros([lf, mf])

        for x in range(lf):
            for y in range(mf):
                densite[x,y] = self.convert_pixel_to_densite(pixel_array[x, y])
            
        return densite


    def get_DICOM_hounsfield(self, slice_id):
        """ Permet de convertir la matrice de pixels au format Hounsfield Unit
        [Return] Une matrice 2D indiquant la valeur sur l'échelle de hounsfield en chaque point
        [Params] - slice_id : identifiant de la coupe
        [NB] Formule : hu = pixel_value * slope + intercept
        """
        # Recuperation des informations
        DICOM_slice = self.slices[slice_id]
        pixel_array = DICOM_slice.pixel_array
        slope = DICOM_slice.RescaleSlope
        intercept = DICOM_slice.RescaleIntercept
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
            contourage = self.get_contour_points(polygone.ContourData)
            # TODO : convertir de maniere plus fine coord -> pixel
            contourages[UID] = contourage

        return contourages
    

    def get_DICOM_contourage(self, ROI_id, slice_id):
        """ Recupere le contourage ROI_id d'une coupe s'il existe
        [Return] Un tableau de points (x, y, z) correspondant à une sequence (contourage)

        [Params]
        - ROI_id : identifiant du type de contourage
        - slice_id : identifiant de la coupe

        [Complexité] O(n)
        """
        UID = self.slices[slice_id].SOPInstanceUID
        DICOM_ROI = self.get_DICOM_ROI(ROI_id)
    
        if not(UID in DICOM_ROI):
            msg = "Erreur : la coupe " + str(UID) + " ne possède pas d'informations pour le "
            msg += "contourage choisi\n"
            sys.stderr.write(msg)
            sys.exit(1)

        return DICOM_ROI[UID]
        

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
        array_3D = 256 + array_3D
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
# Inutile dans les cas academiques traites

    def get_patient_to_pixel_LUT(self):
        """ Permet d'obtenir la matrice de transformation faisant le lien entre les pixels et
        les coordonnées du patient (translation + rotation + pixel_space)
        
        [Return] La matrice de transormation permettant pixel -> coordinate

        NB : la première slice est prise arbitrairement (toutes les slices ont mm metadata)"""

        dx = self.slices[0].PixelSpacing[0]
        dy = self.slices[0].PixelSpacing[1]
        orientation = self.slices[0].ImageOrientationPatient
        position = self.slices[0].ImagePositionPatient

        patient_to_pixel_LUT = np.matrix(
            [[orientation[0]*dx, orientation[3]*dy, 0, position[0]],
             [orientation[1]*dx, orientation[4]*dy, 0, position[1]],
             [orientation[2]*dx, orientation[5]*dy, 0, position[2]],
             [0, 0, 0, 1]])

        return patient_to_pixel_LUT


    def convert_coord_to_pixel(self, point):
        """
        """
        # Determine if the patient is prone or supine
        supine = -1 if 's' in self.slices[0].PatientPosition.lower() else 1
        headfirst = 1 if 'hf' in self.slices[0].PatientPosition.lower() else -1
        position = self.slices[0].ImagePositionPatient
        
        # Get the pixel spacing
        spacing = self.slices[0].PixelSpacing
        
        vector = np.array([[point[0]],
                           [point[1]],
                           [0],
                           [1]])

        # Coordonnees du pixel dans un plan en mm
        coord_pixel_mm = self.patient_to_pixel_LUT * vector

        # On recupere ses coordonnees dans le tableau pixel_array de la forme [x, y, z]
        x = 512 - int((coord_pixel_mm[0][0]) * supine * headfirst / spacing[0])
        y = 512 - int((coord_pixel_mm[1][0]) * supine / spacing[1])
        z = point[2]
        coord_pixel_array = (x, y, z)
        
        return coord_pixel_array
        

    def convert_coord_to_pixel_contourage(self, contourage_coordinate):
        """ Convertit un contourage avec coordonnees exactes vers contourage pixel """
        contourage_pixel = []
        
        for point in contourage_coordinate:
            point_pixel = self.convert_coord_to_pixel(point)
            contourage_pixel.append(point_pixel)

        return np.array(contourage_pixel)

    

###################### Generation des fichiers pour le calcul de dose ######################


    def generate_DICOM_hounsfield(self, filename_header, HU_array):
        """ Permet la génération du fichier coeff_name.don contenant les données HU lues par KIDS
        [Params]
        - filename_header : le nom du cas traité
        - HU_array : matrice 2D retournée par get_DICOM_hounsfield
        """
        filename_coeff = "densite_hu_" + filename_header + ".don"
        np.savetxt(filename_coeff, HU_array,  fmt='%i')
        print filename_coeff + " successfully generated"

    
    def generate_DICOM_don(self, filename_header, slice_id, contourage, zone_influence, affichage=True):
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
            coord_sources = get_coord_sources(sources, self.maillage)
            polygon_domaine = get_polygon_domaine_minimal(self.maillage, domaine)
            self.afficher_DICOM("Placement des sources", slice_id, contourage=contourage, coord_sources=coord_sources, polygon_domaine=polygon_domaine)

        # Reduction des calculs sur le domaine        
        domaine_n_points = get_domaine_n_points(domaine, self.n_points)
        domaine_dimensions = get_domaine_dimensions(domaine, self.dimensions, self.maillage)
        domaine_sources = get_domaine_sources(domaine, sources)
        domaine_HU_array = get_domaine_HU_array(domaine, HU_array)

        # Generation (coefficients HU et fichier de config .don)
        self.generate_DICOM_hounsfield(filename_header, domaine_HU_array)
        lancer_generation(filename_header, domaine_sources, domaine_n_points, domaine_dimensions, rayon, direction_M1, spectre_mono, densite_lu=True)


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


    def afficher_DICOM_files(self):
        """ Affiche les couples (slice_id, file) """
        n_slices = len(self.DICOM_files)
        for (i, file) in zip(range(n_slices), self.DICOM_files):
            print (i, file)


    def afficher_DICOM(self, title, slice_id, dose_matrix=None, contourage=None, contourages_array=None, coord_sources=None, polygon_domaine=None):
        """ Trace une figure representant un fichier DICOM avec eventuellement des doses et contourages
        [Params]
        - title : titre de la figure
        - slice_id : identifiant de la coupe
        - dose_matrix : une matrice 2D correspondant à la répartition de la dose
        - contourage : une sequence de points representant un polygone ferme
        - contourages_array : un tableau de contourage
        - coord_sources : les coordonnees reelles des sources
        """
        fig, ax = plt.subplots()

        depth = self.slices[slice_id].SliceLocation
        title = title + " - Depth (mm) : " + str(depth)

        pixel_array = self.slices[slice_id].pixel_array
        plot_DICOM_pixel_array(ax, pixel_array)

        if (dose_matrix is not None):
            plot_DICOM_dose(ax, dose_matrix)

        if (contourages_array is not None):
            plot_DICOM_contourages_array(ax, contourages_array)
        elif (contourage is not None):
            plot_DICOM_contourage(ax, contourage, 'orange')
        
        if (coord_sources is not None):
            plot_DICOM_sources(ax, coord_sources)

        if (polygon_domaine is not None):
            plot_DICOM_domaine(ax, polygon_domaine)

        # Configuration de la figure
        ax.set_title(title, fontsize=20, y=1.02)
        ax.set_xlabel("x (pixels)", fontsize=20)
        ax.set_ylabel("y (pixels)", fontsize=20)
        (lf, mf, nf) = self.n_points
        ax.set_xlim([0, lf])
        ax.set_ylim([mf, 0])

        fig.show()


###################### Plot informations  ######################


def plot_DICOM_pixel_array(ax, pixel_array):
    """ Ajoute l'image DICOM à la figure
    [Params]
    - ax : l'axe correspondant à la figure
    - pixel_array : un tableau de pixel obtenu grace à DICOM_slice.pixel_array
    """
    ax.imshow(pixel_array, origin='lower', cmap=plt.cm.bone)


def plot_DICOM_dose(ax, dose_matrix):
    """ Ajoute la visualisation de la dose sur la figure
    [Params]
    - ax : l'axe correspondant à la figure
    - dose_matrix : une matrice 2D correspondant à la répartition de la dose
    """
    levelsXZ = (0.05, 0.25, 0.5, 0.85, 0.95)
    maxhom = np.amax(dose_matrix)
    CS = ax.contour(dose_matrix/maxhom, levelsXZ, linewidths=2)
    ax.clabel(CS, inline=1, fontsize=15, inline_spacing=0, linestyles='dashed')


def plot_DICOM_contourage(ax, contourage, color):
    """ Ajoute la visualisation du contourage sur la figure
    [Params]
    - ax : l'axe correspondant à la figure
    - contourage : une sequence de points representant un polygone fermé
    - color : couleur du contourage
    """
    contourage_2D = contourage[:,(0,1)] # On garde seulement 2D pour utiliser mp.Path
    contourage_path = mp.Path(contourage_2D)
    patch = patches.PathPatch(contourage_path, facecolor=color, linewidth=0)
    ax.add_patch(patch)


def plot_DICOM_contourages_array(ax, contourages_array):
    """ Ajoute la visualisation de plusieurs contourages sur la figure
    [Params]
    - ax : l'axe correspondant à la figure
    - contourages_array : un tableau de contourages
    """
    for contourage in contourages_array:
        plot_DICOM_contourage(ax, contourage['array'], contourage['color'])


def plot_DICOM_sources(ax, coord_sources):
    """ Ajoute la visualisation des sources sur la figure
    [Params]
    - ax : l'axe correspondant à la figure
    - coord_sources : un tableau de points indiquant le positionnement des sources
    """
    ax.plot(coord_sources[:,0], coord_sources[:,1], color='b', marker=',', linestyle='None')


def plot_DICOM_domaine(ax, polygon_domaine):
    """ Ajoute la visualisation du domaine sur la figure
    [Params]
    - ax : l'axe correspondant à la figure
    - polygon_domaine : une sequence de cinq points (rectangle) representant le domaine minimal
                        (les coordonnees doivent etre reelles et pas les indices de maillage)
    """
    domaine_path = mp.Path(polygon_domaine)
    patch_domaine = patches.PathPatch(domaine_path, facecolor='none', edgecolor='white', lw=2)
    ax.add_patch(patch_domaine)
    
