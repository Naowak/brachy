import Tkinter as tk
import tkFileDialog

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from dicom_parser import *
from slice import *


# Monkey Patching
def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)

tk.Canvas.create_circle = _create_circle


class MainApplication(tk.Tk):
    def __init__(self, parent):
        tk.Tk.__init__(self)
        self.parent = parent
        self.dicom_path = None
        self.initialize()

    def initialize(self):
        self.toolbar = Toolbar(self)
        self.configure(menu=self.toolbar)
        self.dicomwindow = DicomWindow(self)
        self.dicomwindow.pack(side="right", fill="both", expand=True)


class Toolbar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        # Create a file menu and add it to the menubar
        file_menu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Choisir repertoire DICOM", command=self.OnSelectDirectory)
        file_menu.add_command(label="Choisir fichier RT (structure)", command=self.OnSelectRT)
        file_menu.add_command(label="Choisir slice", command=self.OnSelectSlice)
        file_menu.add_command(label="Quit")#, command=self.on_quit)

        # Create a Edit menu and add it to the menubar
        #edit_menu = tk.Menu(self.menubar, tearoff=False)
        #self.menubar.add_cascade(label="Edit", menu=edit_menu)
        #edit_menu.add_command(label="Cut", underline=2, command=self.on_cut)
        #edit_menu.add_command(label="Copy", underline=0, command=self.on_copy)
        #edit_menu.add_command(label="Paste", underline=0, command=self.on_paste)
        
    def OnSelectDirectory(self):
        return 1
        #self.parent.dicomwindow.dicom_path = tkFileDialog.askdirectory()
        #self.OnDicomSelect()

    def OnSelectRT(self):
        return 1


    def OnSelectSlice(self):
        return 1
        


class DicomWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.canvas = None
        self.initialize()


    def initialize(self):
        # Info
        self.dicom_path = "/home/thibault/stage_CELIA/src/tests/data_tests/prostate"
        self.filename_head = "/home/thibault/stage_CELIA/src/tests/data_tests/resultats_prostate/prostate"
        self.RT_structure_id = 158
        self.slice_id = 149
        self.seuil = 10
        self.OnStartParsing()
        
        #self.curseur = (0, 0)
        # Configuration du canevas
        #self.canvas = tk.Canvas(self, width=600, height=600, cursor="cross")


    def OnStartParsing(self):
        # Loading
        self.dicomparser = DicomParser(self.dicom_path, self.RT_structure_id)
        self.slice = Slice(self, self.slice_id)
        self.slice.set_contourage(5)
        (figure, ax) = self.dicomparser.get_DICOM_figure()
        self.figure = figure
        self.ax = ax
        self.refresh_window()


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
        #self.canvas.create_circle(self.curseur[0], self.curseur[1], 5, fill="red")
        self.curseur = (event.xdata, event.ydata)
        closest_source = self.slice.get_closest_source(self.curseur, self.seuil)
        self.slice.add_source_displayed(self.curseur, closest_source)
        self.refresh_window()


    def OnRightClick(self, event):
        self.curseur = (event.xdata, event.ydata)
        closest_source = self.slice.get_closest_source(self.curseur, self.seuil)
        self.slice.remove_source_displayed(closest_source)
        self.refresh_window()


    def refresh_window(self):
        self.slice.update_dose_matrix()
        self.slice.update_DICOM_figure()
        self.afficher_figure()


    def afficher_figure(self):        
        if self.canvas is None:
            self.canvas = FigureCanvasTkAgg(self.figure, self)
            self.canvas.mpl_connect('button_press_event', self.OnClick)
            self.canvas.mpl_connect('button_press_event', self.OnClick)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
            self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
            self.toolbar.update()
            self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.figure.canvas.draw()


    def backup(self):
        print self.slice.sources_displayed
        
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.mpl_connect('button_press_event', self.OnClick)
        self.canvas.mpl_connect('button_press_event', self.OnClick)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)



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
