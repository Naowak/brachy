#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-
from matplotlib import pyplot as plt
import Img_Density as imd
import json
import random
import numpy as np
import sys
import time 

class Data_Work :
	"""Classe effectuant les calculs sur nos données (Img_Density)"""

	NB_IMG = 2000

	def __init__(self, list_Img_Density, filtre=None) :
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
		self.filtre = filtre
		self.maximum_similarity = imd.max_score_similarity(imd.Img_Density.RAYON_SUB_IMG*2, filtre)
		self.seuil_min_similarity = self.maximum_similarity*0.9

		print("Chargement des images...")
		#self.load_img_from_list_Img_Density(list_Img_Density)
		self.create_N_random_img(self.NB_IMG)
		print("Calcul des similarités...")
		self.compute_similarity()
		print("Calcul des clusters...")
		self.recursive_intelligent_k_means()
		print("Clusters : ", self.clusters)
		#print(self.ind_img_not_managed)
		self.display_stats()
		#self.display_clusters()

		#self.load_similarity()


	# ----------------------------- Travail sur les données : Prédiction -----------------------

	def calcul_similarity_with_all_center_cluster(self, img) :
		"""Retourne un dictionnaire contenant les simiarités avec tous les autres clusters.
		La clef est l'indice du représentant du cluster

		Param :
			-img : list double dimension: l'image
		"""
		dict_sim = {}
		for (center, cluster) in self.clusters :
			m = imd.calcul_matrix_similarity(self.imgs[center], img)
			dict_sim[center] = imd.calcul_similarity(m, self.filtre)
		return dict_sim


	def predict_closest_img(self, img) :
		""" Prédit l'image la plus proche dans notre base de données et la retourne.

		Param : 
			- img : double list : l'image pour laquelle on souhaite trouver son homologue

		Retour :
			- double list : image trouvée
		"""
		dict_sim = self.calcul_similarity_with_all_center_cluster(img)
		# print("Dict_sim center : \n" + str(dict_sim))
		sim_max = 0
		center_max = None
		for center, sim in dict_sim.items() :
			if sim > sim_max :
				sim_max = sim
				center_max = center
		# print("Sim max : " + str(sim_max))
		# print("Center max : " + str(center_max))

		cluster_max = None
		for center, cluster in self.clusters :
			if center == center_max :
				cluster_max = cluster
		# print("Cluster max : " + str(cluster_max))

		dict_sim_img = {}
		for ind_img in cluster_max :
			m = imd.calcul_matrix_similarity(self.imgs[ind_img], img)
			dict_sim_img[ind_img] = imd.calcul_similarity(m, self.filtre)
		# print("Dict_sim img in cluster : \n" + str(dict_sim_img))


		sim_max = 0
		ind_img_max = None
		for ind_img, sim in dict_sim_img.items() :
			if sim > sim_max :
				sim_max = sim
				ind_img_max = ind_img
		#print("Méthode prédiction : ")
		#print("Image Max : " + str(ind_img_max))
		print("Sim max : " + str(sim_max))
		#print("\n")

		return self.imgs[ind_img_max]


	# ----------------------------- Travail sur les données : Entrainement ---------------------


	def compute_similarity(self) :
		"""Calcul la similarité entre toutes nos images,
		enregistre les résultats dans self.dict_similarity. enregistre
		aussi la matrice de similarité dans self.dict_matrix_similarity"""

		self.dict_similarity = dict()
		for i in range(self.NB_IMG) :
			for j in range(i+1, self.NB_IMG) :
				matrix_similarity = imd.calcul_matrix_similarity(self.imgs[i], self.imgs[j])
				score_similarity = imd.calcul_similarity(matrix_similarity, self.filtre)
				self.dict_similarity[str((i,j))] = score_similarity

	def recursive_intelligent_k_means(self) :
		""" Lance récursivement la méthode des k_means intelligent sur les groupes 
		non attribués et sur les groupes trop gros."""
		self.clusters = []
		list_ind_imgs = list(range(self.NB_IMG))
		self.intelligent_k_means(list_ind_imgs)

		old_ind_img_not_managed = None
		while(old_ind_img_not_managed != self.ind_img_not_managed) :
			old_ind_img_not_managed = list(self.ind_img_not_managed)
			self.intelligent_k_means(self.ind_img_not_managed)

		self.create_clusters_with_img_not_managed()


	def intelligent_k_means(self, list_ind_imgs) :
		""" Utilise la méthode des k_means intelligent pour trier nos données
		en différents clusters.

		Param :	
			- list_ind_imgs : list de int : liste des indices de nos images à trier
		"""
		ind_center_img = self.find_new_representant(list_ind_imgs)
		list_ind_imgs.remove(ind_center_img)
		self.define_intelligent_clusters(ind_center_img, list_ind_imgs)

		list_ind_imgs = self.remove_singleton_cluster()
		list_ind_imgs.append(ind_center_img)
		centers_clusters = [elem[0] for elem in self.clusters]

		ind_img_managed = []
		for ind_img in list_ind_imgs :
			(center, score_sim) = self.find_closest_cluster_for_an_img(ind_img, centers_clusters)
			if score_sim >= self.seuil_min_similarity :
				#Si on a une similarité minimum, on ajoute l'image au cluster
				self.add_img_to_cluster(center, ind_img)
				ind_img_managed += [ind_img]

		self.ind_img_not_managed = [i for i in list_ind_imgs if i not in ind_img_managed]


	def add_img_to_cluster(self, center_cluster, ind_img) :
		""" Ajoute au cluster représenter par center_cluster l'image ind_img.

		Param :
			- center_cluster : int : indice de l'image représentant le cluster
			- ind_img : int : indice de l'image à ajouter dans le cluster

		"""
		for (center, cluster) in self.clusters :
			if center == center_cluster :
				cluster.append(ind_img)


	def create_clusters_with_img_not_managed(self) :
		"""Ajoute les self.ind_img_not_managed en tant que cluster singleton dans self.clusters"""
		for ind_img in self.ind_img_not_managed :
			self.clusters.append((ind_img, [ind_img]))
		self.ind_img_not_managed = []


	def find_closest_cluster_for_an_img(self, ind_img, centers_clusters) :
		""" Trouve le cluster ayant le centre le plus proche de ind_img.

		Param :
			- ind_img : int : indice de l'image
			- centers_clusters : indice des images étant les centres de nos clusters

		Retour :
			- tuple : (c, sim_min)
				- c : int : indice du centre le plus proche
				- sim_min : int : score de similarité du centre le plus proches
		""" 
		sim_max = 0
		c = None
		for center in centers_clusters :
			key = find_key(ind_img, center)
			score_sim = self.dict_similarity[key]
			if score_sim > sim_max :
				c = center
				sim_max = score_sim
		return (c, sim_max)

	def remove_singleton_cluster(self) :
		""" Supprime de self.cluster tous les clusters ne possèdant qu'un element.

		Retour :
			La liste des indices des images étant dans des clusters singletons 
		"""
		list_ind_imgs_not_in_cluster = []

		for (representant_cluster, cluster) in self.clusters :
			if len(cluster) == 1 :
				#Un seul élément dans le cluster, on en veut pas.
				list_ind_imgs_not_in_cluster += [representant_cluster]
				#vu qu'il n'y a qu'un seul élément, il n'y a que le représentant

		self.clusters = [elem for elem in self.clusters if elem[0] not in list_ind_imgs_not_in_cluster]
		return list_ind_imgs_not_in_cluster


	def define_intelligent_clusters(self, ind_center_img, list_ind_imgs) :
		""" Utilise l'algorithme des K-means Intelligents pour définirs les clusters.
		Ils seront retourner sous la forme suivante  :
			[(centre, [2, 5, 3, 9, 7, 15]), (centre, [12, 78, 32, 56], [12, 4])]
		Où chaque sous liste est un cluster.
		"""

		while len(list_ind_imgs) > 0 :
			(representant, cluster) = self.find_one_cluster(ind_center_img, list_ind_imgs)
			list_ind_imgs = [elem for elem in list_ind_imgs if elem not in cluster]
			self.clusters += [(representant, cluster)]


	def find_one_cluster(self, ind_center_img, list_ind_imgs) :
		"""Trouve le cluster le plus éloigné avec l'algo des K-Means Intelligent

		Retour : 
			- (int, [int, int ..., int]) : (représentant du cluster, cluster)"""
		old_cluster = list()
		representant_cluster = self.find_farest_img_from_center(ind_center_img, list_ind_imgs)
		cluster = self.find_all_img_closest_to_representant_than_center(ind_center_img, representant_cluster, list_ind_imgs) + [representant_cluster]

		while(not are_clusters_equal(old_cluster, cluster)) :
			#Si le représentant change, on recalcule le cluster
			representant_cluster = self.find_new_representant(cluster)
			old_cluster = cluster
			cluster = self.find_all_img_closest_to_representant_than_center(ind_center_img, representant_cluster, list_ind_imgs) + [representant_cluster]

		return (representant_cluster, cluster)


	def find_farest_img_from_center(self, id_center_img, list_ind_img) :
		""" Retourne l'indice de l'image la plus éloigné de id_center_img

		Param :
			- id_center_img : int : indice de l'image pour laquelle on cherche l'image la plus éloigné
			- list_ind_img : list d'indice : Liste des indices correspondants aux images encore
			non attribuées.
		"""
		score_sim_min = 9999999
		farest_img_id = None
		for i in list_ind_img :
			if i != id_center_img :	
				key = find_key(i, id_center_img)
				score = self.dict_similarity[str(key)]
				if score < score_sim_min :
					score_sim_min = score
					farest_img_id = i

		return farest_img_id

	def find_all_img_closest_to_representant_than_center(self, center_ind, representant_ind, list_ind_img) :
		"""Retourne une liste d'indice des images les plus proches de representant_ind
		que de center_ind.

		Param :
			- center_ind : int : indice de l'image central
			- representant_ind : int : indice de l'image la plus éloignée

		Retour :
			liste d'indice correspondant à toutes les images plus proches de 
			representant_ind que de center_ind
		"""
		cluster = []
		for i in list_ind_img :
			if i != center_ind and i != representant_ind :
				key_center = find_key(center_ind, i)
				key_representant = find_key(representant_ind, i)
				if self.dict_similarity[key_center] <= self.dict_similarity[key_representant] :
					#l'image d'indice i a plus de similarité avec representant_ind qu'avec center_ind
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


	# ------------------------ Display -----------------------------------

	def plot_clusters(self) :
		for (representant, cluster) in self.clusters :
			taille = len(cluster)
			X = 15
			Y = taille/X
			if taille%X > 0 :
				Y += 1
			fig = plt.figure()
			for i,ind in enumerate(cluster) :
				fig.add_subplot(Y, X, i+1)
				plt.imshow(self.imgs[ind])
		plt.show()

	def display_stats(self) :
		nb_imgs_not_managed = len(self.ind_img_not_managed)
		nb_imgs_managed = self.NB_IMG - nb_imgs_not_managed
		pourcentage_managed = (float(nb_imgs_managed) / float(self.NB_IMG))*100
		pourcentage_not_managed = (float(nb_imgs_not_managed) / float(self.NB_IMG))*100
		nb_clusters = len(self.clusters)
		mean_cluster_size = np.mean([len(c[1]) for c in self.clusters])
		rapport_sn = (mean_cluster_size/float(self.NB_IMG))*100
		
		print("Nombre d'images traitées (N): " + str(self.NB_IMG))
		print("Nombre d'images associées : " + str(nb_imgs_managed) + " -----> " + str(pourcentage_managed) + "%")
		print("Nombre d'images non associées : " + str(nb_imgs_not_managed) + " -----> " + str(pourcentage_not_managed) + "%")
		print("Nombre de clusters : " + str(nb_clusters))
		print("Taille moyenne cluster (S): " + str(mean_cluster_size))
		print("Rapport S/N : " +  str(rapport_sn) + "%")

	def display_clusters(self) :
		print("Clusters :")
		for center, cluster in self.clusters :
			print(str(center) + " -----> " + str(cluster))

		
	# ------------------------ Gestion de sauvegarde -----------------------------
	
	def load_img_from_list_Img_Density(self, list_Img_Density) :
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
			self.imgs += img.sub_imgs[:self.NB_IMG] 

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
	"""Créer et retourne une image aléatoire"""
	size_img = imd.Img_Density.RAYON_SUB_IMG*2
	img = [[0 for i in range(size_img)] for j in range(size_img)]
	seuil_elem_1 = 0.0025
	seuil_elem_2 = 0.0050
	proba_propagation = 0.4

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
		if img[p[0]][p[1]] == 0 and r < proba_propagation :
			img[p[0]][p[1]] = 1
			propagation_1 += get_voisin(p[0], p[1], size_img)

	while len(propagation_2) > 0 :
		r = random.random()
		p = propagation_2.pop()
		if img[p[0]][p[1]] == 0 and r < proba_propagation :
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

def are_clusters_equal(cluster1, cluster2) :
	""" Retourne True si les deux clusters sont égaux,
		False sinon

		Param :
			- cluster1 : list int : liste d'indice représentant le premier cluster
			- cluster2 : list int : liste d'indice représentant le second cluster
	"""
	return set(cluster1) == set(cluster2)




# --------------------------- Main ----------------------------------------


if __name__ == "__main__" :
	density_file = "./working_dir/slice_090/densite_lu/densite_hu.don"
	config_file = "./working_dir/slice_090/densite_lu/config_KIDS.don"

	filtre = None
	if len(sys.argv) > 1 :
		filtre = sys.argv[1]

	dw = Data_Work(None, filtre)

	nb_img = 10
	my_imgs = [create_pseudo_random_img() for _ in range(nb_img)]
	time_begin_predict = time.time()
	my_results = [dw.predict_closest_img(my_imgs[i]) for i in range(nb_img)]
	time_end_predict = time.time()
	naiv_results = []

	print(" -------- ")

	time_begin_find = time.time()
	for img in my_imgs :
		indice_max = None
		sim_max = 0
		for i in range(dw.NB_IMG) :
			m = imd.calcul_matrix_similarity(img, dw.imgs[i])
			sim = imd.calcul_similarity(m, filtre)
			if sim > sim_max :
				sim_max = sim 
				indice_max = i
		naiv_results += [dw.imgs[indice_max]]
		# print("Méthode full")
		# print("Meilleur image : " + str(indice_max))
		print("Max sim : " + str(sim_max))
		# print("\n")
	time_end_find = time.time()

	print("Temps prédiction : " + str(time_end_predict - time_begin_predict))
	print("Temps recherche : " + str(time_end_find - time_begin_find))

	fig = plt.figure()
	for i in range(nb_img) :		
		indice = i + 1
		sp1 = fig.add_subplot(nb_img, 3, 3*indice - 2)
		# sp1.title.set_text(str(indice))
		plt.imshow(my_imgs[i])

		sp2 = fig.add_subplot(nb_img, 3, 3*indice - 1)
		# sp2.title.set_text(str(indice))
		plt.imshow(my_results[i])

		sp3 = fig.add_subplot(nb_img, 3, 3*indice)
		# sp3.title.set_text(str(indice))
		plt.imshow(naiv_results[i])

	plt.show()

	# list_ind_img = list(range(200))
	# list_ind_img.remove(0)
	# ind_farest = dw.find_farest_img_from_center(0, list_ind_img)
	# list_ind_img.remove(ind_farest)
	# cluster = dw.find_all_img_closest_to_representant_than_center(0, ind_farest, list_ind_img) + [ind_farest]
	# new_representant = dw.find_new_representant(cluster)
	# print(cluster)
	# cluster = dw.find_all_img_closest_to_representant_than_center(0, new_representant, list_ind_img) + []

	# nb_imgs = len(dw.imgs)
	# list_ind_img = list(range(nb_imgs))
	# ind_img_center = 0
	# (center_cluster, cluster) = dw.find_one_cluster(ind_img_center, list_ind_img)
	# print(center_cluster, cluster)

	# for ind in cluster :
	# 	plt.imshow(dw.imgs[ind])
	# 	plt.show()


	# fig = plt.figure()
	# for i in range(60) :
	# 	sp = fig.add_subplot(4, 15, i+1)
	# 	if not i in dw.ind_img_not_managed :
	# 		sp.title.set_text(str(i))
	# 	plt.imshow(dw.imgs[i])
	# plt.show()

	#img_den = imd.Img_Density(density_file, config_file)
	# dw = Data_Work([None])

	# ind = dw.find_farest_img_from_center(0)

	# fig = plt.figure()
	# fig.add_subplot(1, 2, 1)
	# plt.imshow(dw.imgs[ind])
	# fig.add_subplot(1, 2, 2)
	# plt.imshow(dw.imgs[0])
	# plt.show()
	# with open("s90_data_dist.don", "w+") as f :
	# 	json.dump(dw.dict_similarity, f)


