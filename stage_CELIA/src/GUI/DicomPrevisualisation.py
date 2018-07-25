#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DicomPrevisualisation.py
""" Classe permettant de gerer les options de previsualisation (dose) """
# Author : Thibault PARPAITE, Cyrille BEAUCHESNE
# Copyright (c) 2017, CELIA Bordeaux
# This file is part of cythi, released under a BSD license.

import os
import matplotlib.pyplot as plt
from MainGUI import *
from threading import Thread
from MultiSlider import *
from Atlas import *
from Img_Density import *
import Similarity as simy

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
        self.rayon_x = tk.DoubleVar(value=0.06)
        tk.Label(self, text="Rayon (x, y, z)").grid(row=3, column=0, stick=tk.W)
        e = tk.Entry(self, justify=tk.RIGHT, textvariable=self.rayon_x, width=3)
        e.grid(row=2, column=1, sticky=tk.W)

        self.rayon_y = tk.DoubleVar(value=0.06)
        e = tk.Entry(self, justify=tk.RIGHT, textvariable=self.rayon_y, width=3)
        e.grid(row=2, column=1)

        self.rayon_z = tk.DoubleVar(value=0.06)
        e = tk.Entry(self, justify=tk.RIGHT, textvariable=self.rayon_z, width=3)
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
        self.zone_influence = tk.DoubleVar(value=5)
        tk.Label(self, text="Zone d'influence (cm)").grid(row=7, column=0, stick=tk.W)
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
                              self.rayon_y.get(),
                              self.rayon_z.get()),
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

    def use_atlas(self, filename_hounsfield, filename_config) :

        def create_param(filename_hounsfield, filename_config) :
            param = "load_model=true path=sm97-200.3/"
            param += " config_file=" + filename_config 
            param += " density_file=" + filename_hounsfield
            return param 

        def write_into_files(imgs_to_calcul, dirname="tmp/") :

            def write_img(img, filename) :
                size = (len(img[0]), len(img))
                with open(filename, "w+") as f :
                    string = str(size[0]) + " " + str(size[1]) + "\n"
                    f.write(string)
                    for line in img :
                        for elem in line :
                            f.write(str(elem) + " ")
                        f.write("\n")

            if not os.path.exists(dirname):
                os.makedirs(dirname)
            for ind, img in enumerate(imgs_to_calcul) :
                groupe = ind + 1
                filename = dirname + "img" + str(groupe) + ".dat"
                write_img(img, filename)

        param = create_param(filename_hounsfield, filename_config)
        paraka = Atlas(param.split(" "))
        result, sources, density_hu, quart_pred, list_priority, list_diff_without_margin = paraka.run()
        list_diff = copy_source_result_into_slice_img(result, sources, density_hu)
        write_into_files(list_diff)
        return sources, quart_pred, paraka.test_imgs, list_priority, list_diff_without_margin, density_hu

    def copy_dose(self, sources, quart_pred, imgs_test, list_priority, list_diff_without_margin, densite_hu) :

        def get_big_img_dose(four_quart, priority, rayon) :
            NO = four_quart[0].dose
            NE = four_quart[1].dose
            SO = four_quart[2].dose
            SE = four_quart[3].dose
            all_dose = recompose_into_img([NO, NE, SO, SE], priority, rayon)
            return all_dose

        def get_big_img(four_quart, priority, rayon) :
            NO = four_quart[0].my_img
            NE = four_quart[1].my_img
            SO = four_quart[2].my_img
            SE = four_quart[3].my_img
            all_img = recompose_into_img([NO, NE, SO, SE], priority, rayon)
            return all_img

        def write_dose_in_filedose(self, file_dose, img_to_copy, dose, source, rayon) :

            def are_coordonates_to_copy(img_to_copy, x, y, source, rayon) :
                rayon -= 1
                if x >= source[0] - rayon and x <= source[0] + rayon :
                    if y >= source[1] - rayon and y <= source[1] + rayon :
                        # print(source, x, y)
                        return img_to_copy[y][x] == 1
                return False

            def get_dose(x, y, source, rayon, dose) :
                rayon -= 1
                i = x - source[0] + rayon
                j = y - source[1] + rayon
                return dose[i][j]

            def get_new_line(tab_line, dose) :
                tab_line[3] = "{:.8e}".format(dose)
                new_line = ""
                for elem in tab_line : 
                    new_line += "   " + elem
                return new_line


            incomplete_dose = self.dicom_navigation.working_directory + "/slice_" + \
                str(self.slice.get_slice_id()).zfill(3) + "/densite_lu/tmp_dose" + \
                str(i+1).zfill(3) + ".dat"          
            os.rename(file_dose, incomplete_dose)
            rd = open(incomplete_dose, "r")
            wd = open(file_dose, "w+")

            for line in rd :
                if "#" in line :
                    wd.write(line)
                else :
                    tab = [elem for elem in line.split(" ") if elem != ""]
                    if len(tab) == 7 :
                        x = int(tab[4]) - 1
                        y = int(tab[5]) - 1
                        if are_coordonates_to_copy(img_to_copy, x, y, source, rayon) :
                            my_dose = get_dose(x, y, source, rayon, dose)
                            new_line = get_new_line(tab, my_dose)
                            wd.write(new_line)
                        else :
                            wd.write(line)

            rd.close()
            wd.close()

        def plot_in_files(full_dose, full_img, img_to_copy, img_test) :

            def symmetric_img(img) :
                len_first = len(img)
                len_second = len(img[0])
                return [[img[j][i] for j in range(len_second)] for i in range(len_first)]

            fig = plt.figure()
            fig.add_subplot(2, 2, 1)
            plt.imshow(full_dose)
            fig.add_subplot(2, 2, 2)
            plt.imshow(img_to_copy)
            fig.add_subplot(2, 2, 3)
            full_img = symmetric_img(full_img)
            plt.imshow(full_img)
            fig.add_subplot(2, 2, 4)
            img_test = symmetric_img(img_test)
            plt.imshow(img_test)
            fig.savefig("../my_screen/pred_dose_img/pred_dose_" + str(i).zfill(3) + ".png")
            plt.close(fig)

        rayon = Img_Density.RAYON_SUB_IMG
        list_imgs_to_copy = copy_source_result_into_slice_img(list_diff_without_margin, sources, densite_hu)
        for i, four_quart in enumerate(quart_pred) :
            print("Pred " + str(i))
            for q in four_quart :
                print(q)
            print("\n")

            img_to_copy = list_imgs_to_copy[i]
            priority = list_priority[i]
            dose = get_big_img_dose(four_quart, priority, rayon)
            full_img = get_big_img(four_quart, priority, rayon)

            plot_in_files(dose, full_img, img_to_copy, imgs_test[i][0])
            source = sources[i]
            file_dose = self.dicom_navigation.working_directory + "/slice_" + \
                str(self.slice.get_slice_id()).zfill(3) + "/densite_lu/dose_source_" + \
                str(i+1).zfill(3) + ".dat"
            write_dose_in_filedose(self, file_dose, img_to_copy, dose, source, rayon)

    def run(self):
        """ Code à exécuter pendant l'exécution du thread """
        # Calcul des sources à placer pour la prévisualisation (réparties en fonction du ROI cible)
        self.slice.refresh_sources()
        self.slice.refresh_domaine()

        filename_config = None
        filename_hounsfield = None
        
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
                filename_config = self.dicom_navigation.dicom_parser.generate_DICOM_calculs_finaux(self.slice.get_slice_id(),
                                                                                 self.dicom_navigation.working_directory,
                                                                                 self.options)
                # /!\ IL FAUT TROUVER LE HOUNSFIELD pour les calculs finaux !!!!! 
            else:
                self.slice.preparatifs_precalculs(self.options) # Calcul de la densite, HU_array, etc.
                filename_hounsfield, filename_config = self.dicom_navigation.dicom_parser.generate_DICOM_previsualisation(self.slice.get_slice_id(),
                                                                                   self.dicom_navigation.working_directory,
                                                                                   self.options)


            #---------------------------- Intégration de Paraka --------------------------------------
            # Ici on doit lancer Paraka et extraire les zones à calculer et celle à recopier pour chacune de nos sources
            # On doit aussi les enregistrer dans un dossier temporaire de manière à ce que M1 vienne les lire
            # On lance paraka avec le model enregistrer avec le fichier de test correspondant à l'ensemble des images 
            # extraite (zone d'influence) à partir de config_kids.don et densite_hu.don
            sources, quart_pred, imgs_test, list_priority, list_diff_without_margin, densite_hu = self.use_atlas(filename_hounsfield, filename_config)

            # Puis Lancement du calcul M1
            command = self.dicom_navigation.PATH_start_previsualisation + " " + self.slice.get_slice_directory() + " " + str(self.dicom_navigation.densite_lu.get())
            os.system(command)

            #On recopie les doses qui ne devait pas être à recalculer
            #Et on supprime les fichiers dans tmp/
            self.copy_dose(sources, quart_pred, imgs_test, list_priority, list_diff_without_margin, densite_hu)


            # On retire l'affichage de "Calculs en cours..."
            self.slice.set_calculs_en_cours(0)
                
        # Implicite : Si answer == True, alors on recupere les calculs deja effectués

        # Update du dose mode et HDV
        self.slice.set_dose_mode_ON()
        self.dicom_navigation.get_dicom_contourage().compute_appartenances_contourage_slice(self.slice)
        self.dicom_navigation.get_dicom_hdv().update_hdv()
        self.dicom_navigation.refresh()


def reverse_img(img) :
    size = (len(img), len(img[0]))
    new = [[0 for i in range(size[0])] for j in range(size[1])]
    for i in range(size[1]) :
        for j in range(size[0]) :
            new[i][j] = img[j][i]
    return new

def copy_source_result_into_slice_img(result, sources, densite_hu) :
    all_imgs = []
    size = (len(densite_hu[0]), len(densite_hu))
    for ind, source in enumerate(sources) :
        x1 = source[0]
        x2 = source[1]
        res = result[ind]
        res = reverse_img(res)

        img_to_calcul = [[-1 for i in range(size[0])] for j in range(size[1])]
        taille_img = Img_Density.TAILLE_SUB_IMG
        rayon = Img_Density.RAYON_SUB_IMG

        for i in range(taille_img) :
            for j in range(taille_img) :
                y1 = x2 - rayon + i
                y2 = x1 - rayon + j
                img_to_calcul[y1][y2] = res[i][j]

        all_imgs += [img_to_calcul]
    return all_imgs
