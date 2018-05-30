#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-

import math as m
import matplotlib.pyplot as plt

NB_MATERIAUX = 2

class Zoomed_Image() :
	""" Décomposition d'une image en quadtree, plusieurs niveau de décomposition """

	class Point() :
		def __init__(self, x, y) :
			self.x = x
			self.y = y

		def __str__(self) :
			string = "[" + str(self.x) + ", " + str(self.y) + "]"
			return string

	class Big_Pixel() :
		""" Un gros pixel """

		def __init__(self, topLeft, bottomRight, value) :
			self.topLeft = topLeft
			self.bottomRight = bottomRight
			self.value = value

		def fusion(bp1, bp2, bp3, bp4) :
			""" Fusionne 4 BigPixels formant un carré en un nouveau BigPixel 
					bp1 = pixel haut gauche
					bp2 = pixel haut droite
					bp3 = pixel bas gauche
					bp4 = pixel bas droite"""

			def find_new_value(bps) :
				tab_vote = [0] * NB_MATERIAUX
				for bp in bps :
					tab_vote[bp.value] += 1

				nb_vote_max = 0
				new_value = -1
				for materiaux, nb in enumerate(tab_vote) :
					if nb >= nb_vote_max :
						#Le égal permet de faire passer les autres éléments que 
						#l'eau en priorité en cas d'égalité des votes
						nb_vote_max = nb
						new_value = materiaux
				return new_value

			bps = [bp1, bp2, bp3, bp4]	
			topleft = bp1.topLeft
			bottomright = bp4.bottomRight
			value = find_new_value(bps)
			return Zoomed_Image.Big_Pixel(topleft, bottomright, value)

		def __str__(self) :
			string = str(self.topLeft) + " -> " + str(self.bottomRight) + " : " + str(self.value)
			return string


	def __init__(self, img) :
		self.img = img
		self.size = len(img)
		self.zoom_max = int(m.log(self.size, 2))

		self.zoomed_imgs = [None] * (self.zoom_max+1)
		#contient les images zoomées, elles sont zoomées 2^indice fois
		self.create_zoomed_imgs()
	
	def create_zoomed_imgs(self) :
		"""initialise et créer les images zoomées """

		def init_zoom(self) :
			"""Initialise le zoom 0"""
			zoom0 = [[Zoomed_Image.Big_Pixel(Zoomed_Image.Point(i, j), Zoomed_Image.Point(i, j), self.img[i][j]) for i in range(self.size)] for j in range(self.size)]
			self.zoomed_imgs[0] = zoom0

		def zoom_and_add(self, z_img) :
			size = len(z_img) / 2
			new_zoom = [[None for i in range(size)] for j in range(size)]
			for i in range(size) :
				for j in range(size) :
					bp1 = z_img[2*i][2*j]
					bp2 = z_img[2*i+1][2*j]
					bp3 = z_img[2*i][2*j+1]
					bp4 = z_img[2*i+1][2*j+1]
					new_zoom[i][j] = Zoomed_Image.Big_Pixel.fusion(bp1, bp2, bp3, bp4)
			return new_zoom

		init_zoom(self)
		for i in range(1, len(self.zoomed_imgs)) :
			self.zoomed_imgs[i] = zoom_and_add(self, self.zoomed_imgs[i-1])

	def extract_zoomed_img(self, zoom) :
		indice = int(m.log(zoom, 2))
		z_img = self.zoomed_imgs[indice]
		size_img = len(z_img)
		img = [[z_img[i][j].value for i in range(size_img)] for j in range(size_img)]
		return img

	def show(self) :
		nb_zoomed_imgs = len(self.zoomed_imgs)
		fig = plt.figure()
		for i in range(nb_zoomed_imgs) :
			fig.add_subplot(1, nb_zoomed_imgs, i+1)
			img = self.extract_zoomed_img(pow(2, i))
			plt.imshow(img)
		plt.show()

if __name__ == "__main__" : 
	img = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1], [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1], [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1], [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1], [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1], [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1], [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1], [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1], [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]]
	for line in img : 
		for i, n in enumerate(line) :
			if n == -1 :
				line[i] = 1
	a = Zoomed_Image(img)
	a.show()


