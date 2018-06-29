#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MainGUI.py
""" Classes representant les fenetres principales (mères) de l'application cythi """
# Author : Thibault PARPAITE, Cyrille BEAUCHESNE
# Copyright (c) 2017, CELIA Bordeaux
# This file is part of cythi, released under a BSD license.

import sys
import Tkinter as tk
import tkFileDialog
import ttk
import tkColorChooser as tkc
import matplotlib as mpl
import matplotlib.pyplot as plt

from subprocess import call
from functools import partial
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from tkMessageBox import *

from dicom_parser import *
from slice import *
from DicomView import *
from DicomHDV import *
from DicomContourage import *
from DicomPrevisualisation import *
from DicomContraintes import *


class MainApplication(tk.Tk):
    """ Classe mère (racine) de l'application """
    def __init__(self, parent):
        tk.Tk.__init__(self)
        self.parent = parent
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.initialize()

    def initialize(self):
        self.dicom_navigation = DicomNavigation(self)
        self.menu = Menu(self, self.dicom_navigation)
        self.configure(menu=self.menu)
        self.toolbar = Toolbar(self, self.dicom_navigation)
        self.dicom_right_window = DicomRightWindow(self, self.dicom_navigation)
        self.dicom_left_window = DicomLeftWindow(self, self.dicom_navigation)

        self.toolbar.pack(side="top", fill="both", expand=False)
        self.dicom_right_window.pack(side="right", fill="both", expand=True)
        self.dicom_left_window.pack(side="left", fill="both", expand=False)


class DicomNavigation:
    """
    Cette classe ne représente pas de fenetre a proprement parler. Elle sert de lien entre
    toutes les frames de l'interface graphique pour memoriser des informations essentielles
    sur la session en cours (comme les options d'affichage, le resultat du parsing, etc.)
    """
    def __init__(self, parent):
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.dicom_path = None
        self.dicom_parser = None
        self.checkbox_state = -1

        # Usefull path
        current_directory = os.getcwd()
        self.PATH_initial = current_directory
        self.PATH_start_previsualisation = current_directory + "/src/GUI/start_previsualisation.sh"
        self.PATH_ressources = current_directory + "/ressources/"
        self.working_directory = None

        # Current_slice
        self.slice_id = None
        self.slice = None

        # Contourages
        self.contourages = {}

        # Affichage
        self.figure_dicom = None
        self.figure_HDV = None
        self.display_settings = { "sources": 0, "domaine": 0, "miniature": 0 }

        # Current state
        self.var_etat_abs_rel = tk.StringVar(value="r")  # variable d'etat relatif/absolu
        self.densite_lu = tk.IntVar(value=1)
        
        # Luminosite
        self.vmin = tk.IntVar(value=0)
        self.vmax = tk.IntVar(value=3000)

        # Note Style
        self.note_style = ttk.Style()
        self.note_style.configure("TNotebook", borderwidth=1)
        self.note_style.configure("TNotebook.Tab", borderwidth=1)
        self.note_style.configure("TFrame", background="white", foreground="black", borderwidth=0)


    def start_parsing(self):
        # Loading
        self.dicom_parser = DicomParser(self.dicom_path)
        try :
            self.select_current_slice(90)
        except :
            #correction temporaire pour l'aquisition du premier slice
            #de base Thibault prenait le slice 91 (indice 90)
            #Mais ce slice n'existe pas dans des base de donnée trop petite
            #Donc on prends le 0 par défault si le 90 n'existe pas
            self.select_current_slice(0)
        (self.figure_dicom, self.ax) = self.dicom_parser.get_DICOM_figure()
        self.get_dicom_contourage().load_contourage()
        self.get_dicom_previsualisation().load_initial_values()
        self.refresh()


    def select_current_slice(self, slice_id):
        self.slice_id = slice_id
        self.slice = self.dicom_parser.get_slice(slice_id)
        self.refresh_new_slice()
        

    def refresh(self):        
        self.get_dicom_view().refresh_window()
        self.get_dicom_info().refresh_info()


    def refresh_new_slice(self):
        if self.display_settings["sources"] == 1:
            self.slice.refresh_sources()

        if self.display_settings["domaine"] == 1:
            self.slice.refresh_domaine()

        # MAJ de l'HDV (si dose_matrix est None alors HDV vierge)
        self.get_dicom_hdv().update_hdv()


    def get_dicom_contourage(self):
        return self.parent.dicom_left_window.dicom_contourage


    def get_dicom_previsualisation(self):
        return self.parent.dicom_left_window.dicom_previsualisation


    def get_dicom_contraintes(self):
        return self.parent.dicom_left_window.dicom_contraintes
    

    def get_dicom_info(self):
        return self.parent.dicom_right_window.top_info


    def get_dicom_view(self):
        return self.parent.dicom_right_window.dicom_view


    def get_dicom_hdv(self):
        return self.parent.dicom_right_window.dicom_hdv


    def get_working_directory(self):
        return self.working_directory


    def get_densite_lu(self):
        return self.densite_lu
    

    def set_working_directory(self, working_directory):
        self.working_directory = working_directory

        # Updating working directory into each slices
        for slice in self.dicom_parser.slices:
            slice.set_working_directory(working_directory)
        

class Menu(tk.Menu):
    """ Menus deroulant """
    def __init__(self, parent, dicom_navigation):
        tk.Menu.__init__(self, parent)
        self.parent = parent
        self.dicom_navigation = dicom_navigation
        self.initialize()

    def initialize(self):
        # Create a file menu and add it to the menubar
        file_menu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Choisir un repertoire DICOM", command=self.OnSelectDirectory)
        file_menu.add_command(label="Quitter", command=self.OnQuit)

        help_menu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Afficher l'aide", command=self.OnShowHelp)
        

    def OnQuit(self):
        self.parent.destroy()

        
    def OnSelectDirectory(self):
        str = tkFileDialog.askdirectory()
        
        if (str == ""):
            return
    
        self.parent.dicom_navigation.dicom_path = str
        self.parent.dicom_navigation.start_parsing()

    def OnSelectRT(self):
        return 1

    def OnSelectSlice(self):
        return 1


    def OnShowHelp(self):
        message = "Ce logiciel permet de visualiser les résultats obtenus à partir de l'algorithme M1. \n\
        Il est possible de lancer des calculs de prévisualisation, puis de simuler un dépot de dose en direct avec l'histogramme dose volume (HDV) en support.\n\
        Marche à suivre :\n\
        1) Ouvrir patient -> Choisir un répertoire contenant des fichiers DICOM (.dsm)\n\
        2) Prévisualisation -> Choisir le répertoire de travail (où seront enregistrés les calculs)\n\
        3) Choisir le contourage cible dans le menu déroulant (ROI par défaut)\n\
        4) Lancer la prévisualisation\n\
        - Il y la possibilité de récupérer des calculs déjà effectués\n\
        - Une information -- Calculs en cours -- s'affiche pour indiquer que M1 est en train de tourner pour une slice donnée\n\
        - Une fois les calculs terminés, -- Dose mode -- est activé (une icone l'indique en haut à droite de l'écran)\n\
        5) Contourage -> Cocher les contourages à visualiser sur le HDV\n\
        6) Afficher-Retirer miniature pour voir l'HDV en miniature\n\
        7) Possibilité de switch entre mode absolu et relatif\n\
        BUG : si un bug d'affichage apparait, veuillez actualiser la fenetre en appuyant plusieurs fois sur -- Afficher-Retirer miniature"
        showinfo("Aide basique", message)


class Toolbar(tk.Frame):
    """ Barre d'outils contenant les boutons en haut de page """
    def __init__(self, parent, dicom_navigation):
        tk.Frame.__init__(self, parent, bd=1, relief=tk.RAISED)
        self.parent = parent
        self.dicom_navigation = dicom_navigation
        self.initialize()

    def initialize(self):
        # Button open
        filename = self.dicom_navigation.PATH_ressources + "folder_user.png"
        img = Image.open(filename)
        self.button_folder_user = ImageTk.PhotoImage(img)
        open_button = tk.Button(self, text="Ouvrir patient", image=self.button_folder_user, \
                                relief=tk.FLAT, compound="top", command=self.parent.menu.OnSelectDirectory)
        #open_button = tk.Button(self, text="Toto", relief=tk.FLAT)
        open_button.pack(side=tk.LEFT, padx=2, pady=2)

        # Afficher miniature
        miniature_button = tk.Button(self, text="Afficher/Retirer miniature", relief=tk.FLAT, \
                                     command=self.OnAfficherMiniature)
        miniature_button.pack(side=tk.LEFT, padx=2, pady=2)


    def OnAfficherMiniature(self):
        if self.dicom_navigation.display_settings['miniature'] == 0:
            self.dicom_navigation.display_settings['miniature'] = 1
            current_tab = self.dicom_navigation.parent.dicom_right_window.get_current_tab()

            if current_tab == "Dicom View":
                self.dicom_navigation.parent.dicom_right_window.top_info.canvas_HDV.get_tk_widget().pack(side=tk.RIGHT, fill=tk.Y, expand=False)
            elif current_tab == "HDV":
                self.dicom_navigation.parent.dicom_right_window.top_info.canvas_dicom.get_tk_widget().pack(side=tk.RIGHT, fill=tk.Y, expand=False)

            # Tricky hack pour ne pas avoir le probleme de zoom lorsqu'on met les mignatures (on retrace les canvas initiaux)
            self.dicom_navigation.parent.dicom_right_window.dicom_hdv.canvas.get_tk_widget().update_idletasks()
            self.dicom_navigation.parent.dicom_right_window.dicom_view.canvas.get_tk_widget().update_idletasks()

            #self.dicom_navigation.parent.dicom_right_window.top_info.update()
        elif self.dicom_navigation.display_settings['miniature'] == 1:
            self.dicom_navigation.display_settings['miniature'] = 0
            self.dicom_navigation.parent.dicom_right_window.top_info.canvas_dicom.get_tk_widget().pack_forget()
            self.dicom_navigation.parent.dicom_right_window.top_info.canvas_HDV.get_tk_widget().pack_forget()
            self.dicom_navigation.parent.dicom_right_window.top_info.top_canvas.config(width=600, height=50)

        
class DicomLeftWindow(ttk.Notebook):
    """ Classe mère de la frame de gauche """
    def __init__(self, parent, dicom_navigation):
        # Notebook
        ttk.Notebook.__init__(self, parent, style='TNotebook')
        self.parent = parent
        self.dicom_navigation = dicom_navigation
        self.initialize() 

    def initialize(self):
        self.dicom_contourage = DicomContourage(self, self.dicom_navigation)
        self.dicom_previsualisation = DicomPrevisualisation(self, self.dicom_navigation)
        self.dicom_contraintes = DicomContraintes(self, self.dicom_navigation)
        self.add(self.dicom_contourage, text="Contourage")
        self.add(self.dicom_previsualisation, text="Prévisualisation")
        self.add(self.dicom_contraintes, text="Contraintes")
    

class DicomRightWindow(tk.Frame):
    """ Classe mère de la frame de droite """
    def __init__(self, parent, dicom_navigation):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.dicom_navigation = dicom_navigation
        self.initialize()


    def initialize(self):        
        # Notebook (dicom window + hdv)
        self.notebook = ttk.Notebook(self, style='TNotebook')
        self.dicom_view = DicomView(self, self.dicom_navigation)
        self.dicom_hdv = DicomHDV(self, self.dicom_navigation)
        self.notebook.add(self.dicom_view, text="Dicom View")
        self.notebook.add(self.dicom_hdv, text="HDV")

        # Top frame info
        self.top_info = DicomInfo(self, self.dicom_navigation)

        # Pack
        self.top_info.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        self.notebook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)


    def get_current_tab(self):
        return self.notebook.tab(self.notebook.select(), "text")


class DicomInfo(tk.Frame):
    """ Classe mère de la fenetre DicomInfo, qui contient notamment les miniatures """
    def __init__(self, parent, dicom_navigation):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.dicom_navigation = dicom_navigation
        self.initialize()

    def initialize(self):
        # Drawing top canvas
        figure_hdv = self.dicom_navigation.figure_hdv
        self.top_canvas = tk.Canvas(self, width=600, height=50, borderwidth=1, relief=tk.RAISED)
        self.top_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        # Figure DVH
        self.canvas_HDV = FigureCanvasTkAgg(figure_hdv, self.top_canvas)
        self.canvas_HDV.draw()
        self.canvas_HDV.get_tk_widget().pack_propagate(True) 
        self.canvas_HDV.get_tk_widget().configure(background='black',  highlightcolor='black',\
                                                  highlightbackground='black')
        self.canvas_HDV.get_tk_widget().config(width=600, height=270)
        self.canvas_HDV._tkcanvas.config(highlightthickness=1, relief=tk.RAISED)

        # Figure Dicom
        self.blank_canvas = True
        (fig, axes) = plt.subplots(facecolor="black")

        # Error depending version
        if (mpl.__version__ =='2.0.0'):
            axes.set_facecolor("black")
        else:
            axes.set_facecolor("black")
            
        axes.set_axis_off()
        self.canvas_dicom = FigureCanvasTkAgg(fig, self.top_canvas)
        self.canvas_dicom.get_tk_widget().pack_propagate(True) 
        self.canvas_dicom.get_tk_widget().config(width=500, height=270)
        self.canvas_dicom._tkcanvas.config(highlightthickness=1, relief=tk.RAISED)


    def refresh_info(self):
        # Figure Dicom
        figure_dicom = self.dicom_navigation.figure_dicom    

        # Creation initiale
        if self.blank_canvas:
            self.blank_canvas = False
            self.canvas_dicom.get_tk_widget().destroy()
            self.canvas_dicom = FigureCanvasTkAgg(figure_dicom, self.top_canvas)
            self.canvas_dicom.get_tk_widget().pack_propagate(True)
            self.canvas_dicom.draw()
            self.canvas_dicom.get_tk_widget().configure(background='black',  highlightcolor='black',\
                                                        highlightbackground='black')
            self.canvas_dicom.get_tk_widget().config(width=500, height=270)
            self.canvas_dicom._tkcanvas.config(highlightthickness=1, relief=tk.RAISED)

        # Update
        self.canvas_dicom.draw()






