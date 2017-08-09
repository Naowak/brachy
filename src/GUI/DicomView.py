#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DicomView.py
""" Classe permettant de gerer la vue DICOM et ses interactions """
# Author : Thibault PARPAITE, Cyrille BEAUCHESNE
# Copyright (c) 2017, CELIA Bordeaux
# This file is part of cythi, released under a BSD license.

from MainGUI import *


class DicomView(tk.Frame):
    """
    Classe fille de DicomRightWindow
    Permet d'afficher un fichier Dicom ainsi que les informations correspondantes
    Permet de naviguer entre les slices
    Permet de déposer/retirer des sources en dose mode
    Diverses operations (zoom...) sont egalement possibles dans ce mode
    BUG : lors du changement d'onglet avec les miniatures, il faut parfois actualiser
    la fenetre en faisant afficher/retirer miniature car dimensions incorrectes
    """
    def __init__(self, parent, dicom_navigation):
        tk.Frame.__init__(self, parent, bg="black")
        self.parent = parent
        self.dicom_navigation = dicom_navigation
        self.bind("<Visibility>", self.OnSwitchTab)
        self.initialize()

    def initialize(self):
        # Info
        self.seuil = 10
        
        # Drawing initial empty canvas
        self.blank_canvas = True
        (fig, axes) = plt.subplots(facecolor="black")
        axes.set_axis_bgcolor("black")
        axes.set_axis_off()
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.get_tk_widget().config(width=500, height=270)
        self.canvas._tkcanvas.config(highlightthickness=1, relief=tk.RAISED)
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
        """ Permet d'actualiser les miniatures """
        if self.dicom_navigation.display_settings['miniature'] == 1:
            self.dicom_navigation.parent.dicom_right_window.top_info.canvas_dicom.get_tk_widget().pack_forget()
            self.dicom_navigation.parent.dicom_right_window.top_info.canvas_HDV.get_tk_widget().pack(side=tk.RIGHT, fill=tk.Y, expand=False)
            # Tricky hack pour ne pas avoir le probleme de zoom lorsqu'on met les mignatures (on retrace les canvas initiaux)
            self.dicom_navigation.parent.dicom_right_window.dicom_hdv.canvas.get_tk_widget().update_idletasks()
            self.dicom_navigation.parent.dicom_right_window.dicom_view.canvas.get_tk_widget().update_idletasks()


    def OnClick(self, event):
        """ Seulement valide en dose mode """
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
        """ Deposer une source """
        self.curseur = [event.xdata, event.ydata]
        slice = self.dicom_navigation.slice
        
        closest_source = slice.get_closest_source(self.curseur, self.seuil)
        slice.add_source_displayed(self.curseur, closest_source)



    def OnRightClick(self, event):
        """ Retirer une source """
        self.curseur = [event.xdata, event.ydata]
        slice = self.dicom_navigation.slice
        
        closest_source = slice.get_closest_source(self.curseur, self.seuil)
        slice.remove_source_displayed(closest_source)


    def OnMouseScroll(self, event):
        """ Changer de  slice """
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
        """ Update la figure et l'affiche """
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
