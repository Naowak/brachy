#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-
from matplotlib import pyplot as plt
import math
import random
import copy

import Quartil

class Img_Density :
	"""Classe représentant une image de densité quantifier
	 en M différentes matières. L'image est obtenu à partir 
	 du fichier densite_hu.don calculé par cythi, qui représente
	 la zone d'influence à calculer.
	 Nous récupérons aussi la position des sources dans config_KIDS.don"""

	RAYON_SUB_IMG = 32
	TAILLE_SUB_IMG = 2*RAYON_SUB_IMG - 1
	CENTER_IMG = RAYON_SUB_IMG - 1
	CIRCLE_SHAPE = [[1 if math.sqrt(pow(i-CENTER_IMG, 2) + pow(j-CENTER_IMG, 2)) <= RAYON_SUB_IMG - 1 else 0 for i in range(TAILLE_SUB_IMG)] for j in range(TAILLE_SUB_IMG)]

	 # ------------------------ Init -----------------------------

	def __init__(self, density_file, config_file) :
	 	""" Param :
	 			- density_file : String : Chemin du fichier densite_hu.don
	 			- config_file : String : Chemin du fichier config_KIDS.don

	 		Une instance possède les attributs suivants :
	 		 - self.img_density : image de densité extraite de density_file
	 		 - self.width : largeur de l'image de densité
	 		 - self.height : hauteur de l'image de densité
	 		 - self.sources : position des sources par rapport à l'origine 
	 		 		de l'image de densité
	 		 - self.img_material : img de densité converti en image des matériaux
	 		 - self.sub_imgs : Sous images de matériaux extraite pour chaque source"""

 		def find_directory(density_file) :
 		 	length = len(density_file)
 		 	for i in range(length-1, -1, -1) :
 		 		if density_file[i] == "/" :
 		 			return density_file[:i+1]

	 	self.directory = find_directory(density_file)
	 	#On charge l'image
	 	self.load_img_density(density_file)
	 	#On charge les sources
	 	self.load_sources(config_file)
	 	self.extract_material_from_density([465]) 
	 	self.extract_sub_imgs()

	def load_img_density(self, density_file) :
		"""  Charge les niveaux de densité de l'image à partir de density_file
		Param : 
			- density_file : String : Chemin du fichier densite_hu.don"""

		self.img_density = list()
		with open(density_file) as f :
			for line in f :
				vector_density_column = [int(d) for d in line.split(" ")]
				self.img_density += [vector_density_column]
		self.width = len(self.img_density[0])
		self.height = len(self.img_density)

	def load_sources(self, config_file) :
		""" Charge la position des sources
		Param :
			- config_file : String : Chemin du fichier config_KIDS.don"""

		self.sources = list()
		with open(config_file) as f :
			for line in f :
				if "volume_spheroid" in line :
					tab = line.split(" ")
					x1 = float(tab[2])*10 + 1 # Pour une raison inconnue mes sources n'étais pas centrée
					x2 = float(tab[3])*10 + 2 # Voilà le problème réglé
					self.sources += [(int(round(x1)), int(round(x2)))]

	def extract_material_from_density(self, limits_density_to_material) :
		""" Extrait d'une image de densité classique une image de matériaux.
		On identifie chaque matériaux par un ID.
		L'iD est donné de la manière suivante : 
			exemple : 
			limits_density_to_matérial = [-20, 50, 230, 520]
			ID matériaux densite < -20 : 0
			... < 50 : 1
			... < 230 : 2
			... < 520 : 3
			... >= 520 : 4
	 	# -1000 x < -86 : adipose
	 	# -86 < x < 841 : eau
	 	# 841 < x < 15 000 : os

		Param :
			- limits_density_to_material : list() : valeurs des seuils de densité
				entre les différents matériaux. """

		limits_density_to_material.sort()
		self.img_material = [[0 for i in range(self.width)] for j in range(self.height)]
		for j in range(self.height) :
			for i in range(self.width) :
				material_found = False
				for material, limit in enumerate(limits_density_to_material) :
					if self.img_density[j][i] < limit :
						self.img_material[j][i] = material
						material_found = True
						break
				if not material_found :
					#materiaux pas encore trouvé -> dernier matériaux où densité est >= 
					#au dernier seuil
					self.img_material[j][i] = len(limits_density_to_material)
					material_found = True

	def extract_sub_imgs(self) :
		""" Extrait de self.img_material la sous image associé à chacune
		des sources de self.sources. Enregistre le résultats dans self.sub_imgs"""

		rayon = self.RAYON_SUB_IMG

		self.sub_imgs = list()
		for source in self.sources :
			s_ord = source[1]
			s_abs = source[0]
			sub_ord = self.img_material[s_ord - rayon + 1: s_ord + rayon]
			sub_img = [tmp[s_abs - rayon + 1 : s_abs + rayon] for tmp in sub_ord]
			if len(sub_img) == self.TAILLE_SUB_IMG and len(sub_img[0]) == self.TAILLE_SUB_IMG :
				sub_img = [[sub_img[i][j] if self.CIRCLE_SHAPE[i][j] == 1 else -1 for i in range(self.TAILLE_SUB_IMG)] for j in range(self.TAILLE_SUB_IMG)]
				elem = (sub_img, s_abs, s_ord)
				self.sub_imgs += [elem]


	def extract_images(self) :
		return self.sub_imgs

	def extract_quart_images(self) :
		#ce sont les images de d'apprentissage que l'on extrait
		#il faut conserver un chemin vers leur calcul de dose
		#et savoir quelle est sont orientation (localisation)
		location = ["NO", "NE", "SO", "SE"]
		rayon = self.RAYON_SUB_IMG
		quart_images = list()
		for ind, elem in enumerate(self.sub_imgs) : # il y a autant de sub_img que de sources
			img = elem[0]
			filename_dose = self.directory + "dose_source_" + str(ind+1).zfill(3) + ".dat"
			quartils = extract_quartil(img, rayon)
			quartils = [Quartil.Quartil(q, filename_dose, location[i], self.sources[ind]) for i, q in enumerate(quartils)]
			quart_images += quartils
		return quart_images

	def extract_slice(self) :
		return self.img_density

	def extract_sources(self) :
		return self.sources

	#------------------------- Plot --------------------------

	def show_img_density(self) :
		"""Affiche l'image de densité"""
		plt.imshow(self.img_density)
		self.add_sources_plot()
		plt.show()

	def show_img_materials(self) :
		"""Affiche l'image de matériaux"""
		plt.imshow(self.img_material)
		self.add_sources_plot()
		plt.show()

	def add_sources_plot(self) :
		"""Affiche les sources sur la dernière image chargé par plot"""
		for source in self.sources :
			plt.scatter(source[0], source[1], c='r')

	def show_imgs(self) :
		"""Affiche l'image de densité et l'image de matériaux cote à cote"""
		fig = plt.figure()
		fig.add_subplot(1, 2, 1)
		plt.imshow(self.img_density)
		self.add_sources_plot()
		fig.add_subplot(1, 2, 2)
		plt.imshow(self.img_material)
		self.add_sources_plot()
		plt.show()

	def show_sub_imgs(self) :
		"""Affiche toutes les sous images une par une"""
		for sub_img in self.sub_imgs :
			plt.imshow(sub_img[0])
			plt.show()


# Classe finie -----------------------------------------------

def rotation(img, nb) :
	""" Effectue nb rotation à 90 degrees sur l'images"""

	def rotate_90_degrees(img) :
		tmp = list(zip(*reversed(img)))
		return [list(line) for line in tmp]

	for _ in range(nb) :
		img = rotate_90_degrees(img)
	return img

def extract_quartil(img, rayon = Img_Density.RAYON_SUB_IMG) :
	up_left = img[:rayon]
	up_left = [line[:rayon] for line in up_left]
	up_left = rotation(up_left, 2)

	up_right = img[:rayon]
	up_right = [line[rayon - 1:] for line in up_right]
	up_right = rotation(up_right, 1)

	down_left = img[rayon - 1:]
	down_left = [line[:rayon] for line in down_left]
	down_left = rotation(down_left, 3)

	down_right = img[rayon - 1:]
	down_right = [line[rayon - 1:] for line in down_right]

	return [up_left, up_right, down_left, down_right]

def recompose_into_img(quartils, priority, rayon = Img_Density.RAYON_SUB_IMG) :

	def copy_into(sub, full, location) :

		def copy_sub_into_full(sub_img, full_img, origine_x, origine_y) :
			sub_img_size = len(sub_img)
			for i, x in enumerate(list(range(origine_x, origine_x + sub_img_size))) :
				for j, y in enumerate(list(range(origine_y, origine_y + sub_img_size))) :
					full_img[x][y] = sub_img[i][j]

		if location == "NO" :
			origine_x = 0
			origine_y = 0
		elif location == "NE" :
			origine_y = Img_Density.RAYON_SUB_IMG - 1
			origine_x = 0
		elif location == "SO" :
			origine_y = 0
			origine_x = Img_Density.RAYON_SUB_IMG - 1
		elif location == "SE" :
			origine_x = Img_Density.RAYON_SUB_IMG - 1
			origine_y = Img_Density.RAYON_SUB_IMG - 1

		copy_sub_into_full(sub, full, origine_x, origine_y)

	# priority = [NO, NE, SO, SE] -> ordre inverse de superposition
	[up_left, up_right, down_left, down_right] = quartils
	up_left = rotation(up_left, 2)
	up_right = rotation(up_right, 3)
	down_left = rotation(down_left, 1)
	quartils = [up_left, up_right, down_left, down_right]

	all_location = ["NO", "NE", "SO", "SE"]

	priority.reverse()
	full_img = [[0 for i in range(Img_Density.TAILLE_SUB_IMG)] for j in range(Img_Density.TAILLE_SUB_IMG)]
	for p in priority :
		i = all_location.index(p)
		q = quartils[i]
		copy_into(q, full_img, p)

	return full_img



# ----------------------- Main -----------------------

if __name__ == "__main__" :
	density_file = "../../../working_dir/slice_090/densite_lu/densite_hu.don"
	config_file = "../../../working_dir/slice_090/densite_lu/config_KIDS.don"

	img = Img_Density(density_file, config_file)
	# img.show_imgs()
	# img.show_sub_imgs()
	a = img.extract_quart_images()
	for i, sub_img in enumerate(img.sub_imgs) :
		sub_img = sub_img[0]
		quartils = a[4*i: 4*i + 4]
		recomp = recompose_into_img(quartils, ["NO", "SE", "SO", "NE"])
		fig = plt.figure()
		fig.add_subplot(2, 1, 1)
		plt.imshow(sub_img)
		fig.add_subplot(2, 1, 2)
		plt.imshow(recomp)
		plt.show()

