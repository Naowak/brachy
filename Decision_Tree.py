#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-

import random
import Tree
import Data_Work


class Decision_Tree() :
	
	def __init__(self, representant, list_ind_imgs, similarity, profondeur = 0, k = 2,) :
		self.list_ind_imgs = list_ind_imgs
		self.k = k
		self.tab_similarity = similarity
		self.sons = []
		self.representant = representant
		self.profondeur = profondeur


	# ------------------------ Getter & Setter ---------------------------

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


	# ------------------------- Prediction -------------------------------

	def predict_closest_img(self, img) :
		pass
		
	# ------------------------ Apprentissage -----------------------------

	def create_tree(self) :
		centers, families = self.split_in_k_sons(self.list_ind_imgs)
		for i,fam in enumerate(families) :
			dt = Decision_Tree(centers[i], fam, self.tab_similarity, self.profondeur + 1, self.k)
			self.sons.append(dt)
		for son in self.sons :
			son.create_tree()

	def split_in_k_sons(self, list_ind_imgs) :
		if len(list_ind_imgs) < self.k :
			#on est sur une feuille
			return ([], [])


		def create_k_random_families(dec_tree, list_ind_imgs) :
			list_ind_imgs = list(list_ind_imgs)
			families = [[] for _ in range(dec_tree.k)]
			for i in range(dec_tree.k) :
				ind = list_ind_imgs[i]
				families[i] += [ind]

			# On créer des familles aléatoires
			indice_families = list(range(dec_tree.k))
			for ind_img in list_ind_imgs[2:] :
				ind_fam = random.choice(indice_families)
				families[ind_fam] += [ind_img]
			return families

		def calcul_centers_for_families(dec_tree, families) :
			# On calcule le centre associé à chacune de nos classes
			centers = []
			for fam in families :
				c = dec_tree.find_new_representant(fam)
				centers += [c]
			return centers

		def calcul_new_families_for_centers(dec_tree, centers, list_ind_imgs) :
			families = [[] for _ in range(dec_tree.k)]
			for ind_img in list_ind_imgs :
				is_a_center = False
				# Si ind_img est un center, alors on l'ajoute à la famille correspondante
				for i,c in enumerate(centers) :
					if ind_img == c :
						families[i] += [ind_img]
						is_a_center = True
						break
				#sinon, on cherche son center le plus proche
				if not is_a_center :
					center, sim_value = dec_tree.find_closest_cluster_for_an_img(ind_img, centers)
					indice_fam = [i for i,c in enumerate(centers) if c == center][0]
					families[indice_fam] += [ind_img]
			return families

		def are_equal_families(fam1, fam2) :
			if len(fam1) != len(fam2) :
				return False
			set_fam1 = [set(elem) for elem in fam1]
			set_fam2 = [set(elem) for elem in fam2]
			for elem in set_fam1 :
				if not elem in set_fam2 :
					return False
			return True


		families = create_k_random_families(self, list_ind_imgs)
		centers = calcul_centers_for_families(self, families)
		old_families = [[]]
		# On recalcule les familles jusqu'à convergence
		# (Si les centres ne bougent pas, les familles restent les mêmes)
		while not are_equal_families(old_families, families) :
			old_families = families
			families = calcul_new_families_for_centers(self, centers, list_ind_imgs)
			centers = calcul_centers_for_families(self, families)

		return (centers, families)

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
		for i,center in enumerate(centers_clusters) :
			score_sim = self.get_score_similarity(ind_img, center)
			# print(str(center) + " / " + str(ind_img) + "  --  " + str(score_sim))
			if score_sim > sim_max :
				c = center
				sim_max = score_sim
		return (c, sim_max)

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

	# ------------------------ Display & Plot ----------------------------

	# def __str__(self) :
	# 	string = ""
	# 	string += "Profondeur : " + str(self.profondeur) + "\n"
	# 	string += "Représentant : " + str(self.representant) + "\n"
	# 	string += "Population : " + str(self.list_ind_imgs) + "\n"
	# 	string += "Sons :\n\n" 
	# 	for son in self.sons :
	# 		string += str(son) + "\n"
	# 	return string

	def __str__(self) :
		string = ""
		for _ in range(self.profondeur) :
			string += "  "
		string += str(self.representant) + " --> " + str(self.list_ind_imgs) + "\n"
		for son in self.sons :
			string += str(son)
		return string

		

if __name__ == "__main__" :

	dw = Data_Work.Data_Work([])
	dw.load_imgs_and_similarity("saved_data", {"directory" : "data/"})

	dt = Decision_Tree(None, list(range(len(dw.learn_imgs))), dw.tab_similarity)
	dt.create_tree()
	print(dt)