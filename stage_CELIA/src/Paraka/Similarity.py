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
			self.create_dict(size)

	def create_dict(self, size) :
		self.tab = list()
		for i in range(size) :
			self.tab += [list()]
			for j in range(i+1, size) :
				self.tab[i] += [None]

	def set_similarity(self, ind_img1, ind_img2, score) :
		ind_img2 += 1
		ind_img1 += 1
		if ind_img1 < ind_img2 :
			ind_img2 -= ind_img1
			ind_img1 -= 1
			ind_img2 -= 1
			self.tab[ind_img1][ind_img2] = score
		elif ind_img1 > ind_img2 :
			ind_img1 -= ind_img2
			ind_img1 -= 1
			ind_img2 -= 1
			self.tab[ind_img2][ind_img1] = score

	def get_similarity(self, ind_img1, ind_img2) :
		ind_img2 += 1
		ind_img1 += 1
		if ind_img1 < ind_img2 :
			ind_img2 -= ind_img1
			ind_img1 -= 1
			ind_img2 -= 1
			return self.tab[ind_img1][ind_img2]
		elif ind_img1 > ind_img2 :
			ind_img1 -= ind_img2
			ind_img1 -= 1
			ind_img2 -= 1
			return self.tab[ind_img2][ind_img1]

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

def symmetric_similarity_between_two_imgs(img1, img2) :
	""" Retour : tuple : (max_score, intervale) """
	def symmetric_img(img) :
		len_first = len(img)
		len_second = len(img[0])
		return [[img[j][i] for j in range(len_second)] for i in range(len_first)]

	symmetric_img2 = symmetric_img(img2)
	score_first = similarity_between_two_imgs(img1, img2)
	score_second = similarity_between_two_imgs(img1, symmetric_img2)
	return max(score_first, score_second)

def calcul_matrix_similarity(img1, img2) :
	"""Calcul la matrice de similarité entre deux matrices

	Param :
		- img1, img2 : Une matrice de matériaux : ici une sub_img

	Retour :
		- Retourne la matrice de similarité entre les deux images"""
	size_x1 = len(img1)
	size_y1 = len(img1[0])
	size_x2 = len(img2)
	size_y2 = len(img2[0])
	if size_x1 != size_x2 or size_y1 != size_y2 :
		print(img1, img2)
		print(size_x1, size_x2)
		print(size_y1, size_y2)
		raise ValueError
	return [[1 if img1[i][j]==img2[i][j] else 0 for j in range(size_x1)] for i in range(size_y1)]

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
			if i == 0 and j == 0 :
				pass
			elif is_in_circle(i, j, size) :
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

def get_full_disque(q_intervals) :

	def projection(point, p_center, rayon = imd.Img_Density.RAYON_SUB_IMG) :
		relative_point = (point[0] - p_center[0], point[1] - p_center[1])
		longueur = m.sqrt(pow(relative_point[0], 2) + pow(relative_point[1], 2))
		rapport = float(rayon) / longueur
		point_proj = [relative_point[0] * rapport + p_center[0], relative_point[1] * rapport + p_center[0]]
		return point_proj

	def is_in_circle(point, center,  rayon = imd.Img_Density.RAYON_SUB_IMG) :
		return m.sqrt(pow(point[0] - center[0], 2) + pow(point[1] - center[1], 2)) <= rayon

	def get_value_on_circle(point_proj, p_center, rayon = imd.Img_Density.RAYON_SUB_IMG) :
		point_relative = (point_proj[0] - p_center[0], point_proj[1] - p_center[1])
		point_norm = [point_relative[0] / rayon, point_relative[1] / rayon]

		value = m.acos(point_norm[0])
		if point_norm[1] < 0 :
			value = 2*m.pi - value
		return value

	def recompose_intervale_from_q_intervals(q_intervals) :

		def modulo_2pi(intervale) :
			limite = interval([0, m.pi*2])
			res = interval()
			for elem in intervale :
				inter = interval(elem)
				tmp = inter & limite
				if tmp == inter :
					#interval ne dépasse pas
					res = res | inter
				else :
					#interval qui dépasse
					res = res | tmp
					#on tente au dessus de 2 pi
					tmp_inter = inter - 2*m.pi
					tmp = tmp_inter & limite
					res = res | tmp
					#on tente en dessous de 2 pi
					tmp_inter = inter + 2*m.pi
					tmp = tmp_inter & limite
					res = res | tmp
			return res

		[up_left, up_right, down_left, down_right] = q_intervals
		up_left += m.pi
		up_right += m.pi / 2
		down_left += 1.5 * m.pi
		fusion_inter = up_left | up_right | down_left | down_right
		result_inter = modulo_2pi(fusion_inter)
		return result_inter

	rayon = imd.Img_Density.RAYON_SUB_IMG
	p_center = (rayon - 0.5, rayon - 0.5)
	img_result = [[1 for i in range(2*rayon)] for j in range(2*rayon)]
	intervale = recompose_intervale_from_q_intervals(q_intervals)

	for i in range(2*rayon) :
		for j in range(2*rayon) :
			point = (i, j)
			if is_in_circle(point, p_center) :
				point_proj = projection(point, p_center)
				value_on_circle = get_value_on_circle(point_proj, p_center)
				if value_on_circle in intervale :
					img_result[i][j] = 0
			else :
				pass
				img_result[i][j] = -1

	return img_result




if __name__ == "__main__" :
	density_file = "../../../working_dir/slice_090/densite_lu/densite_hu.don"
	config_file = "../../../working_dir/slice_090/densite_lu/config_KIDS.don"

	inter1 = interval([0.3, 1.2])
	inter2 = interval([1.4, 1.6])
	inter3 = interval([0.1, 0.2], [0.5, 0.6])
	inter4 = interval()
	q_intervals = (inter1, inter2, inter3, inter4)

	img = get_full_disque(q_intervals)
	plt.imshow(img)
	plt.show()

	# img = imd.Img_Density(density_file, config_file)

	# quartil_1 = img.sub_imgs[49]
	# quartil_2 = img.sub_imgs[233]
	# score, inter = similarity_between_two_imgs(quartil_1, quartil_2, False)
	# print(inter)
	# mat = calcul_matrix_similarity(quartil_1, quartil_2)
	# res = get_disque_segment(mat, inter)

	# figure = plt.figure()
	# figure.add_subplot(2, 2, 1)
	# plt.imshow(quartil_1)
	# figure.add_subplot(2, 2, 2)
	# plt.imshow(quartil_2)
	# figure.add_subplot(2, 2, 3)
	# plt.imshow(mat)
	# figure.add_subplot(2, 2, 4)
	# plt.imshow(res)
	# plt.show()




