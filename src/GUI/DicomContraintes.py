#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DicomContraintes.py
""" Classe permettant la gestion des contraintes dans la GUI """
# Author : Thibault PARPAITE, Cyrille BEAUCHESNE
# Copyright (c) 2017, CELIA Bordeaux
# This file is part of cythi, released under a BSD license.

from MainGUI import *
import Tkinter as tk
from calcul_HDV import *
from PONT import *


class DicomContraintes(tk.Frame):  # Onglet contenant les outils de gestion de contrainte.
    def __init__(self, parent, dicom_navigation):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.dicom_navigation = dicom_navigation
        self.initialize()

    def initialize(self):  # Pour initialiser le dict des graph tracés ainsi que le dict du respect des contraintes.
        self.got_doses = False  # sera initialisé à true lorsqu'une matrice de dose sera créée
        self.got_contraintes = False  # sera initialisé à true lorsqu'un fichier de contraintes aura été saisi
        self.got_DICOM = False  # sera initialisé à true lorsque l'on aura récupéré le fichier DICOM
        self.dict_graph = self.dicom_navigation.get_dicom_hdv().dict_graph
        self.dict_respect_contraintes = {}  # contiendra l'information sur le respect des contraintes
        self.dict_widgets_contraintes = {}  # contient les widgets dans l'onglet 'contraintes'
        #self.symbole_plus = ImageTk.PhotoImage(
         #   Image.open(r"C:\Users\beauchesne\Desktop\stage_CELIA-master2\stage_CELIA-master\src\plus2.png"))
        #self.symbole_moins = ImageTk.PhotoImage(
         #   Image.open(r"C:\Users\beauchesne\Desktop\stage_CELIA-master2\stage_CELIA-master\src\moins2.png"))

         # Bouton import
         #filename = r"C:\Users\beauchesne\Desktop\stage_CELIA-master2\stage_CELIA-master\src\open-file2.png"
        #img = Image.open(filename)
        #self.button_folder = ImageTk.PhotoImage(img)
        open_button = tk.Button(self, text="Ouvrir un fichier\nde contraintes", #image=self.button_folder,
                                relief=tk.FLAT, compound="top", command=self.OnSelectContrainteFile)
        open_button.grid(row=0, column=0)


    def dose_selectionnee(self):
        self.got_doses = True


    def DICOM_selectionne(self):  # Initialise 'got_DICOM' à True
        self.got_DICOM = True
        

    def OnSelectContrainteFile(self):  # On sélectionne le fichier de contraintes avec un Dialog
        str = tkFileDialog.askopenfilename()
        if str == '':
            return  # On n'essaie pas de répérer un fichier de contraintes si l'on ne l'a pas choisi
        self.get_contraintes(str)


    def get_contraintes(self, path_fichier_contraintes):  # permet de parser le fichier de contraintes et de récupérer
                                                            # ces dernières
        col_start = 0
        self.dict_contraintes = {}  # on enmagasinera les contraintes dans ce dictionnaire
        fichier_contraintes = open(path_fichier_contraintes)
        lignes_fichier = fichier_contraintes.readlines()[col_start:]
        fichier_contraintes.close()

        get_nom = True
        for ligne in lignes_fichier:  # boucle dans laquelle on classifie les contraintes par ROI
            if get_nom == True:
                nom = ligne[:-1]
                self.dict_contraintes[nom] = {}
                get_nom = False
            elif ligne != '\n':
                mots = ligne.split(':')
                dp = mots[0].split()[0]
                contrainte = float(mots[1].split()[0])
                self.dict_contraintes[nom][dp] = contrainte
            else:
                get_nom = True

        dict_lines = self.parent.parent.dicom_left_window.dicom_contourage.dict_lines
        if dict_lines != {}:  # On vérifie si l'on a récupéré la liste des ROI des fichiers DICOM
            self.get_dict_nom_to_id()
            #self.verifier_les_contraintes_des_hdv_choisis()

        self.got_contraintes = True
        self.parent.parent.dicom_right_window.dicom_hdv.got_contraintes_true()
        self.initalize_scroll_frame()  # on lance l'initialisation de la frame qui contiendra les contraintes dans l'onglet 'contraintes'


#    def get_matrices_contourage(self):
 #       dict_lines = self.parent.parent.dicom_left_window.dicom_contourage.dict_lines
  #      self.dict_matrices_contourage = {}
   #     for nom_ROI in self.dict_contraintes:
    #        ROI_id = self.dict_nom_to_id[nom_ROI]
     #       self.dicom_navigation.parent.dicom_left_window.dicom_contourage.add_contourage(ROI_id, dict_lines[ROI_id]['name'],
      #                          dict_lines[ROI_id]['color'])
       #     self.dicom_navigation.slice.compute_appartenance_contourage(ROI_id)
        #    self.dict_matrices_contourage[ROI_id] = self.dicom_navigation.slice.get_appartenance_contourage(ROI_id)


    def initalize_scroll_frame(self):  # initialise la frame contenant la liste des contraintes

        self.background_color = 'white'

        self.frame_set_contraintes = tk.Frame(self)
        self.frame_set_contraintes.grid(row=1, column=0, sticky=tk.W)


        self.canvas_set_contraintes = tk.Canvas(self.frame_set_contraintes, bg=self.background_color)
        self.listFrame = tk.Frame(self.canvas_set_contraintes, bg=self.background_color)
        self.scrollb = tk.Scrollbar(self, orient="vertical", command=self.canvas_set_contraintes.yview)
        self.scrollb.grid(row=2, column=2, sticky='nsew')  #grid scrollbar in master, but
        self.canvas_set_contraintes['yscrollcommand'] = self.scrollb.set   #attach scrollbar to frameTwo

        self.canvas_set_contraintes.create_window((0, 0), window=self.listFrame, anchor='nw')
        self.listFrame.bind("<Configure>", self.AuxscrollFunction)
        self.scrollb.grid_forget()    #Forget scrollbar because the number of pieces remains undefined by the user. But this not destroy it. It will be "remembered" later.

        self.canvas_set_contraintes.pack(fill=tk.BOTH)

        self.scrollb.grid(row=1, column=1, sticky='nsew', padx=2, pady=2)  # grid scrollbar in master, because user had defined the numer of pieces

        self.afficher_set_contraintes()  # On affiche la liste des contraintes

    def get_dict_nom_to_id(self):  # trick pour passer facilement de ROI_id à nom_ROI
        self.dict_nom_to_id = {}
        self.dict_id_to_nom = {}
        dict_set_ROI = self.dicom_navigation.dicom_parser.get_DICOM_set_ROI()
        for ROI_id in dict_set_ROI:
            self.dict_nom_to_id[dict_set_ROI[ROI_id]['name']] = int(ROI_id)
            self.dict_id_to_nom[int(ROI_id)] = dict_set_ROI[ROI_id]['name']


    def afficher_set_contraintes(self):  # On affiche les contraintes dans l'onglet 'contraintes'
        row = 1
        for nom_ROI in self.dict_contraintes:
            self.dict_widgets_contraintes[nom_ROI] = {}
            self.dict_widgets_contraintes[nom_ROI]['bouton_plus'] = tk.Button(self.listFrame, text='+', relief=tk.FLAT,
                                                                         bg=self.background_color, command=partial(self.afficher_contraintes_pour_une_ROI,nom_ROI))
            self.dict_widgets_contraintes[nom_ROI]['bouton_plus'].grid(row=row, column=0)
            self.dict_widgets_contraintes[nom_ROI]['bouton_moins'] = tk.Button(self.listFrame, text='-', relief=tk.FLAT,
                                                                         bg=self.background_color, command=partial(self.ne_plus_afficher_contraintes_pour_une_ROI,nom_ROI))
            self.dict_widgets_contraintes[nom_ROI]['label'] = tk.Label(self.listFrame, text=nom_ROI, bg=self.background_color)
            self.dict_widgets_contraintes[nom_ROI]['label'].grid(row=row, column=1, columnspan=10, sticky=tk.W)
            self.dict_widgets_contraintes[nom_ROI]['row'] = row
            self.dict_widgets_contraintes[nom_ROI]['checkbuttons'] = {}
            self.dict_widgets_contraintes[nom_ROI]['intvars'] = {}
            for contrainte in self.dict_contraintes[nom_ROI]:
                self.dict_widgets_contraintes[nom_ROI]['intvars'][contrainte] = tk.IntVar()
                self.dict_widgets_contraintes[nom_ROI]['intvars'][contrainte].set(1)
                self.dict_widgets_contraintes[nom_ROI]['checkbuttons'][contrainte] = tk.Checkbutton(self.listFrame,
                                    text=contrainte + ' = ' + str(self.dict_contraintes[nom_ROI][contrainte]),
                                    variable=self.dict_widgets_contraintes[nom_ROI]['intvars'][contrainte],
                                    bg=self.background_color, command=partial(self.action_checkbutton_contrainte, nom_ROI, contrainte))
                if self.parent.parent.dicom_left_window.dicom_contourage.dict_lines == {}:
                    self.disable_checkbutton(nom_ROI, contrainte)
                else:
                    ROI_id = self.dict_nom_to_id[nom_ROI]
                    if self.parent.parent.dicom_left_window.dicom_contourage.dict_lines[ROI_id]['cum'].get() == 0:
                        self.disable_checkbutton(nom_ROI, contrainte)
            row += len(self.dict_contraintes[nom_ROI]) + 1
        self.verifier_les_contraintes_des_hdv_choisis()  # on vérifie les contraintes des contourages sélectionnés



    def action_checkbutton_contrainte(self, nom_ROI, contrainte):  # On définit la commande à affectuer par la
                                                                # checkbox d'une contrainte si on la coche ou décoche
        if nom_ROI in self.dict_widgets_contraintes:
            if self.parent.parent.dicom_left_window.dicom_contourage.dict_lines != {}:  # On vérifie si l'on a récupéré les infos sur les ROIs dans les fichiers DICOM
                ROI_id = self.dict_nom_to_id[nom_ROI]
                if self.dict_widgets_contraintes[nom_ROI]['intvars'][contrainte].get() == 1:
                    #if nom_ROI in self.dict_respect_contraintes:
                    #if contrainte in self.dict_respect_contraintes[nom_ROI]
                    self.verifier_contraintes_sur_une_ROI(ROI_id)
                    self.changer_couleur_label(ROI_id)
                else:
                    self.retirer_une_contrainte_du_dict(nom_ROI, contrainte)
                    self.changer_couleur_label(ROI_id)


    def disable_checkbutton(self, nom_ROI, contrainte):  # disable la checkbox d'une contrainte si on a pas calculé le contourage
        self.dict_widgets_contraintes[nom_ROI]['checkbuttons'][contrainte].configure(state=tk.DISABLED)


    def disable_checkbuttons_pour_une_ROI(self, nom_ROI):  # disable toutes les checkboxes d'une ROI
        if nom_ROI in self.dict_widgets_contraintes:
            for contrainte in self.dict_contraintes[nom_ROI]:
                self.disable_checkbutton(nom_ROI, contrainte)


    def enable_checkbutton(self, nom_ROI, contrainte):  # enable une checkbox
        self.dict_widgets_contraintes[nom_ROI]['checkbuttons'][contrainte].configure(state=tk.NORMAL)


    def enable_checkbuttons_pour_une_ROI(self, nom_ROI):  #enable toutes les checkboxes d'une ROI
        if nom_ROI in self.dict_widgets_contraintes:
            for contrainte in self.dict_contraintes[nom_ROI]:
                self.enable_checkbutton(nom_ROI, contrainte)


    def afficher_contraintes_pour_une_ROI(self, nom_ROI):  # Fonction appelée lorsque l'on clique sur le bouton '+' à coté du nom de la ROI
        row = self.dict_widgets_contraintes[nom_ROI]['row']
        self.dict_widgets_contraintes[nom_ROI]['bouton_plus'].grid_forget()
        self.dict_widgets_contraintes[nom_ROI]['bouton_moins'].grid(row=row, column=0)
        for contrainte in self.dict_contraintes[nom_ROI]:
            self.dict_widgets_contraintes[nom_ROI]['checkbuttons'][contrainte].grid(row=row + 1, column=1, sticky=tk.W)
            row += 1


    def ne_plus_afficher_contraintes_pour_une_ROI(self, nom_ROI):# Fonction appelée lorsque l'on clique sur le bouton '-' à coté du nom de la ROI
        row = self.dict_widgets_contraintes[nom_ROI]['row']
        self.dict_widgets_contraintes[nom_ROI]['bouton_moins'].grid_forget()
        self.dict_widgets_contraintes[nom_ROI]['bouton_plus'].grid(row=row, column=0)
        for contrainte in self.dict_contraintes[nom_ROI]:
            self.dict_widgets_contraintes[nom_ROI]['checkbuttons'][contrainte].grid_forget()


    def AuxscrollFunction(self, event):
        # You need to set a max size for frameTwo. Otherwise, it will grow as needed, and scrollbar do not act
        self.canvas_set_contraintes.configure(scrollregion=self.canvas_set_contraintes.bbox("all"), width=200, height=250)


    def d_pourcentage(self, ROI_id, pourcentage):  #  CALCULE PAR EXEMPLE LE D50, D70, ETC POUR UNE ROI DONNÉE. sert à calculer si une contrainte est respectée
        #doses = Doses_from_matrice(loadtxt('dose_test.txt'))
        #contourage = Contourage_from_matrice(loadtxt('decoup_test.txt', dtype=int, delimiter=','),2)

        #appartenance_contourage = self.dict_matrices_contourage[ROI_id]
        appartenance_contourage = self.dicom_navigation.slice.get_appartenance_contourage(ROI_id)
        contourage = Contourage_from_matrice(appartenance_contourage,
                                             ROI_id)  # On crée un objet 'Contourage_from_matrice' à partir du de la matrice booléenne

        doses = Doses_from_matrice(self.dicom_navigation.slice.get_dose_matrix())

        ddc = Doses_dans_contourage(doses, contourage)
        nb_voxels = ddc.nb_voxels
        liste_ddc = ddc.liste
        indice = int(nb_voxels*(1 - (pourcentage/100.0)))
        x1, x2 = liste_ddc[indice-1:indice+1]
        pourcentage_v_voxel = 100.0/nb_voxels
        y1 = pourcentage_v_voxel*(nb_voxels - indice)

        return (y1-pourcentage)*(x2-x1)/pourcentage_v_voxel + x1  # retourne la dose minimale reçue par le pourcentage du volume passé en argument


    def verifier_une_contrainte(self, ROI_id, contrainte):  # Retourne True si la contrainte est respectée et False autrement
        nom_ROI = self.dict_id_to_nom[ROI_id]
        return self.d_pourcentage(ROI_id, float(contrainte[1:])) < self.dict_contraintes[nom_ROI][contrainte]


    def retirer_une_contrainte_du_dict(self, nom_ROI, contrainte): # on enlève une contrainte du dictionnaire de respect des contraintes
                                                                    # si on ne souhaite pas l'appliquer. À appeler quand on décoche une checkbox
        del(self.dict_respect_contraintes[nom_ROI][contrainte])


    def reset_contraintes_du_dict_pour_une_ROI(self, nom_ROI):  # efface les infos relatives au respect des contraintes (true et false) pour un ROI.
                                                                # À appeler lorsque l'on ajoute une source (quand on change la matrice de dépot de dose)
        if nom_ROI in self.dict_widgets_contraintes:
            self.dict_respect_contraintes[nom_ROI] = {}


    def verifier_contraintes_sur_une_ROI(self, ROI_id):  # À APPELER QUAND ON COCHE UNE NOUVELLE CHECKBOX.
                                                                                # VÉRIFIE QUE LES CONTRAINTES SONT RESPECTÉES POUR UNE ROI DONNÉE ET POUR LES
                                                                                # CONTRAINTES SÉLECTIONNÉES. À VENIR...
        nom_ROI = self.dict_id_to_nom[ROI_id]
        if not nom_ROI in self.dict_widgets_contraintes:
            return
        self.reset_contraintes_du_dict_pour_une_ROI(nom_ROI)


        for contrainte in self.dict_widgets_contraintes[nom_ROI]['intvars']:
            if self.dict_widgets_contraintes[nom_ROI]['intvars'][contrainte].get() == 1:
                respect = self.verifier_une_contrainte(ROI_id, contrainte)
                self.dict_respect_contraintes[nom_ROI][contrainte] = respect
                # ajouter commande qui affiche un message et qui met le titre de la ROI en rouge
        self.changer_couleur_label(ROI_id)



    def verifier_les_contraintes_des_hdv_choisis(self):  # vérifie le respect des contraintes pour les contourages choisis
        dict_lines = self.parent.parent.dicom_left_window.dicom_contourage.dict_lines
        for ROI_id in dict_lines:
            if dict_lines[ROI_id]['cum'].get() == 1:
                self.verifier_contraintes_sur_une_ROI(ROI_id)


    def changer_couleur_label(self, ROI_id):  # change la couleur d'une ROI dans l'onglet Contourage pour rouge si une ou plusieurs contraintes
                                            # ne sont pas respectées. Laisse le label noir si toutes les contraintes sont respectées.
        nom_ROI = self.dict_id_to_nom[ROI_id]
        if not nom_ROI in self.dict_widgets_contraintes:
            return
        for contrainte in self.dict_respect_contraintes[nom_ROI]:
            if not self.dict_respect_contraintes[nom_ROI][contrainte]:
                self.dicom_navigation.get_dicom_contourage().change_label_to_red(ROI_id)
                return
        self.dicom_navigation.get_dicom_contourage().change_label_to_black(ROI_id)
