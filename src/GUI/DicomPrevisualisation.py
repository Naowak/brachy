#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DicomPrevisualisation.py
""" Classe permettant de gerer les options de previsualisation (dose) """
# Author : Thibault PARPAITE, Cyrille BEAUCHESNE
# Copyright (c) 2017, CELIA Bordeaux
# This file is part of cythi, released under a BSD license.

from MainGUI import *
from threading import Thread
from MultiSlider import *

class DicomPrevisualisation(tk.Frame):
    """
    Classe fille de DicomLeftWindow
    Permet de gerer les options de previsualisation de dose
    Permet de lancer les calculs (ou recupérer ceux-ci s'ils ont été gardés en mémoire)
    Permet de lancer les calculs finaux avec la position exacte des sources
    """
    def __init__(self, parent, dicom_navigation):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.dicom_navigation = dicom_navigation
        
        self.initialize()

    def initialize(self):
        # Repertoire de travail
        tk.Label(self, text="Répertoire de travail").grid(row=0, column=0, sticky=tk.W)

        filename = self.dicom_navigation.PATH_ressources + "table_multiple.png"
        img = Image.open(filename)

        self.button_table_multiple = ImageTk.PhotoImage(img)
        open_button = tk.Button(self, image=self.button_table_multiple, \
                                relief=tk.FLAT, command=self.OnSelectWorkingDirectory)
        open_button.grid(row=0, column=1, sticky=tk.E)
        
        # Choix algorithme
        tk.Label(self, text="Algorithme").grid(row=1, column=0, sticky=tk.W)
                 
        liste_options = ('M1', 'M2')
        self.algorithme = tk.StringVar(value=liste_options[0])
        om = tk.OptionMenu(self, self.algorithme, *liste_options)
        om.grid(row=1, column=1, sticky=tk.E)

        # Choix rayon 
        self.rayon_x = tk.DoubleVar(value=0.6)
        tk.Label(self, text="Rayon (x, y)").grid(row=2, column=0, stick=tk.W)
        e = tk.Entry(self, justify=tk.RIGHT, textvariable=self.rayon_x, width=3)
        e.grid(row=2, column=1, sticky=tk.W)

        self.rayon_y = tk.DoubleVar(value=0.6)
        e = tk.Entry(self, justify=tk.RIGHT, textvariable=self.rayon_y, width=3)
        e.grid(row=2, column=1, sticky=tk.E)

        # Choix energie
        self.energie = tk.DoubleVar(value=0.03)
        tk.Label(self, text="Energie").grid(row=3, column=0, stick=tk.W)
        e = tk.Entry(self, justify=tk.RIGHT, textvariable=self.energie, width=7)
        e.grid(row=3, column=1, sticky=tk.E)

        # Choix intensite
        self.intensite = tk.DoubleVar(value=1E20)
        tk.Label(self, text="Intensité").grid(row=4, column=0, stick=tk.W)
        e = tk.Entry(self, justify=tk.RIGHT, textvariable=self.intensite, width=7)
        e.grid(row=4, column=1, sticky=tk.E)

        # Granularité source
        self.granularite_source = tk.IntVar(value=5)
        tk.Label(self, text="Granularité source (px)").grid(row=5, column=0, stick=tk.W)
        e = tk.Entry(self, justify=tk.RIGHT, textvariable=self.granularite_source, width=7)
        e.grid(row=5, column=1, sticky=tk.E)

        # Raffinement source
        self.raffinement = tk.IntVar(value=1)
        tk.Label(self, text="Raffinement").grid(row=6, column=0, stick=tk.W)
        e = tk.Entry(self, justify=tk.RIGHT, textvariable=self.raffinement, width=7)
        e.grid(row=6, column=1, sticky=tk.E)

        # Zone d'influence (mm)
        self.zone_influence = tk.DoubleVar(value=50)
        tk.Label(self, text="Zone d'influence (mm)").grid(row=7, column=0, stick=tk.W)
        e = tk.Entry(self, justify=tk.RIGHT, textvariable=self.zone_influence, width=7)
        e.grid(row=7, column=1, sticky=tk.E)

        # Contourage cible (le vrai est cree ailleurs avec une version dediee)
        tk.Label(self, text="Contourage cible").grid(row=8, column=0, sticky=tk.W)
        liste_options = [""]

        self.contourage_cible_id = None
        self.contourage_cible_name = tk.StringVar(value="ROI")
        
        om = tk.OptionMenu(self, self.contourage_cible_name, *liste_options)
        om.config(width=5)
        om.grid(row=8, column=1, sticky=tk.E)

        # Affichage sources precalculees
        tk.Label(self, text="Affichage des sources précalculées").grid(row=9, column=0, sticky=tk.W)
        self.checkbox_display_sources = tk.IntVar()
        checkbox = tk.Checkbutton(self, variable=self.checkbox_display_sources, \
                                  command=self.OnUpdateAfficherSources)
        checkbox.grid(row=9, column=1, sticky=tk.E)

        # Affichage de la zone d'influence
        tk.Label(self, text="Affichage de la zone d'influence").grid(row=10, column=0, sticky=tk.W)
        self.checkbox_display_area = tk.IntVar()
        self.grey_checkbox = tk.Checkbutton(self, variable=self.checkbox_display_area, \
                                  state=tk.DISABLED, \
                                  command=self.OnUpdateAfficherZoneInfluence)
        self.grey_checkbox.grid(row=10, column=1, sticky=tk.E)

        # Prévisualisation plusieurs slices
        tk.Label(self, text="Prévisualisation plusieurs slices").grid(row=11, column=0, sticky=tk.W)
        self.checkbox_all_slices = tk.IntVar()
        checkbox = tk.Checkbutton(self, variable=self.checkbox_all_slices, \
                                  command=None)
        checkbox.grid(row=11, column=1, sticky=tk.E)

        # Separateur
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=12, padx=10, pady=10, columnspan=2)

        # Bouton pour lancer la previsualisation
        filename = self.dicom_navigation.PATH_ressources + "cog.gif"
        img = Image.open(filename)
        self.button_previsualisation = ImageTk.PhotoImage(img)
        button = tk.Button(self, text="Lancer la previsualisation", image=self.button_previsualisation, \
                           relief=tk.RAISED, compound="right", command=partial(self.OnLancerCalculs, calculs_finaux=False))
        button.grid(row=13, padx=2, pady=2, sticky=tk.W)

        # Bouton pour lancer les calculs finaux
        filename = self.dicom_navigation.PATH_ressources + "cog.gif"
        img = Image.open(filename)
        self.button_calculs = ImageTk.PhotoImage(img)
        button = tk.Button(self, text="Lancer calculs finaux", image=self.button_calculs, \
                                relief=tk.RAISED, compound="right",  command=partial(self.OnLancerCalculs, calculs_finaux=True))
        button.grid(row=14, padx=2, pady=2, sticky=tk.W)

        # Separateur
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=15, padx=10, pady=10, columnspan=2)

        # Bouton pour activer toutes les sources
        button = tk.Button(self, text="Activer toutes les sources", \
                           relief=tk.RAISED, command=self.OnAddAllSources)
        button.grid(row=16, padx=2, pady=2, sticky=tk.W)

        # Bouton pour retirer toutes les sources
        button = tk.Button(self, text="Retirer toutes les sources", \
                           relief=tk.RAISED, command=self.OnRemoveAllSources)
        button.grid(row=17, padx=2, pady=2, sticky=tk.W)

        # Bouton pour optimiser le dépot de dose
        button = tk.Button(self, text="Optimiser le dépot de dose", \
                           relief=tk.RAISED, command=None)
        button.grid(row=18, padx=2, pady=2, sticky=tk.W)

        # Separateur
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=19, padx=10, pady=10, columnspan=2)

        # Sliders permettant de gérer les options d'isodoses (min et max)
        self.isodose_values = [0] * 5
        self.isodose_values[0] = tk.DoubleVar()
        self.isodose_values[1] = tk.DoubleVar()
        self.isodose_values[2] = tk.DoubleVar()
        self.isodose_values[3] = tk.DoubleVar()
        self.isodose_values[4] = tk.DoubleVar()
        
        self.multislider = MultiSlider(self, cursors_values=self.isodose_values,
                                       from_=0.001, to=0.15, resolution=0.001,
                                       command=self.OnChangeIsodose)
        self.multislider.grid(row=20, column=0)

        # Densite lu
        tk.Label(self, text="Densité lue").grid(row=21, column=0, sticky=tk.W)

        self.densite_lu = tk.IntVar(value=1)
        checkbox = tk.Checkbutton(self, variable=self.densite_lu,
                                  command=self.OnUpdateDensiteLu)
        checkbox.grid(row=21, column=1, sticky=tk.E)
    

    def load_initial_values(self):
        """ Chargement des valeurs par défaut lorsqu'on a fini le parsing """
        self.dicom_navigation.dicom_parser.set_granularite_source(self.granularite_source.get())
        self.dicom_navigation.dicom_parser.set_zone_influence(self.zone_influence.get())


    def OnChangeIsodose(self):
        if self.dicom_navigation.dicom_parser is None:
            return

        isodose_real_values = [ isodose_value.get() for isodose_value in self.isodose_values ]
        self.dicom_navigation.dicom_parser.set_isodose_values(isodose_real_values)

        if self.dicom_navigation.slice.get_dose_mode() == 1:
            self.dicom_navigation.refresh()


    def OnSelectWorkingDirectory(self):
        """ Choix du repertoire de travail, où seront sauvegardés les calculs """
        working_directory = tkFileDialog.askdirectory(initialdir="~/tmp/")
        
        if (working_directory == ""):
            return
    
        self.dicom_navigation.set_working_directory(working_directory)


    def OnUpdateDensiteLu(self):
        """ On a déjà calculé les doses correspondant à densité constante ou densité lu """
        self.dicom_navigation.dicom_parser.set_densite_lu(self.densite_lu.get())

        if self.dicom_navigation.slice.get_dose_mode() == 1:
            self.dicom_navigation.slice.set_dose_mode_OFF()
            self.OnRemoveAllSources()


    def OnUpdateAfficherSources(self):
        """ Affiche/cache les sources prises en compte pour la prévisualisation """
        # WARNING : Choisir contourage cible
        if (self.dicom_navigation.dicom_parser.get_contourage_cible_id() is None) or (self.dicom_navigation.get_working_directory() is None):
            showwarning("Attention", "Veuillez d'abord choisir un répertoire de travail et un contourage cible.")
            return
        
        if self.checkbox_display_sources.get() == 1:
            self.grey_checkbox.config(state=tk.NORMAL)
        else:
            self.checkbox_display_area.set(0)
            self.grey_checkbox.config(state=tk.DISABLED)
            self.dicom_navigation.display_settings["domaine"] = 0

        self.dicom_navigation.dicom_parser.set_granularite_source(self.granularite_source.get())
        self.dicom_navigation.display_settings["sources"] = self.checkbox_display_sources.get()
        self.dicom_navigation.slice.refresh_sources()
        self.dicom_navigation.refresh()
        


    def OnUpdateAfficherZoneInfluence(self):
        """ Affiche/cache la zone d'influence calculée à partir des sources """
        self.dicom_navigation.dicom_parser.set_zone_influence(self.zone_influence.get())
        self.dicom_navigation.display_settings["domaine"] = self.checkbox_display_area.get()
        self.dicom_navigation.slice.refresh_domaine()
        self.dicom_navigation.refresh()


    def OnLancerCalculs(self, calculs_finaux=False):
        slice = self.dicom_navigation.slice
        dicom_hdv = self.dicom_navigation.get_dicom_hdv()

        # WARNING : Choisir contourage cible
        if (self.dicom_navigation.dicom_parser.get_contourage_cible_id() is None) or (self.dicom_navigation.get_working_directory() is None):
            showwarning("Attention", "Veuillez d'abord choisir un répertoire de travail et un contourage cible.")
            return

        # Recuperation des parametres
        self.dicom_navigation.dicom_parser.set_granularite_source(self.granularite_source.get())
        self.dicom_navigation.dicom_parser.set_zone_influence(self.zone_influence.get())
        self.dicom_navigation.dicom_parser.set_raffinement(self.raffinement.get())
        self.dicom_navigation.dicom_parser.set_densite_lu(self.densite_lu.get())
        
        isodose_real_values = [ isodose_value.get() for isodose_value in self.isodose_values ]
        self.dicom_navigation.dicom_parser.set_isodose_values(isodose_real_values)

        options = { 'algorithme': self.algorithme.get(),
                    'rayon': (self.rayon_x.get(),
                              self.rayon_y.get(), 1),
                    'direction_M1': (0., 0., 0.), # Curietherapie
                    'spectre_mono': (self.intensite.get(), self.energie.get()),
                    'densite_lu': self.densite_lu.get() }

        if self.checkbox_all_slices.get() == 0:
            # Lancement du thread pour la slice courante
            thread_calculs = LancerCalculs(self.dicom_navigation, self.dicom_navigation.slice, options, calculs_finaux)
            thread_calculs.start()
        else:
            # Lancement des threads pour toutes les slices contourées
            self.lancer_calculs_all_slices(options, calculs_finaux)        


    def OnUpdateContourageCible(self, ROIname):
        """
        Permet de choisir dans quel contourage la prévisualisation doit etre réalisée
        Typiquement c'est le PTV de la prostate qui est choisi
        """
        ROI_id = self.ROIname_to_ROIid(ROIname)
        self.contourage_cible_id = ROI_id

        # Comme si on cochait la checkbox d'affichage
        self.dicom_navigation.parent.dicom_left_window.dicom_contourage.dict_lines[ROI_id]['disp'].set(1)
        self.dicom_navigation.parent.dicom_left_window.dicom_contourage.OnUpdateContourage(ROI_id)
        
        self.dicom_navigation.dicom_parser.set_contourage_cible_id(self.contourage_cible_id)

        # Actualisation de l'affichage
        if self.dicom_navigation.display_settings["sources"] == 1:
            self.dicom_navigation.slice.refresh_sources()

        if self.dicom_navigation.display_settings["domaine"] == 1:
            self.dicom_navigation.slice.refresh_domaine()
            
        self.dicom_navigation.refresh()


    def OnAddAllSources(self):
        # WARNING : Choisir contourage cible
        if (self.dicom_navigation.dicom_parser.get_contourage_cible_id() is None) or (self.dicom_navigation.get_working_directory() is None):
            showwarning("Attention", "Veuillez d'abord choisir un répertoire de travail et un contourage cible.")
            return

        if self.dicom_navigation.slice.get_dose_mode() == 0:
            showwarning("Attention", "Veuillez d'abord lancer les calculs de prévisualisation.")
            return

        self.dicom_navigation.slice.add_all_sources()
        
        # Refresh
        self.dicom_navigation.get_dicom_hdv().update_hdv()
        self.dicom_navigation.get_dicom_view().refresh_window()


    def OnRemoveAllSources(self):
        self.dicom_navigation.slice.remove_all_sources()
        self.dicom_navigation.refresh()

        # Refresh
        self.dicom_navigation.get_dicom_hdv().update_hdv()
        self.dicom_navigation.get_dicom_view().refresh_window()


    def create_contourage_cible_menu(self):
        """ Gère le menu déroulant permettant de choisir le contourage cible """
        # Reverse ROI dictionnary for optionmenu
        set_ROI = self.dicom_navigation.dicom_parser.get_set_ROI()
        self.ROI_name_LUT = dict((v['name'], k) for k, v in set_ROI.iteritems())
        
        liste_options = self.ROI_name_LUT.keys()
        initial_ROI_name = "ROI"
        self.contourage_cible_name.set(initial_ROI_name)
        
        om = tk.OptionMenu(self, self.contourage_cible_name, *liste_options, command=self.OnUpdateContourageCible)
        om.config(width=5, anchor='w')
        om.grid(row=8, column=1, sticky=tk.E)


    def ROIname_to_ROIid(self, ROIname):
        return self.ROI_name_LUT[ROIname]

    
    def lancer_calculs_all_slices(self, options, calculs_finaux):
        dicom_parser = self.dicom_navigation.dicom_parser
        ROI_id = dicom_parser.get_contourage_cible_id()

        # On lance un thread pour chaque slice contourée pour le ROI correspondant au contourage cible
        for (UID, array) in self.dicom_navigation.contourages[ROI_id].iteritems():
            slice_id = dicom_parser.UID_to_sliceid_LUT[UID]
            thread_calculs = LancerCalculs(self.dicom_navigation, dicom_parser.get_slice(slice_id), options, calculs_finaux)
            thread_calculs.start()
            
        
class LancerCalculs(Thread):
    """
    Thread chargé de lancer les calculs de previsualisation (ou calculs finaux) en parallèle du programme principal
    Le principe de la délégation est utilisé pour utiliser les informations relatives à dicom_previsualisation
    """

    def __init__(self, dicom_navigation, slice, options, calculs_finaux=False):
        Thread.__init__(self)
        self.dicom_navigation = dicom_navigation
        self.slice = slice
        self.options = options
        self.calculs_finaux = calculs_finaux

    def run(self):
        """ Code à exécuter pendant l'exécution du thread """
        # Calcul des sources à placer pour la prévisualisation (réparties en fonction du ROI cible)
        self.slice.refresh_sources()
        self.slice.refresh_domaine()
        
        # Verification si des calculs sont en memoire
        answer = False
        if self.slice.dose_already_calculated() and (not self.calculs_finaux):
            message = "Des calculs de prévisualisation sont en mémoire pour la slice " + str(self.dicom_navigation.slice_id + 1) + ", voulez-vous les utiliser ? Si vous répondez NON, ceux-ci seront relancés."
            answer = askyesno("Lancer prévisualisation", message)
            
        if not answer:
            # Affichage de "Calculs en cours..."
            self.slice.set_calculs_en_cours(1)
            self.slice.set_dose_mode_OFF() # Au cas où on soit déjà en dose_mode
            self.dicom_navigation.refresh()
            
            # Generation des fichiers .don
            if self.calculs_finaux:
                self.dicom_navigation.dicom_parser.generate_DICOM_calculs_finaux(self.slice.get_slice_id(),
                                                                                 self.dicom_navigation.working_directory,
                                                                                 self.options)
            else:
                self.slice.preparatifs_precalculs() # Calcul de la densite, HU_array, etc.
                self.dicom_navigation.dicom_parser.generate_DICOM_previsualisation(self.slice.get_slice_id(),
                                                                                   self.dicom_navigation.working_directory,
                                                                                   self.densite_lu.get(),
                                                                                   self.options)

            # Puis Lancement du calcul M1
            command = self.dicom_navigation.PATH_start_previsualisation + " " + self.slice.get_slice_directory() + " " + str(self.dicom_navigation.densite_lu.get())
            os.system(command)

            # On retire l'affichage de "Calculs en cours..."
            self.slice.set_calculs_en_cours(0)
                
        # Implicite : Si answer == True, alors on recupere les calculs deja effectués

        # Update du dose mode et HDV
        self.slice.set_dose_mode_ON()
        self.dicom_navigation.get_dicom_contourage().compute_appartenances_contourage_slice(self.slice)
        self.dicom_navigation.get_dicom_hdv().update_hdv()
        self.dicom_navigation.refresh()
