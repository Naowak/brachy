#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DicomHDV.py
""" Classe permettant la gestion de l'HDV """
# Author : Thibault PARPAITE, Cyrille BEAUCHESNE
# Copyright (c) 2017, CELIA Bordeaux
# This file is part of cythi, released under a BSD license.

from MainGUI import *
from PONT import *
from calcul_HDV import *


class DicomHDV(tk.Frame):
    """
    Classe fille de DicomRightWindow
    Permet de gerer le calcul et l'affichage des HDV
    """
    def __init__(self, parent, dicom_navigation):
        tk.Frame.__init__(self, parent, bg="white")
        self.parent = parent
        self.dicom_navigation = dicom_navigation

        # Utile lors du switch d'onglet
        self.bind("<Visibility>", self.OnSwitchTab)

        # Initialisation des variables
        self.initialize()

    def initialize(self):

        self.ddc = None

        self.got_contraintes = False

        self.dict_graph = {}
        self.dict_plot = {}
        self.dict_doses_max = {}
        self.dict_volumes_max = {}

        self.dict_contraintes = {}
        self.dict_respect_contraintes = {}

        fig = Figure(figsize=(7,6), dpi=100)
        
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.dicom_navigation.figure_hdv = fig            
        self.fig = fig.add_subplot(111)
        self.fig.set_title("Histogramme dose/volume")
        self.fig.plot([],[]) # Initialisation d'un plot vide
        self.fig.set_xlabel('Dose absorbee')
        self.fig.set_ylabel('Pourcentage du volume')
        self.fig.grid(True)
        self.x_lim = 100
        self.y_lim = 100
        self.fig.set_xlim([0, 1.02*self.x_lim])
        self.fig.set_ylim([0, 1.02*self.y_lim])
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
        self.canvas.draw()
        

    def OnSwitchTab(self, event):
        """ Permet d'actualiser les miniatures """
        canvas_HDV = self.dicom_navigation.parent.dicom_right_window.top_info.canvas_HDV
        canvas_dicom = self.dicom_navigation.parent.dicom_right_window.top_info.canvas_dicom
        
        if (self.dicom_navigation.display_settings['miniature'] == 1):
            canvas_HDV.get_tk_widget().pack_forget()
            canvas_dicom.get_tk_widget().pack(side=tk.RIGHT, fill=tk.Y, expand=False)
            # Tricky hack pour ne pas avoir le probleme de zoom lorsqu'on met les mignatures (on retrace les canvas initiaux)
            self.dicom_navigation.parent.dicom_right_window.dicom_hdv.canvas.get_tk_widget().update_idletasks()
            self.dicom_navigation.parent.dicom_right_window.dicom_view.canvas.get_tk_widget().update_idletasks()


    def got_contraintes_true(self):
        self.got_contraintes = True
        

    def update_hdv(self):
        """ Recalcule entièrement le HDV (après une nouvelle source typiquement) """

        dict_var_checkboxes = self.parent.parent.dicom_left_window.dicom_contourage.dict_lines

        # Reset figure
        # Preservation du zoom (1)
        x_lim = self.fig.get_xlim()
        y_lim = self.fig.get_ylim()
        
        # On nettoie le graphe
        self.fig.clear()

        # Preservation du zoom (2)
        self.fig.set_xlim(x_lim)
        self.fig.set_ylim(y_lim)

        # Infos
        self.fig.set_title("Histogramme dose/volume")
        self.fig.set_xlabel('Dose absorbee')
        self.fig.set_ylabel('Pourcentage du volume')
        self.fig.grid(True)

        dose_matrix = self.dicom_navigation.slice.get_dose_matrix()

        # Cas ou aucune source n'est placee
        if dose_matrix is None:
            self.canvas.draw()
            self.parent.top_info.canvas_HDV.draw()
            return

        # On calcule le HDV
        for ROI_id in dict_var_checkboxes:
            if dict_var_checkboxes[ROI_id]['cum'].get() == 1:
                self.add_hdv(ROI_id)
            if dict_var_checkboxes[ROI_id]['diff'].get() == 1:
                self.add_hdv(ROI_id, type_hdv='diff')

        # Contraintes
        if self.got_contraintes:
            self.dicom_navigation.get_dicom_contraintes().verifier_les_contraintes_des_hdv_choisis()

        # Affichage de la version mise a jour
        self.refresh_HDV()

        

    def add_hdv(self, ROI_id, type_hdv='cum', checkbox_mode=False):
        """ Permet d'ajouter un contourage au HDV (appele lorsqu'on coche une case
        Le checkbox_mode sert a definir le moment de l'actualisation de la figure pour
        ne pas avoir un effet sacade
        """

        appartenance_contourage = self.dicom_navigation.slice.get_appartenance_contourage(ROI_id)
        
        contourage = Contourage_from_matrice(appartenance_contourage, ROI_id)  # On crée un objet 'Contourage_from_matrice' à partir du de la matrice booléenne

        dose_matrix = self.dicom_navigation.slice.get_dose_matrix()

        # Cas ou on ajoute pour la premiere fois un contourage
        if dose_matrix is None:
            return
        
        doses = Doses_from_matrice(dose_matrix)  # On crée un objet 'Doses_from_matrice' à partir de la matrice de doses mise à jour

        var = tk.StringVar()  #  À VENIR... VARIABLE D'ÉTAT QUI INDIQUE SI ON EST EN MODE 'VOLUME RELATF' OU 'VOLUME ABSOLU'. CODÉ EN DUR POUR LE MOMENT
        var.set('r')

        self.ddc = Doses_dans_contourage(doses, contourage)  # Triage des doses qui sont dans le contourage.

        if self.ddc.dose_max == 0:  #  Si la dose max est 0, on sait qu'on est à l'extérieur de la zone réduite. ***                  
            return

        if not ROI_id in self.dict_graph:  
            self.dict_graph[ROI_id] = {}  
            self.dict_plot[ROI_id] = {}  
            self.dict_doses_max[ROI_id] = {} 
            if self.dicom_navigation.var_etat_abs_rel.get() == 'a':
                self.dict_volumes_max[ROI_id] = {}  

        self.dict_doses_max[ROI_id][type_hdv] = self.ddc.dose_max

        ###

        if self.dicom_navigation.var_etat_abs_rel.get() == 'r':  # si on est en mode 'volume relatif', le range des axes sera définit différemment
            facteur = 100.0/self.ddc.nb_voxels  # comme l'instance 'axe_volume' créée par les classes hdv_cumulatif et hdv_differentiel contient des données en NOMBRE DE VOXELS
                                                # (et non en pourcentage ou en volume réel), il faut multiplier ces données par le facteur de conversion approprié (il dépend
                                                # de si l'on est en mode 'relatf' ou 'absolu').

        if self.dicom_navigation.var_etat_abs_rel.get() == 'a':  # si on est en mode 'volume absolu'.
            facteur = self.ddc.v_voxel
            self.dict_volumes_max[ROI_id][type_hdv] = self.ddc.v_voxel * self.ddc.nb_voxels 
            self.y_lim = get_max_2D_dic(self.dict_volumes_max)

        ###

        if type_hdv == 'cum':
            hdv = HDV_cumulatif(self.ddc, 100)

        if type_hdv == 'diff':
            hdv = HDV_differentiel(self.ddc, 50)


        self.dict_graph[ROI_id][type_hdv] = hdv
        self.dict_plot[ROI_id][type_hdv], = self.fig.plot(hdv.axe_doses, facteur * hdv.axe_volume)

        ###

        self.x_lim = get_max_2D_dic(self.dict_doses_max) 

        self.fig.set_xlim([0, 1.02*self.x_lim])  # dimension de l'axe des x
        self.fig.set_ylim([0, 1.02*self.y_lim])  # dimension de l'axe des y

        # Contraintes
        if self.got_contraintes and type_hdv == 'cum':  # 'got_contraintes' SERA INITALISÉE À 'TRUE' LORSQUE L'ON AURA RÉCUPÉRÉ LE FICHIER DE CONTRAINTES
            self.dicom_navigation.get_dicom_contraintes().verifier_contraintes_sur_une_ROI(ROI_id)

        # Modifier
        if checkbox_mode:
            self.refresh_HDV()


    def remove_hdv(self, ROI_id, type_hdv='cum'):
        """ Retire un contourage de l'HDV (quand on decoche une case) """

        # Aucune source
        dose_matrix = self.dicom_navigation.slice.get_dose_matrix() 
        if dose_matrix is None:
            return

        if not ROI_id in self.dict_graph:  # En cas où une ROI a été cochée mais qu'elle ne se trouve pas dans la zone reduite, on ne trace pas de graph.
            return                         # Et donc, on essaie pas de retirer un HDV qui n'est pas en mémoire.

        del (self.dict_graph[ROI_id][type_hdv])
        self.dict_plot[ROI_id][type_hdv].remove()  # commande 'remove' nécessaire pour effacer le graph correspondant à la case décochée
        del (self.dict_plot[ROI_id][type_hdv])
        del (self.dict_doses_max[ROI_id][type_hdv]) 

        if self.dicom_navigation.var_etat_abs_rel.get() == 'a':
            del (self.dict_volumes_max[ROI_id][type_hdv])  
            volume_max = get_max_2D_dic(self.dict_volumes_max)  
            if volume_max != 0:  # il faut ajuster l'axe des y en fonction du plus grand volume présent 'dict_volumes_max'.
                self.y_lim = volume_max  # Et on redéfinit les limites conséquemment.

        dose_max = get_max_2D_dic(self.dict_doses_max) 
        if dose_max != 0:  # On ajuste aussi l'axe des x en fonction de la plus grande dose présente
            self.x_lim = dose_max  

        self.fig.set_xlim([0, 1.02 * self.x_lim])  # dimension de l'axe des x
        self.fig.set_ylim([0, 1.02 * self.y_lim])  # dimension de l'axe des y

        # Contraintes
        if self.got_contraintes and type_hdv == 'cum':
            nom_ROI = self.dicom_navigation.get_dicom_contraintes().dict_id_to_nom[ROI_id]
            self.dicom_navigation.get_dicom_contraintes().reset_contraintes_du_dict_pour_une_ROI(nom_ROI)
            self.dicom_navigation.get_dicom_contourage().change_label_to_black(ROI_id)

        self.refresh_HDV()




    def mode_volume_relatif(self):
        """ Pour passer de relatif à absolu et vice_versa. """

        # Pas de source activee
        dose_matrix = self.dicom_navigation.slice.get_dose_matrix() 
        if dose_matrix is None: 
            return  

        if self.dicom_navigation.slice.get_dose_mode() == 0:
            return

        self.dict_volumes_max = {}
        for ROI_id in self.dict_graph:  # on retrace tous les graph présents dans 'dict_graph' (tous ceux affichés à l'écran).
            for type_hdv in self.dict_graph[ROI_id]:
                self.dict_plot[ROI_id][type_hdv].remove()  # on retire d'abord les anciens graph tracés dans dict_plot.

                facteur = 100.0 / self.dict_graph[ROI_id][type_hdv].nb_voxels
                self.dict_plot[ROI_id][type_hdv], = self.fig.plot(self.dict_graph[ROI_id][type_hdv].axe_doses,
                                                                  facteur * self.dict_graph[ROI_id][type_hdv].axe_volume)  # on multiplie 'axe volume' par le facteur approprié.
        self.y_lim = 100
        self.fig.set_xlabel('Dose absorbee')
        self.fig.set_ylabel('Pourcentage du volume')
        self.fig.set_ylim([0, 1.02 * self.y_lim])
        self.refresh_HDV()
        

    def mode_volume_absolu(self):
        """ Pour passer de relatif à absolu et vice_versa. """
        # Pas de source activee
        dose_matrix = self.dicom_navigation.slice.get_dose_matrix()
        if dose_matrix is None: 
            return 

        if self.dicom_navigation.slice.get_dose_mode() == 0:
            return

        for ROI_id in self.dict_graph:  # on retrace tous les graph présents dans 'dict_graph' (tous ceux affichés à l'écran).
            self.dict_volumes_max[ROI_id] = {}  # Quand on passe en mode volume absolu, on crée un dict contenant les volumes max pour ajuster les axes.
            for type_hdv in self.dict_graph[ROI_id]:
                self.dict_volumes_max[ROI_id][type_hdv] = self.dict_graph[ROI_id][type_hdv].v_voxel * self.dict_graph[ROI_id][type_hdv].nb_voxels
                self.dict_plot[ROI_id][type_hdv].remove()  # on retire d'abord les anciens graph tracés dans dict_plot
                facteur = self.dict_graph[ROI_id][type_hdv].v_voxel
                self.dict_plot[ROI_id][type_hdv], = self.fig.plot(self.dict_graph[ROI_id][type_hdv].axe_doses,
                                                                  facteur * self.dict_graph[ROI_id][
                                                                      type_hdv].axe_volume)  # on multiplie 'axe volume' par le facteur approprié.
        self.fig.set_xlabel('Dose absorbee')
        self.fig.set_ylabel('Volume absolu (cm^3)')
        volume_max = get_max_2D_dic(self.dict_volumes_max) 
        if volume_max != 0:  
            self.fig.set_ylim([0, 1.02 * volume_max])  

        self.refresh_HDV()


    def get_contraintes(self, fichier_contraintes):
        """ À ACTIVER LORSQUE LE FICHIER DE CONTRAINTES EST SAISI """
        col_start = 0
        self.dict_contraintes = {}
        lignes_fichier = fichier_contraintes.readlines()[col_start:]

        get_ROI_id = True
        for ligne in lignes_fichier:
            if get_ROI_id == True:
                ROI_id = int(ligne[:-1])
                self.dict_contraintes[ROI_id] = {}
                get_ROI_id = False
            elif ligne != '\n':
                mots = ligne.split(':')
                dp = mots[0].split()[0]
                contrainte = float(mots[1].split()[0])
                self.dict_contraintes[ROI_id][dp] = contrainte
            else:
                get_ROI_id = True
        fichier_contraintes.close()

        self.got_contraintes = True
        for ROI_id in self.dict_graph:
            self.verifier_contraintes(ROI_id)


    def d_pourcentage(self, ROI_id, pourcentage):
        ROI_id_string = str(ROI_id)
        axe_doses = self.dict_graph[ROI_id_string + 'cum'].axe_doses
        axe_volume = self.dict_graph[ROI_id_string + 'cum'].axe_volume
        for i in range(len(axe_doses)):
            if axe_volume[i] < pourcentage:
                indice = i
                break
        x1, x2 = axe_doses[indice-1:indice+1]
        y1, y2 = axe_volume[indice-1:indice+1]

        return (y1-pourcentage)*(x2-x1)/(y1-y2) + pourcentage


    def verifier_contraintes(self, ROI_id):
        for contrainte in self.dict_contraintes[ROI_id]:
            self.dict_respect_contraintes[ROI_id] = {}
            if self.d_pourcentage(ROI_id, float(contrainte[1:])) < self.dict_contraintes[ROI_id][contrainte]:
                self.dict_respect_contraintes[ROI_id][contrainte] = True  # True veux dire que ça respecte la contrainte
            else:
                self.dict_respect_contraintes[ROI_id][contrainte] = False
        # ajouter commande qui affiche un message et qui met le titre de la ROI en rouge


    def refresh_HDV(self):
        """ Permet d'afficher la figure dans les differents canvas (miniature et grand) """
        self.canvas.draw()
        self.dicom_navigation.parent.dicom_right_window.top_info.canvas_HDV.draw()
        
