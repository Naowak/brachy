#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-
from matplotlib import pyplot as plt
import Img_Density as imd
import json
import random

class Data_Work :
	"""Classe effectuant les calculs sur nos données (Img_Density)"""

	def __init__(self, list_Img_Density) :
		"""
		Param :
			list_Img_Density : list de imd.Img_Density

		Une instance possède les attributs :
			- self.imgs : list des images (une pour chaque source)
			- self.clusters : 
			- self.dict_matrix_similarity : dictionnaire de matrice de similarité
					Clé pour une matrice entre l'image indice i et l'image indice j
					tuple (i, j) tel que i < j.
			- self.dict_similarity : dictionnaire de score de similarité
					Clé pour un score entre l'image indice i et l'image indice j
					tuple (i, j) tel que i < j.
		"""
		print("Chargement des images...")
		#self.load_img(list_Img_Density)
		self.create_N_random_img(199)
		print("Calcul des similarités...")
		self.compute_similarity()

		#self.load_similarity()


	# ----------------------------- Travail sur les données ---------------------


	def compute_similarity(self) :
		"""Calcul la similarité entre toutes nos images,
		enregistre les résultats dans self.dict_similarity. enregistre
		aussi la matrice de similarité dans self.dict_matrix_similarity"""

		self.dict_similarity = dict()
		for i in range(len(self.imgs)) :
			for j in range(i+1, len(self.imgs)) :
				matrix_similarity = imd.calcul_matrix_similarity(self.imgs[i], self.imgs[j])
				score_similarity = imd.calcul_similarity(matrix_similarity)
				self.dict_similarity[str((i,j))] = score_similarity

	def define_clusters(self, ind_center_img = 0) :
		""" Utilise l'algorithme des K-means Intelligents pour définirs les clusters.
		Ils seront retourner sous la forme suivante  :
			[[2, 5, 3, 9, 7, 15], [12, 78, 32, 56], [12, 4]]
		Où chaque sous liste est un cluster.
		"""
		self.clusters = []
		nb_imgs = len(self.imgs)
		list_ind_imgs = list(range(nb_imgs))

		ind_center_img = 0
		list_ind_imgs.remove(center_ind)

		while len(list_ind_imgs) > 0 :
			ind_farest_img = find_farest_img(ind_center_img, list_ind_imgs)
			cluster = [ind_farest_img]
			cluster += find_all_img_closest_to_the_farest_img(ind_center_img, ind_farest_img, list_ind_imgs)
			new_representant = self.find_new_representant(cluster)



	def find_farest_img(self, id_img, list_ind_img) :
		""" Retourne l'indice de l'image la plus éloigné de id_img

		Param :
			- id_img : int : indice de l'image pour laquelle on cherche l'image la plus éloigné
			- list_ind_img : list d'indice : Liste des indices correspondants aux images encore
			non attribuées.
		"""
		score_sim_min = 9999999
		farest_img_id = None
		for i in list_ind_img :
				key = find_key(i, id_img)
				score = self.dict_similarity[str(key)]
				if score < score_sim_min :
					score_sim_min = score
					farest_img_id = i

		return farest_img_id

	def find_all_img_closest_to_the_farest_img(self, center_ind, farest_ind, list_ind_img) :
		"""Retourne une liste d'indice des images les plus proches de farest_ind
		que de center_ind.

		Param :
			- center_ind : int : indice de l'image central
			- farest_ind : int : indice de l'image la plus éloignée

		Retour :
			liste d'indice correspondant à toutes les images plus proches de 
			farest_ind que de center_ind
		"""
		cluster = []
		for i in list_ind_img :
			key_center = find_key(center_ind, i)
			key_farest = find_key(farest_ind, i)
			if self.dict_similarity[key_center] < self.dict_similarity[key_farest] :
				#l'image d'indice i a plus de similarité avec farest_ind qu'avec center_ind
				cluster += [i]
		return cluster


	def find_new_representant(self, cluster) :
		"""Trouve parmi le cluster quel est le meilleur représentant de la classe.

		Param :
			- cluster : list indice : liste des indices des images dans le cluster

		retour : int : indice de l'image représentant au mieux le cluster
		"""

		#On cherche l'image qui a la plus grande similarité avec toutes les autres
		# solution : ->>> somme des similarités pour chaque image.

		vector = [0 for _ in range(len(cluster))] 

		for i,ind1 in enumerate(cluster) :
			s = 0
			for ind2 in cluster :
				if ind1 != ind2 :
					key = find_key(ind1, ind2)
					s += self.dict_similarity[key]
			vector[i] = s

		return cluster[vector.index(max(vector))]

		
	# ------------------------ Gestion de sauvegarde -----------------------------
	
	def load_img(self, list_Img_Density) :
		""" Charge les sub_imgs de chaque Img_Density

		Param :
			list_Img_Density : list de imd.Img_Density
		"""
		self.imgs = []
		#On ajoute en premier l'image d'eau, elle nous servira d'image de base
		# --- > origine du repère
		self.imgs.append(create_water_img())

		#On ajoute les autre image 
		for img in list_Img_Density :
			self.imgs += img.sub_imgs[400:600] #on se limite à 200 images pour le test

	def create_N_random_img(self, N) :
		""" Créer N random images pour notre database

		Param :
			N : int : nombre d'image à Créer
		"""
		self.imgs = []
		#On ajoute en premier l'image d'eau, elle nous servira d'image de base
		# --- > origine du repère
		self.imgs.append(create_water_img())
		for _ in range(N) :
			self.imgs += [create_pseudo_random_img()]

	def load_similarity(self, file="s90_data_dist.don") :
		"""Charge les scores de similarité précalculés en enregistrer dans file"""
		with open(file, "r") as f :
			self.dict_similarity = json.load(f)

	def save_similarity(self, file="s90_data_dist.don") :
		"""Enregistre dans un fichier la similarité calculé entre toutes nos images"""
		with open(file, "w+") as f :
			json.dump(self.dict_similarity, f)




# -------------------------- Fonctions utiles -------------------------------------


def find_key(ind1, ind2) :
	"""Retourne la clef permettant d'acceder au score de similarité entre 
	les deux images d'indice ind1 et ind2 dans le dict self.dict_similarity
	"""
	if ind1 < ind2 :
		return str((ind1, ind2))
	return str((ind2, ind1))

def create_water_img() :
	"""Créer une image composée d'eau
	Retour : 
		double list : représente une image composée seulement d'eau
	"""
	size_img = imd.Img_Density.RAYON_SUB_IMG*2
	return [[0 for i in range(size_img)] for j in range(size_img)]


def create_pseudo_random_img() :
	"""Créer des images aléatoires"""
	size_img = imd.Img_Density.RAYON_SUB_IMG*2
	img = [[0 for i in range(size_img)] for j in range(size_img)]
	seuil_elem_1 = 0.0025
	seuil_elem_2 = 0.0050
	proba_propagation = 0.25

	propagation_1 = []
	propagation_2 = []

	for i in range(size_img) :
		for j in range(size_img) :
			r = random.random()
			if r < seuil_elem_1 :
				img[i][j] = 1
				propagation_1 += get_voisin(i, j, size_img)
			elif r < seuil_elem_2 :
				img[i][j] = 2
				propagation_2 += get_voisin(i, j, size_img)

	while len(propagation_1) > 0 :
		r = random.random()
		p = propagation_1.pop()
		if r < proba_propagation :
			img[p[0]][p[1]] = 1
			propagation_1 += get_voisin(p[0], p[1], size_img)

	while len(propagation_2) > 0 :
		r = random.random()
		p = propagation_2.pop()
		if r < proba_propagation :
			img[p[0]][p[1]] = 2
			propagation_2 += get_voisin(p[0], p[1], size_img)

	return img

def get_voisin(i, j, size) :
	""" Retourne les voisins d'un pixels sans dépassé sur les bords

	Param :
		- i : int : indice ordonnee
		- j : int : indice abscisse
		- size : int : taille d'un coté de l'image
	"""
	v = []
	if i - 1 >= 0 :
		v.append((i-1, j))
	if j - 1 >= 0 :
		v.append((i, j-1))
	if i + 1 < size :
		v.append((i+1, j))
	if j + 1 < size :
		v.append((i, j+1))
	return v




# --------------------------- Main ----------------------------------------


if __name__ == "__main__" :
	density_file = "../../working_dir/slice_090/densite_lu/densite_hu.don"
	config_file = "../../working_dir/slice_090/densite_lu/config_KIDS.don"

	dw = Data_Work(None)

	list_ind_img = list(range(200))
	list_ind_img.remove(0)
	ind_farest = dw.find_farest_img(0, list_ind_img)
	print(ind_farest)
	list_ind_img.remove(ind_farest)
	cluster = dw.find_all_img_closest_to_the_farest_img(0, ind_farest, list_ind_img) + [ind_farest]
	print(cluster)
	new_representant = dw.find_new_representant(cluster)
	print(new_representant)

	for ind in cluster :
		plt.imshow(dw.imgs[ind])
		plt.show()


	# fig = plt.figure()
	# for i in range(20) :
	# 	fig.add_subplot(4, 5, i+1)
	# 	plt.imshow(dw.imgs[i])
	# plt.show()

	# img_den = imd.Img_Density(density_file, config_file)
	# dw = Data_Work([img_den])

	# ind = dw.find_farest_img(0)

	# fig = plt.figure()
	# fig.add_subplot(1, 2, 1)
	# plt.imshow(dw.imgs[ind])
	# fig.add_subplot(1, 2, 2)
	# plt.imshow(dw.imgs[0])
	# plt.show()
	# with open("s90_data_dist.don", "w+") as f :
	# 	json.dump(dw.dict_similarity, f)


