#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DicomContourage.py
""" Classe permettant la gestion des contourages dans la GUI """
# Author : Thibault PARPAITE, Cyrille BEAUCHESNE
# Copyright (c) 2017, CELIA Bordeaux
# This file is part of cythi, released under a BSD license.

from MainGUI import *


class DicomContourage(tk.Frame):
    """
    Classe fille de DicomLeftWindow
    Permet de gerer le calcul et l'affichage des contourages en transparence
    Permet egalement de preciser quels contourages a prendre en compte dans l'HDV :
    c'est-à-dire choisir cum/diff et le mode (absolu ou relatif)
    Une slidebar permet egalement de regler la luminosite du fichier DICOM en bas d'onglet
    """
    def __init__(self, parent, dicom_navigation):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.dicom_navigation = dicom_navigation
        self.initialize()


    def initialize(self):
        self.dict_lines = {}
        

    def load_contourage(self):
        self.set_ROI = self.dicom_navigation.dicom_parser.get_set_ROI()
        
        # Loading res
        filename =  self.dicom_navigation.PATH_ressources + "color_button.gif"
        img = Image.open(filename)
        self.color_button = ImageTk.PhotoImage(img)

        tk.Label(self, text="Disp").grid(row=0, column=2, sticky=tk.W)
        tk.Label(self, text="Cum").grid(row=0, column=2)
        tk.Label(self, text="Diff").grid(row=0, column=2, sticky=tk.E)

        row_id = 1
        
        for (ROI_id, contourages) in self.set_ROI.iteritems():
            self.dict_lines[ROI_id] = { 'color': "orange", 'disp': tk.IntVar(), \
                                        'cum': tk.IntVar(), 'diff': tk.IntVar() }

            # Color
            self.dict_lines[ROI_id]['button'] = tk.Button(self, image=self.color_button, \
                                                          relief='flat', \
                                                          background=self.dict_lines[ROI_id]['color'], \
                                                          width=0, height=0, \
                                                          command=partial(self.OnSelectColor, ROI_id))
            self.dict_lines[ROI_id]['button'].grid(row=row_id, column=0, padx=3, pady=2)

            # Text
            self.dict_lines[ROI_id]['name'] = contourages['name']
            self.dict_lines[ROI_id]['label'] = tk.Label(self, text=self.dict_lines[ROI_id]['name'])
            self.dict_lines[ROI_id]['label'].grid(row=row_id, column=1, padx=4)

            # Checkboxes
            checkbox = tk.Checkbutton(self, variable=self.dict_lines[ROI_id]['disp'], \
                                      command=partial(self.OnUpdateContourage, ROI_id))
            checkbox.grid(row=row_id, column=2, sticky=tk.W)
            
            
            checkbox = tk.Checkbutton(self, variable=self.dict_lines[ROI_id]['cum'], \
                                      command=partial(self.OnUpdateHDV, ROI_id, "cum"))
                                                                                           
                                                                                        
            checkbox.grid(row=row_id, column=2)
            
            checkbox = tk.Checkbutton(self, variable=self.dict_lines[ROI_id]['diff'], \
                                      command=partial(self.OnUpdateHDV, ROI_id, "diff"))
            checkbox.grid(row=row_id, column=2,  sticky=tk.E)
            

            row_id += 1

        # Boutons radio
        rad_button = tk.Radiobutton(self, variable = self.dicom_navigation.var_etat_abs_rel, \
                                    value = 'r', text='Volume relatif', \
                                    command=self.dicom_navigation.parent.dicom_right_window.dicom_hdv.mode_volume_relatif)
        rad_button.grid(row=row_id, column=1, pady=10)
        
        rad_button = tk.Radiobutton(self, variable = self.dicom_navigation.var_etat_abs_rel, \
                                    value = 'a', text='Volume absolu', \
                                    command=self.dicom_navigation.parent.dicom_right_window.dicom_hdv.mode_volume_absolu)
        rad_button.grid(row=row_id, column=2, pady=10)
            
        # Creation du menu deroulant dans l'onglet previsualisation
        self.dicom_navigation.get_dicom_previsualisation().create_contourage_cible_menu()

        self.create_slider(row_id)

        # Contraintes
        self.dicom_navigation.get_dicom_contraintes().get_dict_nom_to_id()


    def OnSelectColor(self, ROI_id):
        color = tkc.askcolor(title="Couleur du contourage")[1]

        if color is None:
            return
        
        self.dict_lines[ROI_id]['color'] = color
        self.dict_lines[ROI_id]['button'].config(background=color)
        self.modifier_couleur_contourage(ROI_id, color)
        
        self.dicom_navigation.refresh()


    def OnUpdateContourage(self, ROI_id):
        if self.dict_lines[ROI_id]['disp'].get() == 1:
            self.add_contourage(ROI_id, self.dict_lines[ROI_id]['name'], \
                                self.dict_lines[ROI_id]['color'])
        elif self.dict_lines[ROI_id]['disp'].get() == 0:
            self.remove_contourage(ROI_id)

        self.dicom_navigation.refresh()


    def OnUpdateHDV(self, ROI_id, type_hdv):
        dicom_hdv = self.dicom_navigation.parent.dicom_right_window.dicom_hdv
        
        if self.dict_lines[ROI_id][type_hdv].get() == 1:
            # On coche la case d'affichage si ça n'a pas deja été fait
            if self.dict_lines[ROI_id]['disp'].get() == 0:
                self.dicom_navigation.parent.dicom_left_window.dicom_contourage.dict_lines[ROI_id]['disp'].set(1)
                self.dicom_navigation.parent.dicom_left_window.dicom_contourage.OnUpdateContourage(ROI_id)
            
            # On calcule l'appartenance contourage pour la ROI selectionnee
            self.dicom_navigation.slice.compute_appartenance_contourage(ROI_id)
            
            # Puis on calcule l'HDV
            dicom_hdv.add_hdv(ROI_id, type_hdv, checkbox_mode=True)
            
            # Puis on 'enable' les checkbuttons des contraintes pour lesquelles un contourage est affiché
            if type_hdv == 'cum' and self.dicom_navigation.get_dicom_contraintes().got_contraintes:
                nom_ROI = self.dicom_navigation.get_dicom_contraintes().dict_id_to_nom[ROI_id]
                self.dicom_navigation.get_dicom_contraintes().enable_checkbuttons_pour_une_ROI(nom_ROI)
        elif self.dict_lines[ROI_id][type_hdv].get() == 0:
            dicom_hdv.remove_hdv(ROI_id, type_hdv)
            # On 'disable' les checkbuttons si on décoche le contourage correspondant
            if type_hdv == 'cum' and self.dicom_navigation.get_dicom_contraintes().got_contraintes:
                nom_ROI = self.dicom_navigation.get_dicom_contraintes().dict_id_to_nom[ROI_id]
                self.dicom_navigation.get_dicom_contraintes().disable_checkbuttons_pour_une_ROI(nom_ROI)

        self.dicom_navigation.refresh()


    def compute_appartenances_contourage_slice(self, slice):
        """
        Utilisé lorsqu'on lance les calculs sur une slice pour calculer toutes les
        appartenances contourage (pour avoir les HDV instantannés par la suite)
        """
        for (ROI_id, line) in self.dict_lines.iteritems():
            if line['cum'].get() == 1 or line['diff'].get() == 1:
                slice.compute_appartenance_contourage(ROI_id)            
            
    
    def add_contourage(self, ROI_id, name, color):
        if ROI_id in self.dicom_navigation.contourages:
            return

        dicom_parser = self.dicom_navigation.dicom_parser

        # Recuperation des informations sur le contourage du ROI souhaité
        self.dicom_navigation.contourages[ROI_id] = dicom_parser.get_DICOM_ROI(ROI_id)

        # MAJ de toutes les slices concernees
        for (UID, array) in self.dicom_navigation.contourages[ROI_id].iteritems():
            slice_id = dicom_parser.UID_to_sliceid_LUT[UID]
            dicom_parser.slices[slice_id].add_contourage(ROI_id, name, color, array)
        

    def remove_contourage(self, ROI_id):
        if not(ROI_id in self.dicom_navigation.contourages):
            return

        # MAJ des slices concernees
        for (UID, array) in self.dicom_navigation.contourages[ROI_id].iteritems():
            slice_id = self.dicom_navigation.dicom_parser.UID_to_sliceid_LUT[UID]
            self.dicom_navigation.dicom_parser.slices[slice_id].remove_contourage(ROI_id)

            
        # MAJ de dicom_navigation
        del self.dicom_navigation.contourages[ROI_id]


    def change_label_to_red(self, ROI_id):
        """ Utilisé avec les contraintes """
        self.dict_lines[ROI_id]['label'].config(fg='red')


    def change_label_to_black(self, ROI_id):
        """ Utilisé avec les contraintes """
        self.dict_lines[ROI_id]['label'].config(fg='black')


    def modifier_couleur_contourage(self, ROI_id, color):
        if not (ROI_id in self.dicom_navigation.contourages):
            return
        
        for (UID, array) in self.dicom_navigation.contourages[ROI_id].iteritems():
            slice_id = self.dicom_navigation.dicom_parser.UID_to_sliceid_LUT[UID]
            self.dicom_navigation.dicom_parser.slices[slice_id].modifier_couleur_contourage(ROI_id, color)


    def create_slider(self, current_row_id):
        row_id = current_row_id + 1
        
        tk.Label(self, text="Luminosité min").grid(row=row_id, column=1)
        self.slider_min = tk.Scale(self, from_=0, to=3000, \
                                   variable=self.dicom_navigation.vmin, \
                                   orient=tk.HORIZONTAL, \
                                   command=self.OnChangeLuminosity)
        self.slider_min.grid(row=row_id, column=2)

        row_id += 1

        tk.Label(self, text="Luminosité max").grid(row=row_id, column=1)
        self.slider_max = tk.Scale(self, from_=0, to=3000, \
                                   variable=self.dicom_navigation.vmax, \
                                   orient=tk.HORIZONTAL, \
                                   command=self.OnChangeLuminosity)
        self.slider_max.grid(row=row_id, column=2)


    def OnChangeLuminosity(self, event):
        if self.dicom_navigation.vmin.get() > self.dicom_navigation.vmax.get():
            self.dicom_navigation.vmin.set(self.dicom_navigation.vmax.get())

        self.dicom_navigation.refresh()
