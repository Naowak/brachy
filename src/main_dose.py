# -*- coding: utf-8 -*-
import sys
sys.path.append("../resources/")
sys.path.append("../code_cyrille/")

import Tkinter as tk
import tkFileDialog
import ttk
import tkColorChooser as tkc

from subprocess import call
from functools import partial
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import Figure, FigureCanvasTkAgg, NavigationToolbar2TkAgg
from dicom_parser import *
from slice import *
from PONT import *
from classes_primaires import * 


# Monkey Patching
def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)

tk.Canvas.create_circle = _create_circle


class MainApplication(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self)
        self.parent = parent
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
        self.PATH_lance_KIDS = current_directory + "/lance_KIDS"
        self.PATH_ressources = current_directory + "/../ressources/"

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
        self.select_current_slice(90)
        (self.figure_dicom, self.ax) = self.dicom_parser.get_DICOM_figure()
        self.get_dicom_contourage().load_contourage()
        self.refresh()


    def select_current_slice(self, slice_id):
        self.slice_id = slice_id
        self.slice = self.dicom_parser.get_slice(slice_id)
        

    def refresh(self):            
        self.get_dicom_contourage().refresh_contourage()

        if self.display_settings["sources"] == 1:
            self.slice.refresh_sources()

        if self.display_settings["domaine"] == 1:
            self.slice.refresh_domaine()
            
        self.get_dicom_view().refresh_window()
        self.get_dicom_info().refresh_info()


    def get_dicom_contourage(self):
        return self.parent.dicom_left_window.dicom_contourage


    def get_dicom_info(self):
        return self.parent.dicom_right_window.top_info


    def get_dicom_view(self):
        return self.parent.dicom_right_window.dicom_view


    def set_working_directory(self, working_directory):
        self.working_directory = working_directory

        # Updating working directory into each slices
        for slice in self.dicom_parser.slices:
            slice.set_working_directory(working_directory)
        

class Menu(tk.Menu):
    def __init__(self, parent, dicom_navigation):
        tk.Menu.__init__(self, parent)
        self.parent = parent
        self.dicom_navigation = dicom_navigation
        self.initialize()

    def initialize(self):
        # Create a file menu and add it to the menubar
        file_menu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Choisir repertoire DICOM", command=self.OnSelectDirectory)
        file_menu.add_command(label="Quit")#, command=self.on_quit)

        # Create a Edit menu and add it to the menubar
        #edit_menu = tk.Menu(self.menubar, tearoff=False)
        #self.menubar.add_cascade(label="Edit", menu=edit_menu)
        #edit_menu.add_command(label="Cut", underline=2, command=self.on_cut)
        #edit_menu.add_command(label="Copy", underline=0, command=self.on_copy)
        #edit_menu.add_command(label="Paste", underline=0, command=self.on_paste)
        
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


class Toolbar(tk.Frame):
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

            #self.dicom_navigation.parent.dicom_right_window.top_info.update()
        elif self.dicom_navigation.display_settings['miniature'] == 1:
            self.dicom_navigation.display_settings['miniature'] = 0
            self.dicom_navigation.parent.dicom_right_window.top_info.canvas_dicom.get_tk_widget().pack_forget()
            self.dicom_navigation.parent.dicom_right_window.top_info.canvas_HDV.get_tk_widget().pack_forget()
            self.dicom_navigation.parent.dicom_right_window.top_info.top_canvas.config(width=600, height=50)
        
class DicomLeftWindow(ttk.Notebook):
    def __init__(self, parent, dicom_navigation):
        # Notebook
        ttk.Notebook.__init__(self, parent, style='TNotebook')
        self.parent = parent
        self.dicom_navigation = dicom_navigation
        self.initialize() 

    def initialize(self):
        self.dicom_contourage = DicomContourage(self, self.dicom_navigation)
        self.dicom_previsualisation = DicomPrevisualisation(self, self.dicom_navigation)
        self.add(self.dicom_contourage, text="Contourage")
        self.add(self.dicom_previsualisation, text="Prévisualisation")
    

class DicomRightWindow(tk.Frame):
    def __init__(self, parent, dicom_navigation):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.dicom_navigation = dicom_navigation
        self.initialize()


    def initialize(self):        
        # Notebook (dicom window + hdv)
        self.notebook = ttk.Notebook(self, style='TNotebook')
        self.notebook.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.dicom_view = DicomView(self, self.dicom_navigation)
        self.dicom_hdv = DicomHDV(self, self.dicom_navigation)
        self.notebook.add(self.dicom_view, text="Dicom View")
        self.notebook.add(self.dicom_hdv, text="HDV")

        # Top frame info
        self.top_info = DicomInfo(self, self.dicom_navigation)
        self.top_info.pack(side=tk.TOP, fill=tk.BOTH, expand=False)


    def get_current_tab(self):
        return self.notebook.tab(self.notebook.select(), "text")


class DicomInfo(tk.Frame):
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
        self.canvas_HDV.show()
        self.canvas_HDV.get_tk_widget().configure(background='black',  highlightcolor='black',\
                                                  highlightbackground='black')
        self.canvas_HDV.get_tk_widget().config(width=600, height=270)
        self.canvas_HDV._tkcanvas.config(highlightthickness=1, relief=tk.RAISED)

        # Figure Dicom
        self.blank_canvas = True
        (fig, axes) = plt.subplots(facecolor="black")
        axes.set_axis_bgcolor("black")
        axes.set_axis_off()
        self.canvas_dicom = FigureCanvasTkAgg(fig, self.top_canvas)
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
            self.canvas_dicom.show()
            #self.canvas_dicom.get_tk_widget().pack(side=tk.TOP)#, fill=tk.BOTH, expand=True)
            self.canvas_dicom.get_tk_widget().configure(background='black',  highlightcolor='black',\
                                                        highlightbackground='black')
            self.canvas_dicom.get_tk_widget().config(width=500, height=270)
            self.canvas_dicom._tkcanvas.config(highlightthickness=1, relief=tk.RAISED)

        # Update
        self.canvas_dicom.draw()

        
class DicomView(tk.Frame):
    def __init__(self, parent, dicom_navigation):
        tk.Frame.__init__(self, parent, bg="black")
        self.parent = parent
        self.dicom_navigation = dicom_navigation
        self.bind("<Visibility>", self.OnSwitchTab)
        self.initialize()

    def initialize(self):
        # Info
        #self.dicom_path = "/home/thibault/stage_CELIA/src/tests/data_tests/prostate"
        self.seuil = 10
        
        # Drawing initial empty canvas
        self.blank_canvas = True
        (fig, axes) = plt.subplots(facecolor="black")
        axes.set_axis_bgcolor("black")
        axes.set_axis_off()
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.get_tk_widget().config(width=500, height=270)
        self.canvas._tkcanvas.config(highlightthickness=1, relief=tk.RAISED)
        #self.canvas = tk.Canvas(self, bg="black", width=600, height=600)
        self.canvas.get_tk_widget().pack(side="bottom", fill="both", expand=True)


        # Affichage des informations
        widget = self.canvas.get_tk_widget()
        
        message = "Slice :\n" + \
                  "Position :"
        self.label_NW = tk.Label(widget, text=message, bg="black", fg="white", justify=tk.LEFT)
        self.label_NW.pack(side=tk.TOP, anchor=tk.NW)

        message = "Patient position :"
        self.label_SW = tk.Label(widget, text=message, bg="black", fg="white", justify=tk.LEFT)
        self.label_SW.pack(side=tk.BOTTOM, anchor=tk.SW)
    


    def OnSwitchTab(self, event):
        if self.dicom_navigation.display_settings['miniature'] == 1:
            self.dicom_navigation.parent.dicom_right_window.top_info.canvas_dicom.get_tk_widget().pack_forget()
            self.dicom_navigation.parent.dicom_right_window.top_info.canvas_HDV.get_tk_widget().pack(side=tk.RIGHT, fill=tk.Y, expand=False)
            self.dicom_navigation.parent.dicom_right_window.dicom_hdv.canvas.draw()
            self.dicom_navigation.parent.dicom_right_window.dicom_view.canvas.draw()            


    def OnClick(self, event):
        if not(event.inaxes) or self.dicom_navigation.slice.get_dose_mode() == 0:
            return

        if (event.button == 1):
            self.OnLeftClick(event)
        elif (event.button == 3):
            self.OnRightClick(event)
        else:
            return

        # Refresh
        dicom_hdv = self.dicom_navigation.parent.dicom_right_window.dicom_hdv
        dicom_hdv.update_hdv()
        self.refresh_window()
        

    def OnLeftClick(self, event):
        self.curseur = (event.xdata, event.ydata)
        slice = self.dicom_navigation.slice
        
        closest_source = slice.get_closest_source(self.curseur, self.seuil)
        slice.add_source_displayed(self.curseur, closest_source)



    def OnRightClick(self, event):
        self.curseur = (event.xdata, event.ydata)
        slice = self.dicom_navigation.slice
        
        closest_source = slice.get_closest_source(self.curseur, self.seuil)
        slice.remove_source_displayed(closest_source)


    def OnMouseScroll(self, event):
        if (event.button == 'down'):
            self.OnScrollDown(event)
        elif (event.button == 'up'):
            self.OnScrollUp(event)
        else:
            return


    def OnScrollDown(self, event):
        new_slice_id = self.dicom_navigation.slice_id - 1

        if new_slice_id < 0:
            return
        
        self.dicom_navigation.select_current_slice(new_slice_id)
        self.dicom_navigation.refresh()

    
    def OnScrollUp(self, event):
        new_slice_id = self.dicom_navigation.slice_id + 1

        if new_slice_id >= self.dicom_navigation.dicom_parser.n_slices:
            return
        
        self.dicom_navigation.select_current_slice(new_slice_id)
        self.dicom_navigation.refresh()
        

    def refresh_window(self):
        self.dicom_navigation.slice.update_DICOM_figure(self.dicom_navigation.figure_dicom, \
                                                        self.dicom_navigation.ax, \
                                                        self.dicom_navigation.display_settings, \
                                                        vmin=self.dicom_navigation.vmin.get(), \
                                                        vmax=self.dicom_navigation.vmax.get())
        self.afficher_figure()

    
    def afficher_figure(self):
        figure = self.dicom_navigation.figure_dicom
        
        if self.blank_canvas:
            self.blank_canvas = False
            self.canvas.get_tk_widget().destroy()
            self.canvas = FigureCanvasTkAgg(figure, self)
            self.canvas.mpl_connect('button_press_event', self.OnClick)
            self.canvas.mpl_connect('scroll_event', self.OnMouseScroll)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            self.canvas.get_tk_widget().configure(background='black',  highlightcolor='black',\
                                                  highlightbackground='black')
            self.canvas.get_tk_widget().pack_propagate(False) 
            self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
            self.toolbar.update()
            self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            # Affichage des informations
            widget = self.canvas.get_tk_widget()
        
            message = "Slice : " + str(self.dicom_navigation.slice_id + 1) + "/" + \
                      str(self.dicom_navigation.dicom_parser.n_slices) + "\n" + \
                      "Position : " + str(self.dicom_navigation.slice.position) + " mm"
            self.label_NW = tk.Label(widget, text=message, bg="black", fg="white", justify=tk.LEFT)
            self.label_NW.pack(side=tk.TOP, anchor=tk.NW)

            message = "Patient position : " + str(self.dicom_navigation.slice.dicom_slice.PatientPosition)
            self.label_SW = tk.Label(widget, text=message, bg="black", fg="white", justify=tk.LEFT)
            self.label_SW.pack(side=tk.BOTTOM, anchor=tk.SW)
            

        # On affiche la figure
        self.canvas.draw()  

        # Update des informations
        message = "Slice : " + str(self.dicom_navigation.slice_id + 1) + "/" + \
                  str(self.dicom_navigation.dicom_parser.n_slices) + "\n" + \
                  "Position : " + str(self.dicom_navigation.slice.position) + " mm"
        self.label_NW.config(text=message)
        
        message = "Patient position : " + str(self.dicom_navigation.slice.dicom_slice.PatientPosition)
        self.label_SW.config(text=message)


class DicomHDV(tk.Frame):
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
        #self.objet_doses = Doses_from_matrice(self.dicom_navigation.slice.get_dose_matrix())  # RÉCUPÉRER LA MATRICE ADAPTÉE AU CONTOURAGE
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

        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
        self.canvas.draw()
        ### CODÉ EN DUR POUR L'INSTANT (on a besoin d'un dict du genre {'nom_ROI' : objet de la classe Contourage_from_matrice du fichier PONT, ...} )
        

    def OnSwitchTab(self, event):
        canvas_HDV = self.dicom_navigation.parent.dicom_right_window.top_info.canvas_HDV
        canvas_dicom = self.dicom_navigation.parent.dicom_right_window.top_info.canvas_dicom
        
        if (self.dicom_navigation.display_settings['miniature'] == 1):
            canvas_HDV.get_tk_widget().pack_forget()
            canvas_dicom.get_tk_widget().pack(side=tk.RIGHT, fill=tk.Y, expand=False)
            self.dicom_navigation.parent.dicom_right_window.dicom_hdv.canvas.draw()
            self.dicom_navigation.parent.dicom_right_window.dicom_view.canvas.draw()   

        

    def update_hdv(self):
        """À APPELER APRÈS AVOIR SAISI LE FICHIER DE DOSES OU APRÈS FAIT UN CLIC AYANT CHANGÉ LA MATRICE DE DÉPÔT DE DOSE"""

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

        # Cas ou aucune source n'est placee
        dose_matrix = self.dicom_navigation.slice.get_dose_matrix()      
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

        # Affichage de la version mise a jour
        self.canvas.draw()
        self.parent.top_info.canvas_HDV.draw()

        

    def add_hdv(self, ROI_id, type_hdv='cum'):

        """À APPELER LORSQUE L'ON COCHE UNE CHECKBOX. ON A SEULEMENT BESOIN DE DONNER LA ROI."""

        appartenance_contourage = get_appartenance_contourage(
            self.dicom_navigation.dicom_parser.n_points,
            self.dicom_navigation.dicom_parser.maillage,
            self.dicom_navigation.slice.contourages[ROI_id]['array'])
        
        contourage = Contourage_from_matrice(appartenance_contourage, ROI_id)  # On crée un objet 'Contourage_from_matrice' à partir du de la matrice booléenne

        dose_matrix = self.dicom_navigation.slice.get_dose_matrix()
        
        doses = Doses_from_matrice(dose_matrix)  # On crée un objet 'Doses_from_matrice' à partir de la matrice de doses mise à jour

        var = tk.StringVar()  #  À VENIR... VARIABLE D'ÉTAT QUI INDIQUE SI ON EST EN MODE 'VOLUME RELATF' OU 'VOLUME ABSOLU'. CODÉ EN DUR POUR LE MOMENT
        var.set('r')

        self.ddc = Doses_dans_contourage(doses, contourage)  # Triage des doses qui sont dans le contourage.
        self.dict_doses_max[ROI_id] = self.ddc.dose_max


        if not ROI_id in self.dict_graph:
            self.dict_graph[ROI_id] = {}
            self.dict_plot[ROI_id] = {}

        ###

        if self.dicom_navigation.var_etat_abs_rel.get() == 'r':  # si on est en mode 'volume relatif', le range des axes sera définit différemment
            facteur = 100.0/self.ddc.nb_voxels  # comme l'instance 'axe_volume' créée par les classes hdv_cumulatif et hdv_differentiel contient des données en NOMBRE DE VOXELS
                                                # (et non en pourcentage ou en volume réel), il faut multiplier ces données par le facteur de conversion approprié (il dépend
                                                # de si l'on est en mode 'relatf' ou 'absolu').

        if self.dicom_navigation.var_etat_abs_rel.get() == 'a':  # si on est en mode 'volume absolu'.
            facteur = self.ddc.v_voxel
            self.dict_volumes_max[str(ROI_id) + type_hdv] = self.ddc.v_voxel * self.ddc.nb_voxels
            self.y_lim = self.dict_volumes_max[max(self.dict_volumes_max, key=self.dict_volumes_max.get)]  # on récupère le max en y.

        ###

        if type_hdv == 'cum':
            hdv = HDV_cumulatif(self.ddc, 100)

        if type_hdv == 'diff':
            hdv = HDV_differentiel(self.ddc, 50)


        self.dict_graph[ROI_id][type_hdv] = hdv
        self.dict_plot[ROI_id][type_hdv], = self.fig.plot(hdv.axe_doses, facteur * hdv.axe_volume)

        ###

        self.x_lim = self.dict_doses_max[max(self.dict_doses_max, key=self.dict_doses_max.get)]  # On récupère la plus grande valeur en x

        self.fig.set_xlim([0, 1.02*self.x_lim])  # dimension de l'axe des x
        self.fig.set_ylim([0, 1.02*self.y_lim])  # dimension de l'axe des y

        # Modifier
        self.canvas.draw()
        self.parent.top_info.canvas_HDV.draw()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)


        if self.got_contraintes:  # SERA INITALISÉE À 'TRUE' LORSQUE L'ON AURA RÉCUPÉRÉ LE FICHIER DE CONTRAINTES
            self.verifier_contraintes(ROI_id)


    def remove_hdv(self, ROI_id, type_hdv='cum'):

        """À APPELER LORSQUE L'ON DÉCOCHE UNE CHECKBOX. ON A SEULEMENT BESOIN DE DONNER LA ROI."""

        var = tk.StringVar()  #  À VENIR... VARIABLE D'ÉTAT QUI INDIQUE SI ON EST EN MODE 'VOLUME RELATF' OU 'VOLUME ABSOLU'. CODÉ EN DUR POUR LE MOMENT
        var.set('r')

        if not ROI_id in self.dict_graph:  # En cas où une ROI a été cochée mais qu'elle ne se trouve pas dans la zone reduite, on ne trace pas de graph.
            return                         # Et donc, on essaie pas de retirer un HDV qui n'est pas en mémoire.

        del (self.dict_graph[ROI_id][type_hdv])
        self.dict_plot[ROI_id][type_hdv].remove()  # commande 'remove' nécessaire pour effacer le graph correspondant à la case décochée
        del (self.dict_plot[ROI_id][type_hdv])
        del (self.dict_doses_max[ROI_id])


        if self.dicom_navigation.var_etat_abs_rel.get() == 'a':
            del (self.dict_volumes_max[ROI_id])
            if len(self.dict_volumes_max) != 0:  # il faut ajuster l'axe des y en fonction du plus grand volume présent
                self.y_lim = self.dict_volumes_max[max(self.dict_volumes_max, key=self.dict_volumes_max.get)]

        if len(self.dict_doses_max) != 0: # on ajuste aussi l'axe des x en fonction de la plus grande dose présente
            self.x_lim = self.dict_doses_max[max(self.dict_doses_max, key=self.dict_doses_max.get)]


        self.fig.set_xlim([0, 1.02*self.x_lim])  # dimension de l'axe des x
        self.fig.set_ylim([0, 1.02*self.y_lim])  # dimension de l'axe des y
        self.canvas.draw()
        self.parent.top_info.canvas_HDV.draw()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)


    def mode_volume_relatif(self):  # pour passer de relatif à absolu et vice_versa.  ON A PLUS 'update_abs_rel', maintenant on a une fonction différente pour chaque mode.
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
        self.fig.set_ylim([0, 1.02*self.y_lim])

        self.canvas.draw()
        self.parent.top_info.canvas_HDV.draw()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)


    def mode_volume_absolu(self):  # MODE VOLUME ABSOLU.
        if self.dicom_navigation.slice.get_dose_mode() == 0:
            return
        
        for ROI_id in self.dict_graph:  # on retrace tous les graph présents dans 'dict_graph' (tous ceux affichés à l'écran).
            for type_hdv in self.dict_graph[ROI_id]:
                self.dict_volumes_max[str(ROI_id) + type_hdv] = self.dict_graph[ROI_id][type_hdv].v_voxel * self.dict_graph[ROI_id][type_hdv].nb_voxels
                self.dict_plot[ROI_id][type_hdv].remove()  # on retire d'abord les anciens graph tracés dans dict_plot.
                facteur = self.dict_graph[ROI_id][type_hdv].v_voxel
                self.dict_plot[ROI_id][type_hdv], = self.fig.plot(self.dict_graph[ROI_id][type_hdv].axe_doses,
                                                                  facteur * self.dict_graph[ROI_id][type_hdv].axe_volume)  # on multiplie 'axe volume' par le facteur approprié.
        self.fig.set_xlabel('Dose absorbee')
        self.fig.set_ylabel('Volume absolu (cm^3)')
        self.fig.set_ylim([0, 1.02 * self.dict_volumes_max[max(self.dict_volumes_max, key=self.dict_volumes_max.get)]])

        self.canvas.draw()
        self.parent.top_info.canvas_HDV.draw()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)


    def get_contraintes(self, fichier_contraintes):  # À ACTIVER LORSQUE LE FICHIER DE CONTRAINTES EST SAISI
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

                         

class DicomContourage(tk.Frame):
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

        tk.Label(self, text="Cum").grid(row=0, column=2)
        tk.Label(self, text="Diff").grid(row=0, column=3)

        row_id = 1
        
        for (ROI_id, contourages) in self.set_ROI.iteritems():
            self.dict_lines[ROI_id] = { 'cum': tk.IntVar(), 'diff': tk.IntVar(), 'color': "orange" }

            # Color
            self.dict_lines[ROI_id]['button'] = tk.Button(self, image=self.color_button, \
                                                          relief='flat', \
                                                          background=self.dict_lines[ROI_id]['color'], \
                                                          width=0, height=0, \
                                                          command=partial(self.OnSelectColor, ROI_id))
            self.dict_lines[ROI_id]['button'].grid(row=row_id, column=0, padx=3, pady=2)

            # Text
            self.dict_lines[ROI_id]['name'] = contourages['name']
            tk.Label(self, text=self.dict_lines[ROI_id]['name']).grid(row=row_id, column=1)

            # Checkboxes
            checkbox = tk.Checkbutton(self, variable=self.dict_lines[ROI_id]['cum'], \
                                      command=partial(self.OnUpdateContourage, ROI_id, "cum"))
                                                                                           
                                                                                        
            checkbox.grid(row=row_id, column=2)
            
            checkbox = tk.Checkbutton(self, variable=self.dict_lines[ROI_id]['diff'], \
                                      command=partial(self.OnUpdateContourage, ROI_id, "diff"))
            checkbox.grid(row=row_id, column=3)
            

            row_id += 1

        # Boutons radio
        rad_button = tk.Radiobutton(self, variable = self.dicom_navigation.var_etat_abs_rel, \
                                    value = 'r', text='Volume relatif', \
                                    command=self.dicom_navigation.parent.dicom_right_window.dicom_hdv.mode_volume_relatif)
        rad_button.grid(row=row_id, column=1)
        
        rad_button = tk.Radiobutton(self, variable = self.dicom_navigation.var_etat_abs_rel, \
                                    value = 'a', text='Volume absolu', \
                                    command=self.dicom_navigation.parent.dicom_right_window.dicom_hdv.mode_volume_absolu)
        rad_button.grid(row=row_id, column=2)
            
        # Creation du menu deroulant dans l'onglet previsualisation
        self.dicom_navigation.parent.dicom_left_window.dicom_previsualisation.create_contourage_cible_menu()

        self.create_slider(row_id)


    def OnSelectColor(self, ROI_id):
        color = tkc.askcolor(title="Couleur du contourage")[1]

        if color is None:
            return
        
        self.dict_lines[ROI_id]['color'] = color
        self.dict_lines[ROI_id]['button'].config(background=color)
        self.modifier_contourage(ROI_id, color)
        
        self.dicom_navigation.refresh()


    def OnUpdateContourage(self, ROI_id, type_hdv):
        if (self.dict_lines[ROI_id]['cum'].get() == 1 or self.dict_lines[ROI_id]['diff'].get() == 1):
            # Une checkbox cochee
            self.add_contourage(ROI_id, self.dict_lines[ROI_id]['name'], self.dict_lines[ROI_id]['color'])
        elif (self.dict_lines[ROI_id]['cum'].get() == 0 and self.dict_lines[ROI_id]['diff'].get() == 0):
            # Les deux checkbox decochees
            self.remove_contourage(ROI_id)

        # Dose mode, on met a jour l'HDV
        dicom_hdv = self.dicom_navigation.parent.dicom_right_window.dicom_hdv
        
        if self.dicom_navigation.slice.get_dose_mode() == 1:
            self.refresh_contourage()
            
            if (self.dict_lines[ROI_id]['cum'].get() == 1 or self.dict_lines[ROI_id]['diff'].get() == 1):
                dicom_hdv.add_hdv(ROI_id, type_hdv)
            elif (self.dict_lines[ROI_id]['cum'].get() == 0 or self.dict_lines[ROI_id]['diff'].get() == 0):
                dicom_hdv.remove_hdv(ROI_id, type_hdv)
        
        self.dicom_navigation.refresh()
        
                
    def add_contourage(self, ROI_id, name, color):
        if ROI_id in self.dicom_navigation.contourages:
            return

        self.dicom_navigation.contourages[ROI_id] = { 'name': name, 'color': color }


    def remove_contourage(self, ROI_id):
        if ROI_id in self.dicom_navigation.contourages:
            del self.dicom_navigation.contourages[ROI_id]


    def modifier_contourage(self, ROI_id, color):
        if ROI_id in self.dicom_navigation.contourages:
            self.dicom_navigation.contourages[ROI_id]['color'] = color


    def create_slider(self, current_row_id):
        row_id = current_row_id + 1
        
        tk.Label(self, text="Luminosité min").grid(row=row_id, column=1)
        self.slider_min = tk.Scale(self, from_=0, to=3000, \
                                   variable=self.dicom_navigation.vmin, \
                                   orient=tk.HORIZONTAL, \
                                   command=None)#lambda x: self.dicom_navigation.refresh())
        self.slider_min.grid(row=row_id, column=2)

        row_id += 1

        tk.Label(self, text="Luminosité max").grid(row=row_id, column=1)
        self.slider_max = tk.Scale(self, from_=0, to=3000, \
                                   variable=self.dicom_navigation.vmax, \
                                   orient=tk.HORIZONTAL,
                                   command=None)#lambda x: self.dicom_navigation.refresh())
        self.slider_max.grid(row=row_id, column=2)

        


    def refresh_contourage(self):
        self.dicom_navigation.slice.set_contourages(self.dicom_navigation.contourages)


class DicomPrevisualisation(tk.Frame):
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
        e.grid(row=2, column=1)

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
        tk.Label(self, text="Granularité source").grid(row=5, column=0, stick=tk.W)
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

        # Contourage cible
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

        # Bouton pour lancer la previsualisation
        filename = self.dicom_navigation.PATH_ressources + "cog.gif"
        img = Image.open(filename)
        self.button_previsualisation = ImageTk.PhotoImage(img)
        open_button = tk.Button(self, text="Lancer la previsualisation", image=self.button_previsualisation, \
                                relief=tk.RAISED, compound="right", command=self.OnLancerPrevisualisation)
        open_button.grid(row=12, padx=2, pady=2, sticky=tk.W)

        # Bouton pour lancer les calculs finaux
        filename = self.dicom_navigation.PATH_ressources + "cog.gif"
        img = Image.open(filename)
        self.button_calculs = ImageTk.PhotoImage(img)
        open_button = tk.Button(self, text="Lancer calculs finaux", image=self.button_calculs, \
                                relief=tk.RAISED, compound="right", command=None)
        open_button.grid(row=13, padx=2, pady=2, sticky=tk.W)


    def OnSelectWorkingDirectory(self):
        working_directory = tkFileDialog.askdirectory(initialdir="~/tmp/")
        
        if (working_directory == ""):
            return
    
        self.dicom_navigation.set_working_directory(working_directory)


    def OnUpdateAfficherSources(self):
        if self.checkbox_display_sources.get() == 1:
            self.grey_checkbox.config(state=tk.NORMAL)
        else:
            self.checkbox_display_area.set(0)
            self.grey_checkbox.config(state=tk.DISABLED)

        self.dicom_navigation.dicom_parser.set_granularite_source(self.granularite_source.get())
        self.dicom_navigation.display_settings["sources"] = self.checkbox_display_sources.get()
        self.dicom_navigation.refresh()


    def OnUpdateAfficherZoneInfluence(self):
        self.dicom_navigation.dicom_parser.set_zone_influence(self.zone_influence.get())
        self.dicom_navigation.display_settings["domaine"] = self.checkbox_display_area.get()
        self.dicom_navigation.refresh()


    def OnLancerPrevisualisation(self):
        slice = self.dicom_navigation.slice
        dicom_hdv = self.dicom_navigation.parent.dicom_right_window.dicom_hdv

        self.dicom_navigation.dicom_parser.set_granularite_source(self.granularite_source.get())
        self.dicom_navigation.dicom_parser.set_zone_influence(self.zone_influence.get())
        slice.preparatifs_precalculs()
        
        if slice.dose_already_calculated():
            slice.set_dose_mode_ON()
            return

        self.lancer_calculs_previsualisation()


    def OnUpdateContourageCible(self, ROIname):
        # On enleve le precedant contourage cible s'il etait present
        if self.contourage_cible_id != None:
            self.dicom_navigation.parent.dicom_left_window.dicom_contourage.remove_contourage(self.contourage_cible_id)
        
        # Puis on le met a jour
        self.contourage_cible_id = self.ROIname_to_ROIid(ROIname)
        self.dicom_navigation.dicom_parser.set_contourage_cible_id(self.contourage_cible_id)
        self.dicom_navigation.parent.dicom_left_window.dicom_contourage.add_contourage(self.contourage_cible_id, ROIname, "orange")
        self.dicom_navigation.refresh()


    def create_contourage_cible_menu(self):
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


    def lancer_calculs_previsualisation(self):
        slice = self.dicom_navigation.slice
        
        # Generation des fichiers de configuration .don
        options = { 'rayon': (self.rayon_x, self.rayon_y, 1),
                    'direction_M1': (0., 0., 0.), # Curietherapie
                    'spectre_mono': (self.intensite, self.energie) }
        
        self.dicom_navigation.dicom_parser.generate_DICOM_previsualisation(slice.get_slice_id(),
                                                                           self.dicom_navigation.working_directory,
                                                                           options)

        # Lancement du calcul M1
        os.chdir(self.dicom_navigation.slice.get_slice_directory())
        call([self.dicom_navigation.PATH_lance_KIDS, "config_KIDS.don"])
        os.chdir(self.dicom_navigation.PATH_initial)
        
        

class OldMainWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.x = 0
        self.y = 0
        
        # Configuration du canevas
        self.canvas = tk.Canvas(self, width=600, height=600, cursor="cross")
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.x = event.x
        self.y = event.y

    def on_button_release(self, event):
        (x0, y0) = (self.x, self.y)
        (x1, y1) = (event.x, event.y)
        
        self.canvas.create_rectangle(x0, y0, x1, y1, fill="white")

if __name__ == "__main__":
    app = MainApplication(None)
    app.title("Dicomparser")
    app.mainloop()
