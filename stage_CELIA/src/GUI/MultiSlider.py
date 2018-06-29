#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as tk
import numpy as np

class MultiSlider(tk.Canvas):
    """
    Classe permettant d'avoir un widget de type SCALE avec plusieurs sliders
    Cela permet notamment de definir des intervalles de type min/max
    """
    def __init__(self, parent, cursors_values=[], length=300, orient=tk.HORIZONTAL, from_=0, to=100, resolution=1, command=None):
        self.parent = parent
        self.cursors_values = cursors_values
        self.length = length
        self.orient = orient
        self.from_ = from_
        self.to = to
        self.resolution = resolution
        self.n_curseurs = len(cursors_values)
        self.command = command
        self.pad = 30
        self.padx = 30
        self.pady = 30
        self.cursor_length = 20

        if orient == tk.HORIZONTAL:
            self.height = 20
            self.width = self.length
        elif orient == tk.VERTICAL:
            self.height = self.length
            self.width = 20
        
        self.initialize()


    def initialize(self):
        tk.Canvas.__init__(self, self.parent, width=self.width + 2 * self.padx, height=self.height + 2 * self.pady)
        self.bind( "<Button-1>", self.onLeftClick)
        self.bind( "<ButtonRelease-1>", self.onLeftClickReleased)
        self.bind( "<B1-Motion>", self.onMouseMove)
        
        self.cursor_max = self.from_

        # On initialise le tableau des valeurs et positions
        self.initializeSliderPositions()

        # Curseurs
        step = (self.to - self.from_) / (self.n_curseurs - 1)
        
        self.cursors = []

        for i in range(self.n_curseurs):
            closest_value = self.getClosestValue(step * i)
            self.cursors.append(Cursor(self, i, self.cursors_values[i],
                                       self.value_to_position_LUT[closest_value]))
            
        # Affichage
        self.refreshSlider()
        

    def initializeSliderPositions(self):
        # Les valeurs possibles pour le slider
        self.values = np.arange(self.from_, self.to + self.resolution, self.resolution)

        if len(self.values) > self.length:
            print "Erreur, la resolution est trop petite pour la longueur du slider"

        # Les positions possibles pour le slider
        self.positions = np.linspace(0, self.length, len(self.values))
        self.positions = [ int(position) for position in self.positions ]

        # La correspondance position / valeur
        self.position_to_value_LUT = {}
        self.value_to_position_LUT = {}
        
        for (value, position) in zip(self.values, self.positions):
            self.position_to_value_LUT[position] = value
            self.value_to_position_LUT[value] = position


    def refreshSlider(self):
        self.delete("all")
        self.drawBackground()

        for cursor in self.cursors:
            cursor.drawCursor()
    

    def drawBackground(self):
        self.create_rectangle(self.padx - self.cursor_length / 2,
                              self.pady,
                              self.padx + self.width + self.cursor_length / 2,
                              self.pady + self.height,
                              fill="gray75")


    def onLeftClick(self, event):
        for cursor in self.cursors:
            cursor.onLeftClick(event)


    def onLeftClickReleased(self, event):
        for cursor in self.cursors:
            cursor.onLeftClickReleased(event)


    def onMouseMove(self, event):
        for cursor in self.cursors:
            cursor.onMouseMove(event)


    def getClosestValue(self, x):
        min_value = self.values[0]

        for value in self.values:
            if self.distance(x, value) < self.distance(x, min_value):
                min_value = value

        return min_value


    def getClosestPosition(self, x):
        x = x - self.padx
        min_pos_x = self.positions[0]

        for position in self.positions:
            if self.distance(x, position) < self.distance(x, min_pos_x):
                min_pos_x = position

        return min_pos_x


    def distance(self, x, x_bis):
        return abs(x - x_bis)


    def collisionAvecCurseur(self, id, event):
        """ Regarde si le curseur d'identifiant id est en collision avec un curseur adjacent """
        (x, y) = (event.x, event.y)
        x = x - self.padx

        # Un seul curseur
        if self.n_curseurs == 1:
            return False

        if (id - 1) < 0:
            return x >= self.cursors[id+1].position
        elif (id + 1) >= self.n_curseurs:
            return x <= self.cursors[id-1].position
            
        return (x <= self.cursors[id-1].position) or (x >= self.cursors[id+1].position)


class Cursor:
    def __init__(self, parent, id, cursor_value, position):
        self.parent = parent
        self.id = id
        self.cursor_value = cursor_value
        self.padx = self.parent.padx
        self.pady = self.parent.pady
        self.cursor_length = self.parent.cursor_length
        self.height = self.parent.height
        self.width = self.parent.width
        self.positions = self.parent.positions
        self.position_to_value_LUT = self.parent.position_to_value_LUT
        self.dragged_mode = False

        # Label
        self.label_var = tk.StringVar()
        self.label = tk.Label(self.parent, textvariable=self.label_var)

        self.setCursorPosition(position)


    def drawCursor(self):
        self.parent.create_rectangle(self.padx + self.position_x0,
                                     self.pady,
                                     self.padx + self.position_x1,
                                     self.pady + self.height,
                                     fill="gray95")
        
        self.parent.create_line(self.padx + self.position,
                                self.pady + 5,
                                self.padx + self.position,
                                self.pady + self.height - 5)


        self.label_var.set(str(self.cursor_value.get()))
        self.label.place(x=self.padx + self.position, y=self.pady - 30, anchor=tk.N)


    def onLeftClick(self, event):
        """ Permet de voir si on a cliqué sur le curseur """
        (x, y) = (event.x, event.y)
        
        if (x >= self.padx + self.position_x0) and \
           (x <= self.padx + self.position_x1) and \
           (y >= self.pady) and \
           (y <= self.pady + self.height):
            self.dragged_mode = True


    def onLeftClickReleased(self, event):
        self.dragged_mode = False


    def onMouseMove(self, event):
        """ Permet de gérer le curseur une fois qu'on a cliqué dessus une première fois """
        if not(self.dragged_mode):
            return
        
        (x, y) = (event.x, event.y)

        # Souris hors du slider
        if (x < self.padx) or (x > self.padx + self.width):
            return

        # Curseur en collision avec un autre curseur
        if self.parent.collisionAvecCurseur(self.id, event):
            return

        closest_position = self.parent.getClosestPosition(x)
        self.setCursorPosition(closest_position)
        self.parent.refreshSlider()


    def setCursorPosition(self, position):
        self.position = position
        self.position_x0 = position - self.cursor_length / 2
        self.position_x1 = position + self.cursor_length / 2
        self.cursor_value.set(self.position_to_value_LUT[position])

        # Execution de la commande
        if self.parent.command is not None:
            self.parent.command()
        
        
### TEST
#root = tk.Tk()
#frame = tk.Frame(root, width=800, height=500).pack()
#var_1 = tk.DoubleVar()
#var_2 = tk.DoubleVar()

#vars = [var_1, var_2]
#multislider = MultiSlider(frame, cursors_values=vars, from_=0, to=100, resolution=0.5).pack()
#root.mainloop()
    
