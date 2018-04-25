#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-
from matplotlib import pyplot as plt
import math
import random

class Img_Density :
	"""Classe représentant une image de densité quantifier
	 en M différentes matières. L'image est obtenu à partir 
	 du fichier densite_hu.don calculé par cythi, qui représente
	 la zone d'influence à calculer.
	 Nous récupérons aussi la position des sources dans config_KIDS.don"""

	RAYON_SUB_IMG = 10
	CENTER_IMG = RAYON_SUB_IMG - 0.5

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
	 	#On charge l'image
	 	self.load_img_density(density_file)
	 	#On charge les sources
	 	self.load_sources(config_file)
	 	self.extract_material_from_density([120, 200])
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
				if "volume_sphere" in line :
					tab = line.split(" ")
					self.sources += [(int(round(float(tab[2]))), int(round(float(tab[3]))))]

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
		#rayon = min([source[0] for source in self.sources])
		rayon = self.RAYON_SUB_IMG
		
		self.sub_imgs = list()
		for source in self.sources :
			s_ord = source[1]
			s_abs = source[0]
			sub_ord = self.img_material[s_ord - rayon: s_ord + rayon]
			sub_img = [tmp[s_abs - rayon : s_abs + rayon] for tmp in sub_ord]
			self.sub_imgs += [sub_img]


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
			plt.imshow(sub_img)
			plt.show()

# ---------------------- Fonction -------------------

def calcul_matrix_similarity(img1, img2) :
	"""Calcul la matrice de similarité entre deux matrices

	Param :
		- img1, img2 : Une matrice de matériaux : ici une sub_img

	Retour :
		- Retourne la matrice de similarité entre les deux images"""
	size = 2*Img_Density.RAYON_SUB_IMG
	return [[1 if img1[i][j]==img2[i][j] else 0 for j in range(size)] for i in range(size)]



# def activate_filed_of_view(matrix) :
# 	""" Permet à une matrice de similarité de prendre en compte le champs de vu
# 	En effet, les voxels espacé par un 0 avec la source ne doit pas être égal à 1
# 	mais à 0.

# 	Param : 
# 		- matrix : matrice de similarité
# 	"""
# 	size = 2*Img_Density.RAYON_SUB_IMG
# 	# new = [list(ligne) for ligne in matrix]
# 	new = [[0 for i in range(size)] for j in range(size)]

# 	def visit(x, y) :
# 		if x >= 0 and y >= 0 and x < size and y < size :
# 			if matrix[y][x] != 0 :
# 				new[y][x] = 1

# 	def tileblocked(x, y) :
# 		if x >= 0 and y >= 0 and x < size and y < size :
# 			return matrix[y][x] == 0

# 	def visit_2(x, y) :
# 		if x >= 0 and y >= 0 and x < size and y < size :
# 			if matrix[y][x] != 0 :
# 				new[y][x] = 1
# 				return False
# 			else :
# 				return True


# 	#fov.fieldOfView(10, 10, 20, 20, 10, visit, tileblocked)
# 	fov.fov(10, 10, 15, visit_2)
# 	return new



	

def calcul_similarity(matrix_similarity, filtre=None) :
	""" Calcul le score de similarité entre deux matrices.

	Param :
		- matrix_similarity : Matrice de similarité entre les deux matrices
				pour lesquelles on souhaite calculer le score.
		- filtre : String : ["gaussien", "proportionnel", "lineaire"]

	Retour :
		- int : score de similarité
	"""
	size = 2*Img_Density.RAYON_SUB_IMG
	res = 0
	for j in range(size) :
		for i in range(size) :
			if matrix_similarity[j][i] == 1 :
				#Dans le cas où les deux pixels sont égaux
				tmp = 1
				try :
					if j-1 >= 0 and matrix_similarity[j-1][i] == 1 :
						tmp += 1
				except IndexError :
					pass
				try :
					if i-1 >= 0 and matrix_similarity[j][i-1] == 1 :
						tmp += 1
				except IndexError :
					pass
				try :
					if matrix_similarity[j+1][i] == 1 :
						tmp += 1
				except IndexError :
					pass
				try :
					if matrix_similarity[j][i+1] == 1 :
						tmp += 1
				except IndexError :
					pass
				if filtre == None :
					res += tmp
				elif filtre == "gaussien" :
					res += tmp*gaussienne(i, j, 20)
				elif filtre == "proportionnel" :
					res += tmp*proportionnelle(i,j)
	return res

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
	rayon = Img_Density.RAYON_SUB_IMG
	x0 = rayon
	y0 = rayon
	x -= x0
	y -= y0
	return math.exp(-(pow(x,2)/(float(2*var)) + pow(y,2)/(float(2*var))))

def proportionnelle(x, y) :
	rayon = float(Img_Density.RAYON_SUB_IMG)
	x0 = rayon 
	y0 = rayon 
	x -= x0
	y -= y0
	x = float(x)
	y = float(y)
	return math.sqrt(pow(x/rayon,2) + pow(y/rayon, 2))

def line(x, y, center_x = Img_Density.CENTER_IMG, center_y = Img_Density.CENTER_IMG) :
	#longueur en x
	x -= center_x
	#longueur en y
	y -= center_y
	rayon = Img_Density.RAYON_SUB_IMG

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

def get_intersection_with_side(x, y, center_x = Img_Density.CENTER_IMG, center_y = Img_Density.CENTER_IMG) :
	x -= center_x
	y -= center_y

	length_max = float(Img_Density.CENTER_IMG)

	if abs(x) <= abs(y) :
		y_max = length_max * (-1 if y <= 0 else 1)
		x_max = x*y_max/y
	else :
		x_max = length_max * (-1 if x <= 0 else 1)
		y_max = y*x_max/x

	return (int(round(x_max + center_x)), int(round(y_max + center_y)))


def get_two_lines_around_a_point(x, y) :
	min_x = x - 0.5
	max_x = x + 0.5
	min_y = y - 0.5
	max_y = y + 0.5

	x -= Img_Density.CENTER_IMG
	y -= Img_Density.CENTER_IMG

	line_1 = None
	line_2 = None

	if x <= 0 and y <= 0 or x > 0 and y > 0:
		#coin haut gauche
		point_limit1 = get_intersection_with_side(min_x, max_y)
		point_limit2 = get_intersection_with_side(max_x, min_y)
		print(point_limit1, point_limit2)
		line_1 = line(point_limit1[0], point_limit1[1])
		line_2 = line(point_limit2[0], point_limit2[1])
	else :
		#coin bas gauche
		point_limit1 = get_intersection_with_side(min_x, min_y)
		point_limit2 = get_intersection_with_side(max_x, max_y)
		print(point_limit1, point_limit2)
		line_1 = line(point_limit1[0], point_limit1[1])
		line_2 = line(point_limit2[0], point_limit2[1])

	return (line_1, line_2)


# ----------------------- Main -----------------------

if __name__ == "__main__" :
	density_file = "../../working_dir/slice_092/densite_lu/densite_hu.don"
	config_file = "../../working_dir/slice_092/densite_lu/config_KIDS.don"


	# var = 20
	# # m = [[proportionnelle(i,j) for i in range(20)] for j in range(20)]
	# # print(m)
	# # plt.plot(m)
	# # plt.show()

	# m = [[1 for i in range(20)] for i in range(20)]
	# list_points = [(17, 7), (17,13)]
	# for point in list_points :
	# 	lines = get_two_lines_around_a_point(point[0], point[1])
	# 	for l in lines :
	# 		print(l)
	# 		for p in l :
	# 			m[p[1]][p[0]] = 0
	# 	m[point[1]][point[0]] = 2


	# p2 = (-10,-10)
	# l = line(p2[0], p2[1])
	# for p in l :
	# 	print(p)
	# 	try :
	# 		m[p[1]-10][p[0]-10] = 0
	# 	except IndexError :
	# 		pass

	# coords = list(range(20))
	# for _ in range(10) :
	# 	x = random.choice(coords)
	# 	y = random.choice(coords)
	# 	m[y][x] = 0
	# fig = plt.figure()
	# fig.add_subplot(1, 2, 1)
	# plt.imshow(m)
	# m = activate_filed_of_view(m)
	# fig.add_subplot(1, 2, 2)
	# plt.imshow(m)
	# plt.show(m)
	# print(m)

	img = Img_Density(density_file, config_file)
	img.show_imgs()
	img.show_sub_imgs()
	# sub_img1 = img.sub_imgs[0]
	# sub_img2 = img.sub_imgs[1]
	# sub_img3 = img.sub_imgs[2]

	# matrix_sim1_3 = calcul_matrix_similarity(sub_img1, sub_img3)
	# matrix_sim2_3 = calcul_matrix_similarity(sub_img2, sub_img3)

	# fig = plt.figure()
	# fig.add_subplot(3, 1, 1)
	# plt.imshow(sub_img1)
	# fig.add_subplot(3, 1, 2)
	# plt.imshow(sub_img2)
	# fig.add_subplot(3, 1, 3)
	# plt.imshow(sub_img3)

	# plt.show()

	# print(calcul_similarity(matrix_sim1_3), calcul_similarity(matrix_sim2_3))