# -*- coding: utf-8 -*-


from dicom_parser import DicomParser, get_appartenance_contourage
from matplotlib import pyplot as plt
from numpy import array


class DICOM_from_path:
    def __init__(self, path, RT_id):
        self.path = path
        self.DP = DicomParser(path)


class Doses_from_matrice:
    def __init__(self,matrice_doses, slice_id=None):
        self.matrice = array(matrice_doses)
        self.slice_id = slice_id
        self.dim = self.matrice.shape
    def afficher(self):
        plt.imshow(self.matrice, origin='lower')
        plt.show()


class Contourage_from_matrice:
    def __init__(self, matrice_booleenne, ROI_id):
        self.matrice = matrice_booleenne
        self.dim = matrice_booleenne.shape
        self.nom = 'ROI : ' + str(ROI_id)
        self.ROI_id = ROI_id
    def afficher(self):
        plt.imshow(self.matrice, origin='lower')
        plt.show()


class Contourage_from_DP:
    def __init__(self, classe_DICOM, ROI_id, slice_id):
        DP = classe_DICOM.DP
        self.nom = DP.set_ROI[ROI_id]['name']

        try:
            self.matrice = get_appartenance_contourage(DP.n_points, DP.maillage, DP.get_DICOM_contourage(ROI_id, slice_id))
        except KeyError:
            print 'ROI <' + str(ROI_id) + ' : ' + str(self.nom) + '> absente de la slice ' + str(slice_id)

        self.n_points = DP.n_points
        self.dimensions = DP.dimensions
        self.maillage = DP.maillage
        self.ROI_id = ROI_id
        self.slice_id = slice_id
    def afficher(self): # Pour afficher le contourage
        plt.imshow(self.matrice, origin='lower')
        plt.show()


class Groupe_contourages:  # POUR UNE SLICE
    def __init__(self, classe_DICOM, slice_id):
        self.dict_classes_contourages = {}
        self.dict_ROI = {}
        self.slice_id = slice_id
        for ROI_id in classe_DICOM.DP.set_ROI:
            self.dict_classes_contourages[classe_DICOM.DP.set_ROI[ROI_id]['name']] = Contourage_from_DP(classe_DICOM, ROI_id, slice_id)
            self.dict_ROI[ROI_id] = classe_DICOM.DP.set_ROI[ROI_id]['name']






if __name__ == '__main__':

    DICOM = DicomParser(r'C:\Users\beauchesne\Desktop\Python stage Bordeaux\19-07-2017_fusion_code_thibault\data_tests\prostate', RT_structure_id=158)
    contourage = Contourage_from_DP(DICOM, 5, 89)


    print contourage.matrice




