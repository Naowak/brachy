# -*- coding: utf-8 -*-
import sys
sys.path.append("../resources/")
sys.path.append("../code_cyrille/")

import Tkinter as tk
import tkFileDialog
import ttk
import tkColorChooser as tkc

from functools import partial
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import Figure, FigureCanvasTkAgg, NavigationToolbar2TkAgg
from dicom_parser import *
from slice import *
from PONT import *


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
        self.menu = Menu(self)
        self.configure(menu=self.menu)
        self.toolbar = Toolbar(self)
        self.dicom_navigation = DicomNavigation(self)
        self.dicom_right_window = DicomRightWindow(self)
        self.dicom_left_window = DicomLeftWindow(self)

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
        self.dose_mode = False
        self.checkbox_state = -1

        # Current_slice
        self.slice_id = None
        self.slice = None

        # Contourages
        self.contourages = {}

        # Note Style
        self.note_style = ttk.Style()
        self.note_style.configure("TNotebook", borderwidth=1)
        self.note_style.configure("TNotebook.Tab", borderwidth=1)
        self.note_style.configure("TFrame", background="white", foreground="black", borderwidth=0)


    def start_parsing(self):
        # Loading
        self.dicom_parser = DicomParser(self.dicom_path)
        self.select_current_slice(90)
        (self.figure, self.ax) = self.dicom_parser.get_DICOM_figure()
        self.parent.dicom_left_window.frame1.load_contourage()
        self.refresh()


    def select_current_slice(self, slice_id):
        self.slice_id = slice_id
        self.slice = self.dicom_parser.get_slice(slice_id)
        self.dose_mode = False
        self.slice.set_contourages(self.contourages)
        

    def refresh(self):
        self.parent.dicom_left_window.frame1.refresh_contourage()
        self.parent.dicom_right_window.frame1.refresh_window()
        


class Menu(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)
        self.parent = parent
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
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bd=1, relief=tk.RAISED)
        self.parent = parent
        self.initialize()

    def initialize(self):
        # Button open
        img = Image.open("../resources/folder_user.png")
        self.button_folder_user = ImageTk.PhotoImage(img)
        open_button = tk.Button(self, text="Ouvrir patient", image=self.button_folder_user, \
                                relief=tk.FLAT, compound="top", command=self.parent.menu.OnSelectDirectory)
        #open_button = tk.Button(self, text="Toto", relief=tk.FLAT)
        open_button.pack(side="left", padx=2, pady=2)
        
        
class DicomLeftWindow(ttk.Notebook):
    def __init__(self, parent):
        # Notebook
        ttk.Notebook.__init__(self, parent, style='TNotebook')
        self.parent = parent
        self.initialize() 

    def initialize(self):
        self.frame1 = DicomContourage(self)
        self.frame2 = DicomPrevisualisation(self)
        self.add(self.frame1, text="Contourage")
        self.add(self.frame2, text="Prévisualisation")
    

class DicomRightWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bg="black")
        self.parent = parent
        self.initialize()


    def initialize(self):
        # Drawing top canvas
        self.top_canvas = tk.Canvas(self, width=600, height=40, borderwidth=1, relief=tk.RAISED)#, highlightbackground="black")
        self.top_canvas.pack(side="top", fill="both", expand=False)

        # Notebook (dicom window + dvh)
        self.notebook = ttk.Notebook(self, style='TNotebook')
        self.notebook.pack(side="left", fill="both", expand=True)
        self.frame1 = DicomView(self)
        self.frame2 = DicomDVH(self)
        self.notebook.add(self.frame1, text="Dicom View")
        self.notebook.add(self.frame2, text="DVH")


class DicomView(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bg="black")
        self.parent = parent
        self.dicom_navigation = self.parent.parent.dicom_navigation
        self.initialize()

    def initialize(self):
        # Info
        #self.dicom_path = "/home/thibault/stage_CELIA/src/tests/data_tests/prostate"
        self.seuil = 10
        
        # Drawing initial empty canvas
        self.blank_canvas = True
        self.canvas = tk.Canvas(self, bg="black", width=600, height=600)
        self.canvas.pack(side="bottom", fill="both", expand=True)
        self.label_NW = None
        self.label_SW = None


    def OnClick(self, event):
        if not event.inaxes:
            return

        if (event.button == 1):
            self.OnLeftClick(event)
        elif (event.button == 3):
            self.OnRightClick(event)
        else:
            return
        

    def OnLeftClick(self, event):
        if not(self.dicom_navigation.dose_mode):
            return
        
        self.curseur = (event.xdata, event.ydata)
        slice = self.dicom_navigation.slice
        
        closest_source = slice.get_closest_source(self.curseur, self.seuil)
        slice.add_source_displayed(self.curseur, closest_source)
        self.refresh_window()


    def OnRightClick(self, event):
        if not(self.dicom_navigation.dose_mode):
            return
        
        self.curseur = (event.xdata, event.ydata)
        slice = self.dicom_navigation.slice
        
        closest_source = slice.get_closest_source(self.curseur, self.seuil)
        slice.remove_source_displayed(closest_source)
        self.refresh_window()


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
        self.refresh_window()

    
    def OnScrollUp(self, event):
        new_slice_id = self.dicom_navigation.slice_id + 1

        if new_slice_id >= self.dicom_navigation.dicom_parser.n_slices:
            return
        
        self.dicom_navigation.select_current_slice(new_slice_id)
        self.refresh_window()
        

    def refresh_window(self):
        #self.slice.update_dose_matrix()
        self.dicom_navigation.slice.update_DICOM_figure(self.dicom_navigation.figure, \
                                                       self.dicom_navigation.ax)
        self.afficher_figure()
    

    def afficher_figure(self):
        figure = self.dicom_navigation.figure
        
        if self.blank_canvas:
            self.blank_canvas = False
            self.canvas.destroy()
            self.canvas = FigureCanvasTkAgg(figure, self)
            self.canvas.mpl_connect('button_press_event', self.OnClick)
            self.canvas.mpl_connect('scroll_event', self.OnMouseScroll)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            self.canvas.get_tk_widget().configure(background='black',  highlightcolor='black', highlightbackground='black')
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
        figure.canvas.draw()  

        # Update des informations
        message = "Slice : " + str(self.dicom_navigation.slice_id + 1) + "/" + \
                  str(self.dicom_navigation.dicom_parser.n_slices) + "\n" + \
                  "Position : " + str(self.dicom_navigation.slice.position) + " mm"
        self.label_NW.config(text=message)
        
        message = "Patient position : " + str(self.dicom_navigation.slice.dicom_slice.PatientPosition)
        self.label_SW.config(text=message)


class DicomDVH(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bg="black")
        self.parent = parent
        self.dicom_navigation = self.parent.parent.dicom_navigation
        #self.initialize()

    def initialize(self):
        label = tk.Label(self, text="Histogramme dose/volume", font=("Verdana", 14))
        label.grid(row=0, column=0, columnspan=7)

        self.ddc = None

        self.dict_graph = {}
        self.dict_plot = {}
        self.dict_doses_max = {}
        self.dict_volumes_max = {}


        fig = Figure(figsize=(7,6), dpi=100)


        self.canvas = FigureCanvasTkAgg(fig, self)

        self.objet_doses = Doses_from_matrice(self.dicom_navigation.slice.get_dose_matrix())

        self.fig = fig.add_subplot(111)
        self.fig.plot([],[]) # Initialisation d'un plot vide
        self.fig.grid(True)
        self.x_lim = 100
        self.y_lim = 100
        self.fig.set_xlim([-0.01*self.x_lim, 1.02*self.x_lim])
        self.fig.set_ylim([0, 1.02*self.y_lim])
        self.canvas.draw()  # Action similaire à plt.show() avec matplotlib. C'est ce qui permet d'afficher le canvas à l'écran tel qu'il a été créé ou modifié.
        self.canvas.get_tk_widget().grid(row=1, column=self.col_graph, rowspan=8, columnspan=6)

        toolbar_frame = Frame(self)  # La barre d'outil au bas du graphique.
        toolbar_frame.grid(row=9,column=self.col_graph)
        NavigationToolbar2TkAgg(self.canvas, toolbar_frame)

                         

class DicomContourage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.dicom_navigation = self.parent.parent.dicom_navigation
        self.initialize()


    def initialize(self):
        self.dict_lines = {}


    def load_contourage(self):
        self.set_ROI = self.dicom_navigation.dicom_parser.get_set_ROI()

        # Loading res
        img = Image.open("../resources/color_button.gif")
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
                                      command=partial(self.OnUpdateContourage, ROI_id))
                                                                                           
                                                                                        
            checkbox.grid(row=row_id, column=2)
            
            checkbox = tk.Checkbutton(self, variable=self.dict_lines[ROI_id]['diff'], \
                                      command=partial(self.OnUpdateContourage, ROI_id))
            checkbox.grid(row=row_id, column=3)
            

            row_id += 1


    def OnSelectColor(self, ROI_id):
        color = tkc.askcolor(title="Couleur du contourage")[1]

        if color is None:
            return
        
        self.dict_lines[ROI_id]['color'] = color
        self.dict_lines[ROI_id]['button'].config(background=color)
        self.modifier_contourage(ROI_id, color)
        
        self.dicom_navigation.refresh()


    def OnUpdateContourage(self, ROI_id):
        if (self.dict_lines[ROI_id]['cum'].get() == 1 or self.dict_lines[ROI_id]['diff'].get() == 1):
            self.add_contourage(ROI_id, \
                                self.dict_lines[ROI_id]['name'], \
                                self.dict_lines[ROI_id]['color'])
        elif (self.dict_lines[ROI_id]['cum'].get() == 0 and self.dict_lines[ROI_id]['diff'].get() == 0):
            self.remove_contourage(ROI_id)
        else:
            return

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


    def refresh_contourage(self):
        self.dicom_navigation.slice.set_contourages(self.dicom_navigation.contourages)


class DicomPrevisualisation(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.dicom_navigation = self.parent.parent.dicom_navigation
        self.initialize()

    def initialize(self):
        # Repertoire de travail
        tk.Label(self, text="Répertoire de travail").grid(row=0, column=0, sticky=tk.W)
        
        img = Image.open("../resources/table_multiple.png")
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
        self.rayon = tk.DoubleVar(value=0.6)
        tk.Label(self, text="Rayon").grid(row=2, column=0, stick=tk.W)
        e = tk.Entry(self, justify=tk.RIGHT, textvariable=self.rayon, width=7)
        e.grid(row=2, column=1, sticky=tk.E)

        # Choix energie
        self.energie = tk.DoubleVar(value=1E20)
        tk.Label(self, text="Energie").grid(row=3, column=0, stick=tk.W)
        e = tk.Entry(self, justify=tk.RIGHT, textvariable=self.energie, width=7)
        e.grid(row=3, column=1, sticky=tk.E)

        # Granularité source
        self.granularite = tk.IntVar(value=5)
        tk.Label(self, text="Granularité source").grid(row=4, column=0, stick=tk.W)
        e = tk.Entry(self, justify=tk.RIGHT, textvariable=self.granularite, width=7)
        e.grid(row=4, column=1, sticky=tk.E)

        # Zone d'influence (mm)
        self.zone_influence = tk.DoubleVar(value=50)
        tk.Label(self, text="Zone d'influence (mm)").grid(row=5, column=0, stick=tk.W)
        e = tk.Entry(self, justify=tk.RIGHT, textvariable=self.zone_influence, width=7)
        e.grid(row=5, column=1, sticky=tk.E)

        # Contourage cible
        tk.Label(self, text="Contourage cible").grid(row=6, column=0, sticky=tk.W)
                 
        liste_options = ('M1', 'M2')
        self.contourage_cible = tk.StringVar(value=liste_options[0])
        om = tk.OptionMenu(self, self.contourage_cible, *liste_options)
        om.grid(row=6, column=1, sticky=tk.E)

        # Bouton pour lancer la previsualisation
        img = Image.open("../resources/cog.gif")
        self.button_previsualisation = ImageTk.PhotoImage(img)
        open_button = tk.Button(self, text="Lancer la previsualisation", image=self.button_previsualisation, \
                                relief=tk.RAISED, compound="right", command=None)
        open_button.grid(row=7, padx=2, pady=2)


    def OnSelectWorkingDirectory(self):
        str = tkFileDialog.askdirectory()
        
        if (str == ""):
            return
    
        self.working_directory = str


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
