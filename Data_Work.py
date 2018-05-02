#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-
from matplotlib import pyplot as plt
import Img_Density as imd
import Similarity as simy
import json
import random
import numpy as np
import sys
import time 
import os
import copy

class Data_Work :
	"""Classe effectuant les calculs sur nos données (Img_Density)"""


	NB_IMG = 500
	NB_SIMS = NB_IMG*(NB_IMG+1)/2
	NB_TEST = 15
	NB_MAX_ELEM_IN_CLUSTER = 20

	def __init__(self, list_Img_Density, filtre=None) :
		"""
		Param :
			list_Img_Density : list de imd.Img_Density

		Une instance possède les attributs :
			- self.learn_imgs : list des images (une pour chaque source)
			- self.clusters : 
			- self.dict_matrix_similarity : dictionnaire de matrice de similarité
					Clé pour une matrice entre l'image indice i et l'image indice j
					tuple (i, j) tel que i < j.
			- self.tab_similarity : dictionnaire de score de similarité
					Clé pour un score entre l'image indice i et l'image indice j
					tuple (i, j) tel que i < j.
		"""
		self.filtre = filtre
		self.maximum_similarity = simy.max_score_similarity(imd.Img_Density.RAYON_SUB_IMG*2, filtre)
		self.seuil_min_similarity = self.maximum_similarity*0.9
		self.list_Img_Density = list_Img_Density

	# ----------------------------- Fonction tâche principale ----------------------------------

	def load_from_saved_data(self, directory) :
		""" Param : directory : string du path du repertoire de la forme :
				directory :
					- test_imgs/
					- learn_imgs/
		"""
		self.learn_imgs = self.load_imgs_in_files(directory + "learn_imgs/")
		self.test_imgs = self.load_imgs_in_files(directory + "test_imgs/")
		self.NB_IMG = len(self.learn_imgs)
		self.NB_TEST = len(self.test_imgs)

	def load_from_img_density(self, list_Img_Density, all_imgs = False) :
		self.load_img_from_list_Img_Density(list_Img_Density, all_imgs)
		self.extract_N_samples_for_test()

	def load_new_random_imgs(self, nb_learning_imgs = NB_IMG, nb_testing_imgs = NB_TEST) :
		self.create_N_random_img(nb_learning_imgs)
		self.create_N_random_img_for_test(nb_testing_imgs)

	def load_imgs_and_similarity(self, how, param) :
		if how == "saved_data" and param["directory"]:
			directory = param["directory"]
			self.load_from_saved_data(directory)
			self.load_similarity()

		elif how == "img_density" and param["list_Img_Density"] :
			try :
				all_imgs = param["all_imgs"]
			except :
				all_imgs = False
			self.load_from_img_density(param["list_Img_Density"], all_imgs)
			self.compute_similarity()

		elif how == "random_img" :
			self.load_new_random_imgs()
			self.compute_similarity()

	def save_data(self) :
		print("Enregistrement des données dans ./data/ ...")
		self.save_imgs_in_files(self.learn_imgs, "./data/learn_imgs/")
		self.save_imgs_in_files(self.test_imgs, "./data/test_imgs/")
		self.save_similarity()

	def train(self) :
		print("Chargement des images et similarité...")
		self.load_imgs_and_similarity("saved_data", {"directory" : "data/"})
		# self.load_imgs_and_similarity("img_density", {"list_Img_Density" : self.list_Img_Density, "all_imgs" : True})
		# self.load_imgs_and_similarity("random_img", {})
		print("Classification de nos données...")
		list_ind_imgs = list(range(self.NB_IMG))
		self.clusters = self.recursive_intelligent_k_means(list_ind_imgs)
		print("Fin entrainement :")
		self.display_stats()

	def test(self, plot = False) :
		print(" -------- ")
		print("Prédiction sur nos données...")
		nb_img = len(self.test_imgs)

		print("Résultats prédictions")
		time_begin_predict = time.time()
		my_results = [self.predict_closest_img(self.test_imgs[i], self.clusters) for i in range(nb_img)]
		time_end_predict = time.time()
		naiv_results = []

		print("Résultats naifs")
		time_begin_find = time.time()
		for cpt, img in enumerate(self.test_imgs) :
			indice_max = None
			sim_max = 0
			for i in range(self.NB_IMG) :
				sim = simy.similarity_between_two_imgs(img, self.learn_imgs[i], filtre)
				if sim > sim_max :
					sim_max = sim 
					indice_max = i
			naiv_results += [self.learn_imgs[indice_max]]
			print(str(cpt) + " - Sim Max : " + str(sim_max))
		time_end_find = time.time()

		print("Temps prédiction : " + str(time_end_predict - time_begin_predict))
		print("Temps recherche : " + str(time_end_find - time_begin_find))

		if plot :
			fig = plt.figure()
			for i in range(nb_img) :		
				indice = i + 1
				sp1 = fig.add_subplot(nb_img, 4, 4*indice - 3)
				# sp1.title.set_text(str(indice))
				plt.imshow(my_imgs[i])

				sp2 = fig.add_subplot(nb_img, 4, 4*indice - 2)
				# sp2.title.set_text(str(indice))
				plt.imshow(my_results[i])

				sp3 = fig.add_subplot(nb_img, 4, 4*indice - 1)
				# sp3.title.set_text(str(indice))
				plt.imshow(naiv_results[i])

				sp4 = fig.add_subplot(nb_img, 4, 4*indice)
				ms = simy.calcul_matrix_similarity(my_imgs[i], my_results[i])
				hidden_points = simy.activate_field_of_view(ms)
				for p in hidden_points :
					ms[p[1]][p[0]] = 0
				plt.imshow(ms)

			plt.show()

	# ----------------------------- Travail sur les données : Prédiction -----------------------

	def calcul_similarity_with_all_center_cluster(self, img, my_clusters) :
		"""Retourne un dictionnaire contenant les simiarités avec tous les autres clusters.
		La clef est l'indice du représentant du cluster

		Param :
			-img : list double dimension: l'image
		"""
		dict_sim = {}
		for (center, cluster) in my_clusters :
			dict_sim[center] = simy.similarity_between_two_imgs(self.learn_imgs[center], img, self.filtre)
		return dict_sim


	def predict_closest_img(self, img, my_clusters) :
		""" Prédit l'image la plus proche dans notre base de données et la retourne.

		Param : 
			- img : double list : l'image pour laquelle on souhaite trouver son homologue

		Retour :
			- double list : image trouvée
		"""
		#on récupère le centre le représentant le plus proche de img
		dict_sim = self.calcul_similarity_with_all_center_cluster(img, my_clusters)
		sim_max = 0
		center_max = None
		for center, sim in dict_sim.items() :
			if sim > sim_max :
				sim_max = sim
				center_max = center

		#on cherche le cluster associé
		cluster_max = None
		for center, cluster in my_clusters :
			if center == center_max :
				cluster_max = cluster

		if isinstance(cluster_max[0], tuple) :
			#on a une liste de cluster imbriqué dans ce cluster
			return self.predict_closest_img(img, cluster_max)
		else :
			#on est dans un cluster ne possèdant que des images uniques
			#on calcule la similarité entre les images du clusters et la notre
			dict_sim_img = {}
			for ind_img in cluster_max :
				dict_sim_img[ind_img] = simy.similarity_between_two_imgs(self.learn_imgs[ind_img], img, self.filtre)

			#on retourne l'image avec la plus grosse similarité
			sim_max = 0
			ind_img_max = None
			for ind_img, sim in dict_sim_img.items() :
				if sim > sim_max :
					sim_max = sim
					ind_img_max = ind_img
			print("Sim max : " + str(sim_max))

			return self.learn_imgs[ind_img_max]

	# ----------------------------- Travail sur les données : Entrainement ---------------------

	def compute_similarity(self) :
		"""Calcul la similarité entre toutes nos images,
		enregistre les résultats dans self.tab_similarity. enregistre
		aussi la matrice de similarité dans self.dict_matrix_similarity"""

		self.tab_similarity = list()
		cpt = 0

		for i in range(self.NB_IMG) :
			self.tab_similarity += [list()]
			#temporaire dans le cas ou on prends toutes nos images il faut recalculer
			self.NB_SIMS = (self.NB_IMG * (self.NB_IMG + 1))/2
			avancement_pourcentage = float(float(cpt) / float(self.NB_SIMS) * 100)
			avancement_pourcentage = float(int(avancement_pourcentage*100))/100
			print(str(avancement_pourcentage) + "%")
			for j in range(i+1, self.NB_IMG) :
				self.tab_similarity[i] += [simy.similarity_between_two_imgs(self.learn_imgs[i], self.learn_imgs[j], self.filtre)]
				cpt += 1

	def recursive_intelligent_k_means(self, list_ind_imgs) :
		""" Lance récursivement la méthode des k_means intelligent sur les groupes 
		non attribués et sur les groupes trop gros."""
		nb_imgs = len(list_ind_imgs)
		my_clusters = []
		my_clusters = self.intelligent_k_means(list_ind_imgs, my_clusters)
		old_ind_img_not_managed = list()
		while(set(old_ind_img_not_managed) != set(self.ind_img_not_managed)) :
			old_ind_img_not_managed = list(self.ind_img_not_managed)
			my_clusters = self.intelligent_k_means(self.ind_img_not_managed, my_clusters)
		self.create_clusters_with_img_not_managed(my_clusters)

		for center, cluster in my_clusters :
			if len(cluster) > self.NB_MAX_ELEM_IN_CLUSTER  and len(cluster) != nb_imgs:
				#nombre d'élément supérieur à celui max attendu dans un cluster on relance dessus
				#seulement si on n'a pas créer qu'un seul cluster de ces données
				cluster = self.recursive_intelligent_k_means(cluster)

		return my_clusters


	def intelligent_k_means(self, list_ind_imgs, my_clusters) :
		""" Utilise la méthode des k_means intelligent pour trier nos données
		en différents clusters.

		Param :	
			- list_ind_imgs : list de int : liste des indices de nos images à trier
		"""
		if(len(list_ind_imgs) == 0) :
			return

		#On défini les premiers clusters (centres)
		ind_center_img = self.find_new_representant(list_ind_imgs)
		list_ind_imgs.remove(ind_center_img)
		my_clusters = self.define_intelligent_clusters(ind_center_img, list_ind_imgs, my_clusters)

		#On supprime les clusters singletons
		my_clusters, list_ind_imgs = self.remove_singleton_cluster(my_clusters)
		list_ind_imgs.append(ind_center_img)
		centers_clusters = [elem[0] for elem in my_clusters]

		#On prends toutes les images et on les places dans le clusters du centre le plus
		#proche si le seuil de sim est correspondant
		ind_img_managed = []
		for ind_img in list_ind_imgs :
			(center, score_sim) = self.find_closest_cluster_for_an_img(ind_img, centers_clusters)
			if score_sim >= self.seuil_min_similarity :
				#Si on a une similarité minimum, on ajoute l'image au cluster
				self.add_img_to_cluster(center, ind_img, my_clusters)
				ind_img_managed += [ind_img]

		self.ind_img_not_managed = [i for i in list_ind_imgs if i not in ind_img_managed]
		return my_clusters


	def add_img_to_cluster(self, center_cluster, ind_img, my_clusters) :
		""" Ajoute au cluster représenter par center_cluster l'image ind_img.

		Param :
			- center_cluster : int : indice de l'image représentant le cluster
			- ind_img : int : indice de l'image à ajouter dans le cluster

		"""
		for (center, cluster) in my_clusters :
			if center == center_cluster :
				cluster.append(ind_img)

	def create_clusters_with_img_not_managed(self, my_clusters) :
		"""Ajoute les self.ind_img_not_managed en tant que cluster singleton dans my_cluster"""
		for ind_img in self.ind_img_not_managed :
			my_clusters.append((ind_img, [ind_img]))
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
			score_sim = self.get_score_similarity(ind_img, center)
			if score_sim > sim_max :
				c = center
				sim_max = score_sim
		return (c, sim_max)

	def remove_singleton_cluster(self, my_clusters) :
		""" Supprime de my_clusters tous les clusters ne possèdant qu'un element.

		Retour :
			La liste des indices des images étant dans des clusters singletons 
		"""
		list_ind_imgs_not_in_cluster = []

		for (representant_cluster, cluster) in my_clusters :
			if len(cluster) == 1 :
				#Un seul élément dans le cluster, on en veut pas.
				list_ind_imgs_not_in_cluster += [representant_cluster]
				#vu qu'il n'y a qu'un seul élément, il n'y a que le représentant

		my_clusters = [elem for elem in my_clusters if elem[0] not in list_ind_imgs_not_in_cluster]
		return (my_clusters, list_ind_imgs_not_in_cluster)

	def define_intelligent_clusters(self, ind_center_img, list_ind_imgs, my_clusters) :
		""" Utilise l'algorithme des K-means Intelligents pour définirs les clusters.
		Ils seront retourner sous la forme suivante  :
			[(centre, [2, 5, 3, 9, 7, 15]), (centre, [12, 78, 32, 56], [12, 4])]
		Où chaque sous liste est un cluster.

		Param :
			- ind_center_img : int : indice de l'image "centrale" (ayant le max de 
			similarité avec toutes les autres) dans notre liste d'image
			- list_ind_imgs : list de int : liste des indices de toutes les images
			que l'on souhaite classée.

		Les clusters calculés s'ajoute à my_cluster
		"""

		while len(list_ind_imgs) > 0 :
			(representant, cluster) = self.find_one_cluster(ind_center_img, list_ind_imgs)
			list_ind_imgs = [elem for elem in list_ind_imgs if elem not in cluster]
			my_clusters += [(representant, cluster)]

		return my_clusters

	def find_one_cluster(self, ind_center_img, list_ind_imgs) :
		"""Trouve le cluster le plus éloigné de l'image centrale avec l'algo des K-Means Intelligent

		Param :
			- ind_center_img : int : indice de l'image "centrale" (ayant le max de 
			similarité avec toutes les autres) dans notre liste d'image
			- list_ind_imgs : list de int : liste des indices de toutes les images
			que l'on souhaite classée.

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

		Retour :
			- int : indice de l'image la plus éloigné du centre
		"""
		score_sim_min = 9999999
		farest_img_id = None
		for i in list_ind_img :
			if i != id_center_img :	
				score = self.get_score_similarity(i, id_center_img)
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
			- list_ind_img : list de int : liste des indices des images à traiter

		Retour :
			liste d'indice correspondant à toutes les images plus proches de 
			representant_ind que de center_ind
		"""
		cluster = []
		for i in list_ind_img :
			if i != center_ind and i != representant_ind :
				if self.get_score_similarity(center_ind, i) <= self.get_score_similarity(representant_ind, i):
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
					s += self.get_score_similarity(ind1, ind2)
			vector[i] = s

		return cluster[vector.index(max(vector))]


	# ------------------------ getter & setter ---------------------------

	def get_score_similarity(self, ind_img1, ind_img2) :
		ind_img2 += 1
		ind_img1 += 1
		if ind_img1 < ind_img2 :
			ind_img2 -= ind_img1
			ind_img1 -= 1
			ind_img2 -= 1
			return self.tab_similarity[ind_img1][ind_img2]
		elif ind_img1 > ind_img2 :
			ind_img1 -= ind_img2
			ind_img1 -= 1
			ind_img2 -= 1
			return self.tab_similarity[ind_img2][ind_img1]

	def set_score_similarity(self, ind_img1, ind_img2, score) :
		ind_img2 += 1
		ind_img1 += 1
		if ind_img1 < ind_img2 :
			ind_img2 -= ind_img1
			ind_img1 -= 1
			ind_img2 -= 1
			self.tab_similarity[ind_img1][ind_img2] = score
		elif ind_img1 > ind_img2 :
			ind_img1 -= ind_img2
			ind_img1 -= 1
			ind_img2 -= 1
			self.tab_similarity[ind_img2][ind_img1] = score

	# ------------------------ Display -----------------------------------

	def plot_clusters(self) :
		"""Affiche tous les clusters à l'écran (une fenetre par cluster)"""
		for (representant, cluster) in self.clusters :
			taille = len(cluster)
			X = 15
			Y = taille/X
			if taille%X > 0 :
				Y += 1
			fig = plt.figure()
			for i,ind in enumerate(cluster) :
				fig.add_subplot(Y, X, i+1)
				plt.imshow(self.learn_imgs[ind])
		plt.show()

	def display_stats(self) :
		""" Affiche les statistiques calculées de notre classification dans le terminal"""
		nb_imgs_not_managed = len(self.ind_img_not_managed)
		nb_imgs_managed = self.NB_IMG - nb_imgs_not_managed
		pourcentage_managed = (float(nb_imgs_managed) / float(self.NB_IMG))*100
		pourcentage_not_managed = (float(nb_imgs_not_managed) / float(self.NB_IMG))*100
		nb_clusters = len(self.clusters)
		mean_cluster_size = np.mean([len(c[1]) for c in self.clusters])
		rapport_sn = (mean_cluster_size/float(self.NB_IMG))*100
		list_size_clusters = [len(c[1]) for c in self.clusters]
		list_size_clusters.sort()
		median_size = list_size_clusters[nb_clusters/2]
		max_size = list_size_clusters[-1]
		
		print("Nombre d'images traitées (N): " + str(self.NB_IMG))
		print("Nombre de clusters : " + str(nb_clusters))
		print("Taille moyenne cluster (S): " + str(mean_cluster_size))
		print("Taille médiane cluster : " + str(median_size))
		print("Taille du cluster le plus grands : " + str(max_size))
		print("Rapport S/N : " +  str(rapport_sn) + "%")

	def display_clusters(self) :
		""" Affiche les clusters obtenus dans le terminal"""
		print("Clusters :")
		for center, cluster in self.clusters :
			print(str(center) + " -----> " + str(cluster))
		
	# ------------------------ Gestion de sauvegarde -----------------------------
	
	def load_img_from_list_Img_Density(self, list_Img_Density, all_imgs=True) :
		""" Charge les sub_imgs de chaque Img_Density

		Param :
			list_Img_Density : list de imd.Img_Density
		"""
		self.learn_imgs = []
		cpt = 0
		#On ajoute en premier l'image d'eau, elle nous servira d'image de base
		# --- > origine du repère
		# self.learn_imgs.append(create_water_img())
		# cpt += 1

		#On ajoute les autre image 
		for img in list_Img_Density :
			if not all_imgs :
				if cpt + len(img.sub_imgs) > self.NB_IMG :
					#pas toutes les images, on arrive à la limite acceptable
					nb_image_restantes = self.NB_IMG - cpt
					self.learn_imgs += img.sub_imgs[:nb_image_restantes]
					cpt += nb_image_restantes
					break
				else :
					#pas toutes les images, on dépasse pas encore la limite
					self.learn_imgs += img.sub_imgs
					cpt += len(img.sub_imgs)
			if all_imgs :
				#toutes les images, on add tout
				self.learn_imgs += img.sub_imgs

		if all_imgs :
			#toutes les images, on mets à jour la valeur de self.NB_IMG
			self.NB_IMG = len(self.learn_imgs)
		print("Nombre Image : " + str(self.NB_IMG))

	def extract_N_samples_for_test(self, N = NB_TEST) :
		""" Choisi de manière aléatoire N images dans self.learn_imgs et les 
		range dans self.test_imgs, réduit self.NB_IMG de N"""

		self.test_imgs = []

		for _ in range(N) :
			ind_imgs = list(range(self.NB_IMG))
			ind = random.choice(ind_imgs)
			self.test_imgs += [self.learn_imgs[ind]]
			del(self.learn_imgs[ind])
			self.NB_IMG -= 1
			
	def create_N_random_img(self, N) :
		""" Créer N random images pour notre database.
		Toutes les images sont ajoutées à self.learn_imgs

		Param :
			N : int : nombre d'image à Créer
		"""
		self.learn_imgs = []
		#On ajoute en premier l'image d'eau, elle nous servira d'image de base
		# --- > origine du repère
		self.learn_imgs.append(create_water_img())
		for _ in range(N) :
			self.learn_imgs += [create_pseudo_random_img()]

	def create_N_random_img_for_test(self, N) :
		self.test_imgs = []
		for _ in range(N) :
			self.test_imgs += [create_pseudo_random_img()]

	def load_imgs_in_files(self, directory) :
		def is_int(value) :
			try :
				int(value)
				return True
			except :
				return False
		files = os.listdir(directory) 
		my_imgs = [0 for _ in range(len(files))]
		for filename in files :
			with open(directory + filename, "r") as f :
				res = f.read()
				f = filename.split("_")
				if f[0] == "img" :
					ind = int(f[-1])
					my_imgs[ind] = [[int(i) for i in a if is_int(i)] for a in res.split("]") if len(a) > 0]

		return my_imgs

	def save_imgs_in_files(self, my_imgs, directory="./data/learn_imgs/") :
		for i in range(len(my_imgs)) :
			file_name = directory + "img_" + str(i)
			with open(file_name, "w+") as f :
				f.write(str(my_imgs[i]))

	def load_similarity(self, file="./data/similarity.don") :
		"""Charge les scores de similarité préc alculés en enregistrer dans file

		Param :
			-file : string : nom du fichier
		"""
		with open(file, "r") as f :
			dict_sim = json.load(f)


		nb_img = max([int(elem.split(",")[0][1:]) for elem in list(dict_sim.keys())]) + 1 + 1 #indice donc + 1, 
		self.tab_similarity = [[0 for i in range(j)] for j in range(nb_img - 1, 0, -1)]
		#indice le plus gros est 499 pour couplé l'image 500 donc + 2
		for j in range(nb_img) :
			for i in range(nb_img - j - 1) :
				self.tab_similarity[j][i] = dict_sim[str((j, i))]

	def save_similarity(self, file="./data/similarity.don") :
		"""Enregistre dans un fichier la similarité calculé entre toutes nos images

		Param :
			- file : string : nom du fichier
		"""
		dict_sim = {}
		for j in range(len(self.tab_similarity)) :
			for i in range(len(self.tab_similarity[j])) :
				dict_sim[str((j, i))] = self.tab_similarity[j][i]

		with open(file, "w+") as f :
			json.dump(dict_sim, f)

# -------------------------- Fonctions utiles -------------------------------------

def create_water_img() :
	"""Créer une image composée d'eau
	Retour : 
		double list : représente une image composée seulement d'eau
	"""
	size_img = imd.Img_Density.RAYON_SUB_IMG*2
	return [[0 for i in range(size_img)] for j in range(size_img)]

def create_pseudo_random_img() :
	"""Créer et retourne une image aléatoire. 
	L'image va préférentiellement créer des zones

	Retour :
		- double list : représente une image aléatoire"""


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

	Retour :
		list de tuple (u,v). Où u est l'abscisse et v et l'ordonnée de 
		chacun des voisin de (i,j)
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

# --------------------------- Main  ----------------------------------------


if __name__ == "__main__" :
	density_file = "../../../working_dir/slice_098/densite_lu/densite_hu.don"
	config_file = "../../../working_dir/slice_098/densite_lu/config_KIDS.don"

	filtre = None
	if len(sys.argv) > 1 :
		filtre = sys.argv[1]

	img_density = imd.Img_Density(density_file, config_file)
	dw = Data_Work([img_density], filtre)
	dw.train()
	dw.test()
	# dw.save_data()
