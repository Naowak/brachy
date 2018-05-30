#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-

import Img_Density as imd
import copy
from matplotlib import pyplot as plt
from interval import interval
import math as m


class Dict_Sim :

	def __init__(self, size = None) :
		self.tab = None
		if size != None :
			self.tab = [[None for i in range(size)] for j in range(size)]

	def set_similarity(self, ind_img1, ind_img2, sim) :
		self.tab[ind_img1][ind_img2] = sim
		self.tab[ind_img2][ind_img1] = sim

	def get_similarity(self, ind_img1, ind_img2) :
		return self.tab[ind_img1][ind_img2]

	def save_similarity(self, directory) :
			file_name = directory + "similarity.don"
			with open(file_name, "w+") as f :
				f.write(str(self.tab))

	def load_similarity(self, file_name) :
		def is_sim(value) :
			if value[:5] == " None" or value[:4] == "None" :
				return True
			return is_float(value)

		def is_float(value) :
			try :
				float(value)
				return True
			except :
				return False

		def string_to_sim(value) :
			if value[:5] == " None" or value[:4] == "None":
				return None
			return float(value)

		with open(file_name, 'r') as f :
			res = f.read()
			sim = [[string_to_sim(c) for c in b.split(',') if is_sim(c)] for b in res.replace(']', '').split("[") if len(b) > 0]
			self.tab = sim

	def __str__(self) :
		return str(self.tab)


def calcul_matrix_similarity(img1, img2) :
	"""Calcul la matrice de similarité entre deux matrices

	Param :
		- img1, img2 : Une matrice de matériaux : ici une sub_img

	Retour :
		- Retourne la matrice de similarité entre les deux images"""
	size = imd.Img_Density.RAYON_SUB_IMG
	return [[1 if img1[i][j]==img2[i][j] else 0 for j in range(size)] for i in range(size)]

def similarity_between_two_imgs(img1, img2, plot = False) :

	def get_corners_projections(pixel, rayon_max,) :

		def projection(point, rayon_max) :
			longueur = m.sqrt(pow(point[0], 2) + pow(point[1], 2))
			rapport = float(rayon_max) / longueur
			point_on_circle = [point[0]*rapport, point[1]*rapport]
			return point_on_circle

		def get_two_corner_from_pixel(pixel) :
			min_x = pixel[0] - 0.5
			max_x = pixel[0] + 0.5
			min_y = pixel[1] - 0.5
			max_y = pixel[1] + 0.5
			point_1 = (max_x, min_y)
			point_2 = (min_x, max_y)
			return point_1, point_2

		p1, p2 = get_two_corner_from_pixel(pixel)
		return projection(p1, rayon_max), projection(p2, rayon_max)

	def is_in_circle(i, j, rayon) :
		return m.sqrt(pow(i, 2) + pow(j, 2)) <= rayon 

	def get_intervale(point_1, point_2) :
		cos_1 = float(point_1[0])/size
		cos_2 = float(point_2[0])/size
		acos_1 = m.acos(cos_1)
		acos_2 = m.acos(cos_2)
		if acos_1 < acos_2 :
			return interval([acos_1, acos_2])
		else :
			return interval([acos_2, acos_1])

	def get_intervale_length(intervale) :
		cpt = 0
		for x in intervale :
			cpt += x.sup - x.inf
		return cpt

	inter = interval()
	matrix = calcul_matrix_similarity(img1, img2)
	size = imd.Img_Density.RAYON_SUB_IMG

	# A REVOIR POUR OPTIMISATION
	for i in range(size) :
		for j in range(size) :
			if is_in_circle(i, j, size) and matrix[i][j] == 0 : 
				#différence repéré entre les deux images
				#on projette le point sur le cercle
				proj_1, proj_2 = get_corners_projections((i, j), size)
				inter = inter | get_intervale(proj_1, proj_2)

	if plot :
		print(inter)
		print(m.pi/2 - get_intervale_length(inter))
		fig = plt.figure()
		fig.add_subplot(3, 1, 1)
		plt.imshow(img1)
		fig.add_subplot(3, 1, 2)
		plt.imshow(img2)
		fig.add_subplot(3, 1, 3)
		plt.imshow(matrix)
		plt.show()


	return m.pi/2 - get_intervale_length(inter), inter

def max_score_similarity() :
	return m.pi / 2

def get_disque_segment(img, intervale) :
	def projection(point, rayon_max) :
		longueur = m.sqrt(pow(point[0], 2) + pow(point[1], 2))
		rapport = float(rayon_max) / longueur
		point_on_circle = [point[0]*rapport, point[1]*rapport]
		return point_on_circle

	def is_in_circle(i, j, rayon) :
		return m.sqrt(pow(i + 0.5, 2) + pow(j + 0.5, 2)) <= rayon 

	size = imd.Img_Density.RAYON_SUB_IMG
	res = [[1 for i in range(size)] for j in range(size)]

	for i in range(size) :
		for j in range(size) :
			# A AMELIORER, ON PEUT PARCOURIR QUE LES PIXELS DU DISQUE
			if i != 0 or j != 0 :
				if is_in_circle(i, j, size) :
					p = [i, j]
					proj = projection(p, size)
					proj_norm = float(proj[0])/size
					if proj_norm > 1 :
						proj_norm = 1.0
					value_on_circle = m.acos(proj_norm)
					if value_on_circle in intervale :
						res[i][j] = 0
				else :
					res[i][j] = -1
	return res



if __name__ == "__main__" :
	density_file = "../../../working_dir/slice_090/densite_lu/densite_hu.don"
	config_file = "../../../working_dir/slice_090/densite_lu/config_KIDS.don"

	img = imd.Img_Density(density_file, config_file)

	quartil_1 = img.sub_imgs[49]
	quartil_2 = img.sub_imgs[233]
	score, inter = similarity_between_two_imgs(quartil_1, quartil_2, False)
	print(inter)
	mat = calcul_matrix_similarity(quartil_1, quartil_2)
	res = get_disque_segment(mat, inter)

	figure = plt.figure()
	figure.add_subplot(2, 2, 1)
	plt.imshow(quartil_1)
	figure.add_subplot(2, 2, 2)
	plt.imshow(quartil_2)
	figure.add_subplot(2, 2, 3)
	plt.imshow(mat)
	figure.add_subplot(2, 2, 4)
	plt.imshow(res)
	plt.show()




