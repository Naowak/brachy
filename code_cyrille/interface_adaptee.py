# -*- coding: utf-8 -*-
import sys
sys.path.append("../src")


from matplotlib import use
use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure


from functools import partial  # Servira lors de la création des checkboxes. Permet de créer une commande à partir d'une fonction prenant des arguments

from Tkinter import *

from classes_primaires import *
from PONT import *

LARGE_FONT= ("Verdana", 14)



###



class Graph(Frame):

    ''' Contiendra le HDV dans l'interface graphique. Contient également toutes les méthodes nécessaires pour le mettre à jour.

    Arguments :

    - parent : la fenêtre parent Tk dans laquelle sera contenu le HDV.

    Attributs :

    - col_graph : paramètre correspondant à la colonne dans laquelle sera placé le HDV avec la méthode 'grid'.
    - ddc : Objet initialement de type None. Sera initialisé plus tard pour être un objet 'doses_dans_contourage' de la dernière courbe tracée dans le HDV.
    - dict_graph : dictionnaire ayant pour clé le nom d'une ROI + _cum ou _diff et dont la valeur correspond à un objet 'hdv_cumulatif' ou 'hdv_differentiel'.
                    on les garde en mémoire dans le cas où l'on veuille changer du mode 'volume relatif' à 'volume absolu'.
    - dict_plot : dictionnaire dans lequel on placera chacune des commandes 'plot' avec pour clé le nom de la ROI + _cum ou _diff.
                    On les place dans un dictionnaire pour pouvoir leur donner une adresse mémoire connue et ainsi les supprimer plus tard si nécessaire.
    - dict_doses_max : dictionnaire ayant pour clé le nom d'une ROI + _cum ou _diff et dont la valeur correspond à la dose maximale reçue pour cette ROI.
                        Sera utile pour redimentionner l'axe des x du HDV de manière interactive.
    - dict_volumes_max : dictionnaire ayant pour clé le nom d'une ROI + _cum ou _diff et dont la valeur correspond au nombre de pixels présents dans le
                        contourage correspondant à cette ROI. Sera utile pour redimentionner l'axe des y du HDV de manière interactive en mode volume absolu
    - canvas : canvas dans lequel on trace la HDV.
    - objet_doses : objet 'Doses_from_matrice' contenant une matrice test (VA CHANGER AVEC CODE THIBAULT, ON VEUT RÉCUPÉRER LES DOSES DIRECTEMENT DE SON
                            CODE ET NON D'UN FICHIER)
    - fig : commade qui ajouter un plot dans le canvas
    - x_lim, y_lim : Points de repère pour donner les bonnes dimensions aux axes x et y. Sera utile pour redimentionner le HDV de manière interactive.


    Instances :

    - update_hdv : permet de mettre à jour le HDV d'après les checkboxes cochées. Prend en argument le nom de la ROI et le type de HDV voulu.
    - update_abs_rel : permet de passer d'un HDV en volume relatif à absolu et vice-versa.'''

    def __init__(self, parent):
        self.col_graph = 15
        Frame.__init__(self, parent)
        label = Label(self, text="Histogramme dose/volume", font=("Verdana", 14))
        label.grid(row=0, column=self.col_graph, columnspan=7)


        self.ddc = None

        self.dict_graph = {}
        self.dict_plot = {}
        self.dict_doses_max = {}
        self.dict_volumes_max = {}


        fig = Figure(figsize=(7,6), dpi=100)


        self.canvas = FigureCanvasTkAgg(fig, self)


        self.objet_doses = Doses_from_matrice(loadtxt('dose_test.txt'))


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



    def update_hdv(self, name_ROI, type_hdv='_cum'):

        contourage = controls.classe_groupe_contourages.dict_classes_contourages[name_ROI]  # on récupère le contourage associé à la ROI donnée en argument
        #contourage.afficher()
        var = controls.var.get()  # variable de type 'string' associée au boutons radios qui servent à choisir entre volume relatif et absolu.
                                    # elle a la valeur 'r' en mode volume relatif et 'a' en volume absolu.


        self.ddc = doses_dans_contourage(self.objet_doses, contourage)
        self.dict_doses_max[name_ROI + type_hdv] = self.ddc.dose_max


        if var == 'r':  # si on est en mode volume relatif
            facteur = 100.0/self.ddc.nb_voxels  # comme l'instance 'axe_volume' créé par les classes hdv_cumulatif et hdv_differentiel contient des données en nombre de voxels,
                                                # (et non en pourcentage ou en volume réel) il faut multiplier ces données par le facteur de conversion approprié (il dépend
                                                # du type de HDV).

            if type_hdv == '_cum':
                if controls.dict_checkboxes[name_ROI][0].get() == 1: # à exécuter si une checkbox vient d'être cochée.
                    hdv_cum = hdv_cumulatif(self.ddc, 100)
                    self.dict_graph[name_ROI + '_cum'] = hdv_cum
                    self.dict_plot[name_ROI + '_cum'], = self.fig.plot(hdv_cum.axe_doses, facteur * hdv_cum.axe_volume)  # c'est ici qu'on multiplie l'axe des volume
                                                                                                                        # par le facteur approprié.
                else:  # à exécuter si on décoche une checkbox. quand ça arrive, on suprime ce qui a été gardé en mémoire (lignes ci-dessous).
                    del (self.dict_graph[name_ROI + '_cum'])
                    self.dict_plot[name_ROI + '_cum'].remove()  # commande 'remove' nécessaire pour effacer le graph correspondant à la case décochée
                    del (self.dict_plot[name_ROI + '_cum'])
                    del (self.dict_doses_max[name_ROI + '_cum'])
            if type_hdv == '_diff':
                if controls.dict_checkboxes[name_ROI][2].get() == 1:
                    hdv_diff = hdv_differentiel(self.ddc, 50)
                    self.dict_graph[name_ROI + '_diff'] = hdv_diff
                    print hdv_diff.axe_doses
                    print hdv_diff.axe_volume
                    self.dict_plot[name_ROI + '_diff'], = self.fig.plot(hdv_diff.axe_doses, facteur*hdv_diff.axe_volume)
                else:
                    del (self.dict_graph[name_ROI + '_diff'])
                    self.dict_plot[name_ROI + '_diff'].remove()
                    del (self.dict_plot[name_ROI + '_diff'])
                    del (self.dict_doses_max[name_ROI + '_diff'])

            self.y_lim = 100  # en volume relatif, le maximum en y est 100%


        if var == 'a':  # si on est en mode 'volume absolu'.
            facteur = self.ddc.v_voxel
            self.dict_volumes_max[name_ROI + type_hdv] = self.ddc.v_voxel*self.ddc.nb_voxels

            if type_hdv == '_cum':
                if controls.dict_checkboxes[name_ROI][0].get() == 1:
                    hdv_cum = hdv_cumulatif(self.ddc, 100)
                    self.dict_graph[name_ROI + '_cum'] = hdv_cum
                    self.dict_plot[name_ROI + '_cum'], = self.fig.plot(hdv_cum.axe_doses, facteur * hdv_cum.axe_volume)
                else:
                    del (self.dict_graph[name_ROI + '_cum'])
                    self.dict_plot[name_ROI + '_cum'].remove()
                    del (self.dict_plot[name_ROI + '_cum'])
                    del (self.dict_doses_max[name_ROI + '_cum'])
                    del (self.dict_volumes_max[name_ROI + '_cum'])

            if type_hdv == '_diff':
                if controls.dict_checkboxes[name_ROI][2].get() == 1:
                    hdv_diff = hdv_differentiel(self.ddc, 50)
                    self.dict_graph[name_ROI + '_diff'] = hdv_diff
                    self.dict_plot[name_ROI + '_diff'], = self.fig.plot(hdv_diff.axe_doses, facteur*hdv_diff.axe_volume)
                else:
                    del (self.dict_graph[name_ROI + '_diff'])
                    self.dict_plot[name_ROI + '_diff'].remove()
                    del (self.dict_plot[name_ROI + '_diff'])
                    del (self.dict_doses_max[name_ROI + '_diff'])
                    del (self.dict_volumes_max[name_ROI + '_diff'])

            if len(self.dict_volumes_max) != 0:  # il faut ajuster l'axe des y en fonction du plus grand volume présent
                self.y_lim = self.dict_volumes_max[max(self.dict_volumes_max, key=self.dict_volumes_max.get)]


        if len(self.dict_doses_max) != 0: # on ajuste aussi l'axe des x en fonction de la plus grande dose présente
            self.x_lim = self.dict_doses_max[max(self.dict_doses_max, key=self.dict_doses_max.get)]


        self.fig.set_xlim([-0.01*self.x_lim, 1.02*self.x_lim])  # dimension de l'axe des x
        self.fig.set_ylim([0, 1.02*self.y_lim])  # dimension de l'axe des y
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=self.col_graph, rowspan=8, columnspan=6)


    def update_abs_rel(self):  # pour passer de relatif à absolu et vice_versa.
        self.dict_volumes_max = {}
        for nom in self.dict_graph:  # on retrace tous les graph présents dans 'dict_graph' (tous ceux affichés à l'écran).
            self.dict_plot[nom].remove()  # on retire d'abord les anciens graph tracés.

            if controls.var.get() == 'r':
                facteur = 100.0/self.dict_graph[nom].nb_voxels
                self.dict_plot[nom], = self.fig.plot(self.dict_graph[nom].axe_doses, facteur*self.dict_graph[nom].axe_volume)  # on multiplie 'axe volume'
                                                                                                                                # par le facteur approprié.
                self.fig.set_ylim([0, 102])
            if controls.var.get() == 'a':
                self.dict_volumes_max[nom] = self.dict_graph[nom].v_voxel*self.dict_graph[nom].nb_voxels

                facteur = self.dict_graph[nom].v_voxel
                self.dict_plot[nom], = self.fig.plot(self.dict_graph[nom].axe_doses, facteur*self.dict_graph[nom].axe_volume)  # on multiplie 'axe volume'
                                                                                                                                # par le facteur approprié.
                nom_volume_max = max(self.dict_volumes_max, key=self.dict_volumes_max.get)
                self.fig.set_ylim([0, 1.02*self.dict_volumes_max[nom_volume_max]])

            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=1, column=self.col_graph, rowspan=8, columnspan=6)



class Ex(Frame):  # Graphique fictif à titre d'exemple (C'EST LÀ QUE VA L'INTERFACE DE THIBAULT).

    def __init__(self, parent):
        col_graph = 15
        Frame.__init__(self, parent)
        label = Label(self, text="Interface Thibault", font=("Verdana", 14))
        label.grid(row=0, column=col_graph, columnspan=7)


        self.liste_classes_doses_dans_contourages = []
        self.dict_graph = {}


        fig = Figure(figsize=(7,6), dpi=100)
        #gs = gridspec.GridSpec(2, 2, width_ratios=[1, 2])


        canvas = FigureCanvasTkAgg(fig, self)
        canvas.show()
        canvas.get_tk_widget().grid(row=1, column=col_graph, rowspan=8, columnspan=6)


        b = fig.add_subplot(111)
        b.plot([8, 2, 3, 4, 5, 6, 7, 1], [1, 6, 1, 3, 8, 9, 3, 10])
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=col_graph, rowspan=8, columnspan=6)


        toolbar_frame = Frame(self)
        toolbar_frame.grid(row=9,column=col_graph)
        NavigationToolbar2TkAgg(canvas, toolbar_frame)





class Menu(Frame):

    ''' Contiendra le menu permettant de controler le HDV de manière interactive.

    Arguments :

    - parent : la fenêtre parent Tk dans laquelle sera contenu le menu.

    Attributs :

    - col_graph : paramètre correspondant à la colonne dans laquelle sera placé le HDV avec la méthode 'grid'.
    - var : variable de type 'string' liée au boutons radios pour le choix du mode volume relatif ou absolu. prend la valeur 'r'
            pour le mode 'volume relatif' et 'a' pour le mode 'volume absolu'.
    - classe_DICOM : objet DicomParser obtenu avec les arguments nécessaires (codé en dur pour l'instant).
    - dicom_path : répertoire dans lequel sont les fichiers DICOM
    - RT_id : id du fichier RT
    - slice_id : id de la slice qui nous intéresse
    - classe_groupe_contourages : objet Groupe_contourages contenant un dictionnaire d'objets Contourage_from_DP de toutes les ROI présentes dans la slice.
    - dict_labels_ROI : dictionnaire dont la clé est le nom d'une ROI et dont la valeur est un objet Label
                        (servira à constituer la liste des ROIs apparaissant à l'écran).
    - dict_checkboxes : dictionnaire ayant pour clé le nom d'une ROI et comme valeur une liste contenant des informations sur les checkboxes.
                        ex : {'nom_ROI' : [objet 'IntVar' associé à la prochaine checkbox, objet Checkbutton, objet IntVar, objet Checkbutton,
                        numéro de ligne (pour la fonction grid), ROI_id], 'nom_ROI2' : ...}
                        PAS IDÉAL COMME STRUCTURE MAIS ÇA MARCHE TRÈS BIEN. À CHANGER PEUT-ÊTRE.
    - liste_boutons_radios : liste dans laquelle on place les boutons radios nécessaires au choix du mode 'volume relatif' ou 'volume absolu'.
    - row_bouton : paramètre pour ajuster la position des checkboxes


    Instances :

    - creer_checkboxes : lance la création des checkboxes et les affiche à l'écran
    '''

    def __init__(self, parent, classe_hdv=None):
        self.col_graph = graph2.col_graph
        Frame.__init__(self, parent)
        label = Label(self, text="Entrée des données\n", font=("Verdana", 14))
        label.grid(row=0, column=9, columnspan=6)



        ###

        self.var = StringVar()
        self.var.set('r')

        ###

        self.classe_DICOM = None
        self.dicom_path = None
        self.RT_id = None
        self.slice_id = None

        #self.classe_doses = None
        self.classe_groupe_contourages = None

        ###

        self.dict_labels_ROI = {}
        #self.dict_classes_contourages = {}
        self.dict_checkboxes = {}

        self.liste_boutons_radios = []
        #self.liste_boutons = []

        ###

        self.row_bouton = 0

        self.creer_checkboxes()



    def creer_checkboxes(self):

        self.dicom_path="/home/thibault/stage_CELIA/src/tests/data_tests/prostate"
        self.RT_id = 158
        self.slice_id = 89

        #debut

        self.classe_DICOM = DICOM_from_path(self.dicom_path, self.RT_id)

        #0.264

        self.classe_groupe_contourages = Groupe_contourages(self.classe_DICOM, self.slice_id)
        #10.085
        dict_ROI = self.classe_groupe_contourages.dict_ROI
        row_noms_ROI = 2

        # 10.085

        for ROI in dict_ROI:
            nom = dict_ROI[ROI]
            self.dict_labels_ROI[dict_ROI[ROI]] = Label(self, text=str(ROI) + ' : ' + dict_ROI[ROI], fg='green3')

            update_hdv_cum = partial(graph2.update_hdv, nom)

            self.dict_checkboxes[nom] = [IntVar()]
            self.dict_checkboxes[nom].append(Checkbutton(self, variable=self.dict_checkboxes[nom][0], command=update_hdv_cum))
            self.dict_checkboxes[nom][1].grid(row=row_noms_ROI+self.row_bouton, column=10)

            update_hdv_diff = partial(graph2.update_hdv, nom, type_hdv='_diff')

            self.dict_checkboxes[nom].append(IntVar())
            self.dict_checkboxes[nom].append(Checkbutton(self, variable=self.dict_checkboxes[nom][2], command=update_hdv_diff))
            self.dict_checkboxes[nom][3].grid(row=row_noms_ROI+self.row_bouton, column=11)

            self.dict_checkboxes[nom].append(row_noms_ROI+self.row_bouton)
            self.dict_checkboxes[nom].append(ROI)
            self.dict_labels_ROI[dict_ROI[ROI]].grid(row=row_noms_ROI + self.row_bouton, column=9, columnspan=1)
            self.row_bouton += 1
        #18.427

        Label(self, text='Cum').grid(row=1, column=10)

        Label(self, text='Diff').grid(row=1, column=11)

        self.row_bouton += 9

        Label(self).grid(row=self.row_bouton + 2, column=9)  # Pour faire un espace vertical

        self.liste_boutons_radios = [Radiobutton(self, text='Volume en pourcentage', variable=self.var, value='r', command=graph2.update_abs_rel),
                   Radiobutton(self, text='Volume absolu', variable=self.var, value='a', command=graph2.update_abs_rel)]
        self.liste_boutons_radios[0].grid(row=self.row_bouton + 3, column=9, columnspan=1)
        self.liste_boutons_radios[1].grid(row=self.row_bouton + 3, column=10, columnspan=2)

        Label(self).grid(row=self.row_bouton + 4, column=9)  # Pour faire un espace vertical




if __name__ == '__main__':

    ### *** INTERFACE GRAPHIQUE ***


    root = Tk()  # Fenête maîtresse


    #  - GRAPHIQUE BIDON (C'EST LÀ QUE SERA L'INTERFACE À THIBAULT)

    frame_graph1 = Frame()
    frame_graph1.grid(row=0, column=0, columnspan=8, rowspan=6)

    graph1 = Ex(frame_graph1)
    graph1.grid(row=0, column=0, columnspan=8, rowspan=6)
    graph1.tkraise()


    #  - TRAÇAGE DU HDV

    frame_graph2 = Frame()
    frame_graph2.grid(row=0, column=15, columnspan=8, rowspan=6)

    graph2 = Graph(frame_graph2)
    graph2.grid(row=0, column=15, columnspan=8, rowspan=6)
    graph2.tkraise()


    #  - MENU

    frame_controls = Frame()
    frame_controls.grid(row=0, column=9, columnspan=5)

    controls = Menu(frame_controls)
    controls.grid(row=0, column=9, columnspan=5)
    controls.tkraise()



    root.mainloop()
