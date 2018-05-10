#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-

import Img_Density as imd
import copy
from matplotlib import pyplot as plt

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
			return is_int(value)

		def is_int(value) :
			try :
				int(value)
				return True
			except :
				return False

		def string_to_sim(value) :
			if value[:5] == " None" or value[:4] == "None":
				return None
			return int(value)

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
	size = 2*imd.Img_Density.RAYON_SUB_IMG
	return [[1 if img1[i][j]==img2[i][j] else 0 for j in range(size)] for i in range(size)]

def calcul_similarity(matrix_similarity, filtre=None, plot=False) :
	""" Calcul le score de similarité entre deux matrices.

	Param :
		- matrix_similarity : Matrice de similarité entre les deux matrices
				pour lesquelles on souhaite calculer le score.
		- filtre : String : ["gaussien", "proportionnel", "lineaire"]

	Retour :
		- int : score de similarité
	"""
	size = 2*imd.Img_Density.RAYON_SUB_IMG
	warm_img = [[0 for i in range(size)] for j in range(size)]
	res = 0
	for j in range(size) :
		for i in range(size) :
			if matrix_similarity[j][i] == 1 :
				#Dans le cas où les deux pixels sont égaux
				tmp = 1
				try :
					if matrix_similarity[j-1][i] == 1 :
						tmp += 1
				except IndexError :
					tmp += 1
				try :
					if matrix_similarity[j][i-1] == 1 :
						tmp += 1
				except IndexError :
					tmp += 1
				try :
					if matrix_similarity[j+1][i] == 1 :
						tmp += 1
				except IndexError :
					tmp += 1
				try :
					if matrix_similarity[j][i+1] == 1 :
						tmp += 1
				except IndexError :
					tmp += 1
				warm_img[j][i] = tmp
				if filtre == None :
					res += tmp
				elif filtre == "gaussien" :
					res += tmp*gaussienne(i, j, 20)
				elif filtre == "proportionnel" :
					res += tmp*proportionnelle(i,j)

	if plot :
		plt.imshow(warm_img)
		plt.show()

	return res

def similarity_between_two_imgs(img1, img2, filtre = None, plot = False) :
	""" Retourne le score de similarité entre img1 et img2 en prenant en compte le filtre
	et le champs de vue.

	Param :
		- img1 : double list de int : représente l'image 1
		- img2 : double list de int : représente l'image 2
		- filtre : String : Nom du filtre à utiliser. Exemple : ["gaussien", "proportionnel"]

	Retour :
		- int : score de similarité entre img1 et img2
	"""
	m = calcul_matrix_similarity(img1, img2)
	list_points_hidden = activate_field_of_view(m)
	for p in list_points_hidden :
		m[p[1]][p[0]] = 0

	if plot :
		fig = plt.figure()
		fig.add_subplot(3, 1, 1)
		plt.imshow(m)
		fig.add_subplot(3, 1, 2)
		plt.imshow(img1)
		fig.add_subplot(3, 1, 3)
		plt.imshow(img2)
		plt.show()

	return calcul_similarity(m, filtre)

def max_score_similarity(size_img, filtre=None) :
	""" Retour le score max de similarité obtenable en fonction de la taille
	des images que l'ont compare.

	Param :
		- size_img : int : taille de l'image (qui doit être un carré)
		- filtre : String : ["gaussien", "proportionnel", "lineaire"]

	Retour :
		- int : score de similirité maximum possible
	"""
	img = [[1 for i in range(size_img)] for j in range(size_img)]
	return calcul_similarity(img, filtre)

def gaussienne(x, y, var) :
	""" Retourne la valeur Gaussienne du point (x,y) pour une gaussienne situé au centre
	de l'image et de variance var

	Param :
		- x : int : position en x
		- y : int : position en y
		- var : float : variance de la gaussienne

	Retour :
		float : valeur de la gaussienne au point (x,y)
	"""
	rayon = imd.Img_Density.RAYON_SUB_IMG
	x0 = rayon
	y0 = rayon
	x -= x0
	y -= y0
	return math.exp(-(pow(x,2)/(float(2*var)) + pow(y,2)/(float(2*var))))

def proportionnelle(x, y) :
	""" Retourne la valeur du point (x,y). Celle ci correspond proportionnellement
	à la distance au centre. 

	Param :
		- x : int : position en x
		- y : int : position en y

	Retour :
		float : valeur du point (x,y)
	"""
	rayon = float(imd.Img_Density.RAYON_SUB_IMG)
	x0 = rayon 
	y0 = rayon 
	x -= x0
	y -= y0
	x = float(x)
	y = float(y)
	return math.sqrt(pow(x/rayon,2) + pow(y/rayon, 2))

def line(x, y, center_x = imd.Img_Density.CENTER_IMG, center_y = imd.Img_Density.CENTER_IMG) :
	""" Retourne les coordonnées de tous les points où passe la droite allant du 
	centre au point (x,y).

	Param :
		- x : int/float : position en x
		- y : int/float : position en y
		- center_x : int/float : centre de l'image en x
		- center_y : int/float : centre de l'image en y
	
	Retour :
		list de tuple : [(x1,y1), (x2,y2), ...] : coordonnée des points de la droite
	"""
	#longueur en x
	x -= center_x
	#longueur en y
	y -= center_y
	rayon = imd.Img_Density.RAYON_SUB_IMG

	coef1 = float(x)/float(y)
	coef2 = float(y)/float(x)
	my_line = []
	if abs(x) <= abs(y) :
		if y >= 0 :
			if x < 0 : 
				for i in range(0, int(round(y))) :
					my_line += [(int(round(coef1*i + rayon)) - 1, i + rayon)]
			else :		
				for i in range(1, int(round(y)) + 1) :
					my_line += [(int(round(coef1*i + rayon)) - 1, i + rayon - 1)]
		else :
			if x < 0 :
				for i in range(0, int(round(y)), -1) :
					my_line += [(int(round(coef1*i + rayon)) -1, i + rayon - 1)]
			else :
				for i in range(0, int(round(y)), -1) :
					my_line += [(int(round(coef1*i + rayon)), i + rayon - 1)]
	else :
		if x >= 0 :
			if y < 0 :
				for i in range(1, int(round(x)) + 1) :
					my_line += [(int(round(i + rayon)) - 1, int(round(coef2*i + rayon)))]
			else :
				for i in range(1, int(round(x)) + 1) :
					my_line += [(int(round(i + rayon)) - 1, int(round(coef2*i + rayon)) - 1)]

		else :
			if y < 0 :
				for i in range(0, int(round(x)), -1) :
					my_line += [(int(round(i + rayon)) - 1, int(round(coef2*i + rayon)) - 1)]
			else :
				for i in range(0, int(round(x)), -1) :
					my_line += [(int(round(i + rayon)) - 1, int(round(coef2*i + rayon)))]
	return my_line

def get_intersection_with_side(x, y, center_x = imd.Img_Density.CENTER_IMG, center_y = imd.Img_Density.CENTER_IMG) :
	""" Retourne le point d'intersection entre la droite qui passe par le centre de l'image et le point (x,y) 
	et le bord de l'image

	Param :
		- x : int/float : position en x
		- y : int/float : position en y
		- center_x : int/float : centre de l'image en x
		- center_y : int/float : centre de l'image en y
	
	Retour :
		tuple : (x1,y1) : coordonnée du point d'intersection en la droite et les limites de l'image
	""" 
	x -= center_x
	y -= center_y

	length_max = float(imd.Img_Density.CENTER_IMG)

	if abs(x) <= abs(y) :
		y_max = length_max * (-1 if y <= 0 else 1)
		x_max = x*y_max/y
	else :
		x_max = length_max * (-1 if x <= 0 else 1)
		y_max = y*x_max/x

	return (int(round(x_max + center_x)), int(round(y_max + center_y)))

def get_two_lines_around_a_point(x, y) :
	""" Retourne les coordonnées des points des deux droites entourant le point (x,y)

	Param :
		- x : int/float : position en x
		- y : int/float : position en y
		- center_x : int/float : centre de l'image en x
		- center_y : int/float : centre de l'image en y
	
	Retour :
		tuple de list de tuple : (line1, line2) ou line1 = [(x1,y1), (x2,y2), ...] : coordonnée des points de la droite
	"""
	min_x = x - 0.5
	max_x = x + 0.5
	min_y = y - 0.5
	max_y = y + 0.5

	x -= imd.Img_Density.CENTER_IMG
	y -= imd.Img_Density.CENTER_IMG

	line_1 = None
	line_2 = None

	if x <= 0 and y <= 0 or x > 0 and y > 0:
		#coin haut gauche
		point_limit1 = get_intersection_with_side(min_x, max_y)
		point_limit2 = get_intersection_with_side(max_x, min_y)
		line_1 = line(point_limit1[0], point_limit1[1])
		line_2 = line(point_limit2[0], point_limit2[1])
	else :
		#coin bas gauche
		point_limit1 = get_intersection_with_side(min_x, min_y)
		point_limit2 = get_intersection_with_side(max_x, max_y)
		line_1 = line(point_limit1[0], point_limit1[1])
		line_2 = line(point_limit2[0], point_limit2[1])

	return (line_1, line_2)

def get_infos_line(line) :
	""" Retourne les informations utiles sur une ligne line :

	Param :
		line : liste de tuple : [(x1, y1), (x2, y2), ...]

	Retour :
		(char, int) : où char = axe où la droite s'intersecte avec les bords de l'image
	"""
	last = line[-1]
	limit = None
	if last[0] == 0 or last[0] == imd.Img_Density.RAYON_SUB_IMG * 2 - 1 :
		limit = ('x', last[0])
	else :
		limit = ('y', last[1])
	return limit

def points_hidden_behind_point(matrix, x, y) :
	""" Retourne la liste des points cachés par un obstacle en position (x,y),
	du point de vu du centre, dans notre matrix.

	Param :
		- matrix : double list de int (0 ou 1) : représente la matrice 
			de similarité entre deux images 
		- x : int : position en x de l'obstacle
		- y : int : position en y de l'obstacle

	Retour :
		liste de tuple : [(x1, y1), (x2, y2), ...] : ensemble des points 
		caché par l'obstacle en (x,y)
	"""
	(line1, line2) = get_two_lines_around_a_point(x, y)
	limit1 = get_infos_line(line1)
	limit2 = get_infos_line(line2)

	points_hidden = list()

	indice_max = 2* imd.Img_Density.RAYON_SUB_IMG - 1

	if limit1[0] == 'x' and limit2[0] == 'x' :
		if limit1[1] == indice_max and limit2[1] == indice_max :
			# cas les deux limites à droite
			# on ne garde que les points qui dépassent
			line1 = [p for p in line1 if p[0] >= x]
			line2 = [p for p in line2 if p[0] >= x]
		elif limit1[1] == 0 and limit2[1] == 0 :
			# cas les deux limites à gauche
			# on ne garde que les points qui dépassent
			line1 = [p for p in line1 if p[0] <= x]
			line2 = [p for p in line2 if p[0] <= x]

		length = len(line1)
		if length > 0 and line1[0][1] > line2[0][1] :
			#on switch nos deux lignes pour que line1 soit celle la plus
			#proche de l'origine
			tmp = line1
			line1 = line2
			line2 = tmp

		for i in range(length) :
			p = list(line1[i])
			boolean = True
			while boolean :
				#tant que l'on a pas atteint le point équivalent sur l'autre ligne on continue
				if p == list(line2[i]) :
					boolean = False
				if (p[1] >= y and y >= imd.Img_Density.RAYON_SUB_IMG) or (p[1] <= y and y <= imd.Img_Density.RAYON_SUB_IMG) :
					points_hidden += [copy.copy(p)]
				p[1] += 1

	elif limit1[0] == 'y' and limit2[0] == 'y' :
		if limit1[1] == indice_max and limit2[1] == indice_max :
			# cas les deux limites en bas
			# on ne garde que les points qui dépassent
			line1 = [p for p in line1 if p[1] >= y]
			line2 = [p for p in line2 if p[1] >= y]
		elif limit1[1] == 0 and limit2[1] == 0 :
			# cas les deux limites en haut
			# on ne garde que les points qui dépassent
			line1 = [p for p in line1 if p[1] <= y]
			line2 = [p for p in line2 if p[1] <= y]

		length = len(line1)
		if length > 0 and line1[0][0] > line2[0][0] :
			#on switch nos deux lignes pour que line1 soit celle la plus
			#proche de l'origine
			tmp = line1
			line1 = line2
			line2 = tmp

		for i in range(length) :
			p = list(line1[i])
			boolean = True
			while boolean :
				#tant que l'on a pas atteint le point équivalent sur l'autre ligne on continue
				if p == list(line2[i]) :
					boolean = False
				if (p[0] >= x and x >= imd.Img_Density.RAYON_SUB_IMG) or (p[0] <= x and x <= imd.Img_Density.RAYON_SUB_IMG) :
					points_hidden += [copy.copy(p)]
				p[0] += 1

	elif (limit1[0] == 'y' and limit2[0] == 'x') or (limit1[0] == 'x' and limit2[0] == 'y') :
		#on ne prends que les points intéressants de line1
		if limit1[0] == 'x' and limit1[1] == 0 :
			line1 = [p for p in line1 if p[0] < x]
		elif limit1[0] == 'x' and limit1[1] == indice_max :
			line1 = [p for p in line1 if p[0] > x]
		elif limit1[0] == 'y' and limit1[1] == 0 :
			line1 = [p for p in line1 if p[1] < y]
		elif limit1[0] == 'y' and limit1[1] == indice_max :
			line1 = [p for p in line1 if p[1] > y]

		#on ne prends que les points intéressants de line2
		if limit2[0] == 'x' and limit2[1] == 0 :
			line2 = [p for p in line2 if p[0] < x]
		elif limit2[0] == 'x' and limit2[1] == indice_max :
			line2 = [p for p in line2 if p[0] > x]
		elif limit2[0] == 'y' and limit2[1] == 0 :
			line2 = [p for p in line2 if p[1] < y]
		elif limit2[0] == 'y' and limit2[1] == indice_max :
			line2 = [p for p in line2 if p[1] > y]

		for i in range(len(line1)) :
			#on parcours tous les points de line1
			p = list(line1[i])
			while not point_in_line(p, line2) :
				#pour chacun des points, on remonte selon l'autre axe jusqu'à rencontré
				#soit le bord, soit un point de line2
				points_hidden += [copy.copy(p)]
				if limit1[0] == 'x' and limit2[1] == 0 :
					p[1] -= 1
					if p[1] < 0 :
						break
				elif limit1[0] == 'x' and limit2[1] == indice_max :
					p[1] += 1
					if p[1] > indice_max :
						break
				if limit1[0] == 'y' and limit2[1] == 0 :
					p[0] -= 1
					if p[0] < 0 :
						break
				elif limit1[0] == 'y' and limit2[1] == indice_max :
					p[0] += 1
					if p[0] > indice_max :
						break

		for i in range(len(line2)) :
			p = list(line2[i])
			while not point_in_line(p, line1) :
				points_hidden += [copy.copy(p)]
				if limit2[0] == 'x' and limit1[1] == 0 :
					p[1] -= 1
					if p[1] < 0 :
						break
				elif limit2[0] == 'x' and limit1[1] == indice_max :
					p[1] += 1
					if p[1] > indice_max :
						break
				if limit2[0] == 'y' and limit1[1] == 0 :
					p[0] -= 1
					if p[0] < 0 :
						break
				elif limit2[0] == 'y' and limit1[1] == indice_max :
					p[0] += 1
					if p[0] > indice_max :
						break

	return points_hidden

def point_in_line(point, line) :
	""" Retour true si point appartient à line, False sinon

	Param :
		- point : tuple de int : (x, y) : coordonnées du point
		- line : list de tuple : ensemble des points représentant la ligne
	""" 
	for p in line :
		if point[0] == p[0] and point[1] == p[1] :
			return True
	return False

def activate_field_of_view(matrix) :
	""" Etablit un champs de vu du point de vu du centre de l'image (matrix).
	Les obstacles sont les points ayant pour valeur 0 : ces points sont 
	ceux qui ont changé entre les deux images comparés, par conséquent, 
	ceux derrières sont aussi à changer.

	Param :
		- matrix : double liste de int (0 ou 1): représente la matrice de 
			similarité entre deux images
	
	Retour :
		list de tuple : [(x1, y1), (x2, y2), ...] : Ensemble des points 
			non visbile à cause des obstacles
	"""
	center = [int(imd.Img_Density.CENTER_IMG), int(imd.Img_Density.CENTER_IMG)]
	point = [0, 0]
	lim_pos_x = 1
	lim_pos_y = 1
	lim_neg_x = -1
	lim_neg_y = -1

	list_points_hidden = list()

	def end_while(lim_pos_x, lim_pos_y, lim_neg_x, lim_neg_y) :
		return lim_pos_x > imd.Img_Density.RAYON_SUB_IMG and \
			lim_pos_y > imd.Img_Density.RAYON_SUB_IMG and \
			lim_neg_x < -int(imd.Img_Density.CENTER_IMG) and \
			lim_neg_y < -int(imd.Img_Density.CENTER_IMG)

	def fov(matrix, point, center, list_points_hidden) :
		p = [point[0] + center[0], point[1] + center[1]]
		if matrix[p[1]][p[0]] == 0 and point not in list_points_hidden :
			list_points_hidden += points_hidden_behind_point(matrix, p[0], p[1])

	while True :
		#boucle pos x
		while point[0] <= lim_pos_x :
			fov(matrix, point, center, list_points_hidden)
			if point[0] < lim_pos_x :
				point[0] += 1
			else :
				#égalité donc fin du parcours sur cet axe
				break
		lim_pos_x += 1

		#boucle pos y
		while point[1] <= lim_pos_y :
			fov(matrix, point, center, list_points_hidden)
			if point[1] < lim_pos_y :
				point[1] += 1
			else :
				#égalité donc fin du parcours sur cet axe
				break
		lim_pos_y += 1

		#boucle neg x
		while point[0] >= lim_neg_x :
			fov(matrix, point, center, list_points_hidden)
			if point[0] > lim_neg_x :
				point[0] -= 1
			else :
				#égalité donc fin du parcours sur cet axe
				break
		lim_neg_x -= 1

		if end_while(lim_pos_x, lim_pos_y, lim_neg_x, lim_neg_y) :
			break

		#boucle en neg_y
		while point[1] >= lim_neg_y :
			fov(matrix, point, center, list_points_hidden)
			if point[1] > lim_neg_y :
				point[1] -= 1
			else :
				#égalité donc fin du parcours sur cet axe
				break
		lim_neg_y -= 1

	return list_points_hidden
