#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-

import random
import Data_Work
import Similarity as simy
from matplotlib import pyplot as plt
import time



class Decision_Tree() :
	
	def __init__(self, representant, list_ind_imgs, similarity, imgs, tests, profondeur = 0, k = 7) :
		self.list_ind_imgs = list_ind_imgs
		self.k = k
		self.tab_similarity = similarity
		self.sons = []
		self.representant = representant
		self.profondeur = profondeur
		self.imgs = imgs
		self.tests = tests


	# ------------------------ Getter & Setter ---------------------------

	def get_score_similarity(self, ind_img1, ind_img2) :
		# ind_img2 += 1
		# ind_img1 += 1
		# if ind_img1 < ind_img2 :
		# 	ind_img2 -= ind_img1
		# 	ind_img1 -= 1
		# 	ind_img2 -= 1
		# 	return self.tab_similarity[ind_img1][ind_img2]
		# elif ind_img1 > ind_img2 :
		# 	ind_img1 -= ind_img2
		# 	ind_img1 -= 1
		# 	ind_img2 -= 1
		# 	return self.tab_similarity[ind_img2][ind_img1]
		return self.tab_similarity.get_similarity(ind_img1, ind_img2)


	# ------------------------- Prediction -------------------------------

	def predict_closest_img(self, ind_img) :

		def calcul_similarity_with_all_imgs(ind_test, ind_imgs) :
			dict_sim = {}
			for ind_img in ind_imgs :
				dict_sim[ind_img] = simy.similarity_between_two_imgs(self.tests[ind_test], self.imgs[ind_img])
			return dict_sim

		def find_closest_img_in_cluster(ind_img, list_ind_imgs) :
			dict_sim = calcul_similarity_with_all_imgs(ind_img, list_ind_imgs)
			closest_img = None
			score_max = 0
			for key, score_sim in dict_sim.items() :
				if score_sim > score_max :
					closest_img = key
					score_max = score_sim
			return (closest_img, score_max)

		if len(self.list_ind_imgs) < self.k :
			#on est sur qu'il n'y a pas de sous cluster
			return find_closest_img_in_cluster(self, ind_img, self.list_ind_imgs)

		node = self
		score_actual_representant = 0
		#Tant que l'on est pas dans un noeud trop petit
		while len(node.list_ind_imgs) >= self.k :
			#On cherche le centre le plus proche
			centers = [son.representant for son in node.sons]
			max_center, score_sim = find_closest_img_in_cluster(ind_img, centers)

			#Si le centre le plus proche n'est pas plus proche que le représentant actuel, 
			#on retourne le représentant actuel
			if score_actual_representant > score_sim :
				return node.representant, score_actual_representant, node
			score_actual_representant = score_sim

			#On attribut à node le bon fils
			for son in node.sons :
				if son.representant == max_center :
					node = son
					break

		center, score = find_closest_img_in_cluster(ind_img, node.list_ind_imgs)
		return center, score, node

	def predict_and_add_img(self, ind_img) :
		closest_img, score_sim, dt = self.predict_closest_img(ind_img)



		
	# ------------------------ Apprentissage -----------------------------

	def create_tree(self) :
		centers, families = self.split_in_k_sons(self.list_ind_imgs)
		# print(str([len(f) for f in families]))
		for i,fam in enumerate(families) :
			dt = Decision_Tree(centers[i], fam, self.tab_similarity, self.imgs, self.tests, self.profondeur + 1, self.k)
			self.sons.append(dt)
		for son in self.sons :
			son.create_tree()

	def split_in_k_sons(self, list_ind_imgs) :
		if len(list_ind_imgs) < self.k :
			#on est sur une feuille
			return ([], [])


		def create_k_random_families(dec_tree, list_ind_imgs) :
			#On initialise d'abord nos familles avec un element
			list_ind_imgs = list(list_ind_imgs)
			families = [[] for _ in range(dec_tree.k)]
			for i in range(dec_tree.k) :
				ind = random.choice(list_ind_imgs)
				list_ind_imgs.remove(ind)
				families[i] += [ind]

			# On créer des familles aléatoires
			indice_families = list(range(dec_tree.k))
			for ind_img in list_ind_imgs :
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

	def __str__(self) :
		string = str(self.profondeur) + "."
		for _ in range(self.profondeur) :
			string +=  "    "
		string += str(self.representant) + " --> " + str(self.list_ind_imgs) + "\n"
		for son in self.sons :
			string += str(son)
		return string

	def display_stats(self) :

		def get_profondeur_max(self) :
			if len(self.sons) == 0 :
				return self.profondeur
			else :
				return max([get_profondeur_max(son) for son in self.sons])

		print("Profondeur max de l'arbre : " + str(get_profondeur_max(self)))


		

if __name__ == "__main__" :

	dw = Data_Work.Data_Work([])
	dw.load_imgs_and_similarity("saved_data", {"directory" : "data/"})

	nb_test = 50
	imgs =  list(range(len(dw.learn_imgs)))
	test = []
	for _ in range(nb_test) :
		img = random.choice(imgs)
		imgs.remove(img)
		test.append(img)

	dt = Decision_Tree(None, imgs, dw.tab_similarity, dw.learn_imgs)
	dt.create_tree()
	print(dt)

	cpt_predict = 0
	cpt_research = 0

	for img in test : 
		t1 = time.time()
		predict, score_pred, node = dt.predict_closest_img(img)
		tfp = time.time() - t1
		cpt_predict += tfp
		print("Temps predict : " + str(tfp))

		t2 = time.time()
		scores = [(simy.similarity_between_two_imgs(dw.learn_imgs[img], dw.learn_imgs[l_img]), l_img) for l_img in imgs]
		max_score = 0
		best = None
		for s in scores :
			if s[0] > max_score :
				max_score = s[0]
				best = s[1]
		research = best
		tfr = time.time() - t2
		cpt_research += tfr
		print("Temps recherche : " + str(tfr))


		print(predict, research, score_pred, max_score, float(score_pred)/max_score*100)
		print("\n")
		fig = plt.figure()
		fig.add_subplot(4, 1, 1)
		plt.imshow(dw.learn_imgs[img])
		fig.add_subplot(4, 1, 2)
		plt.imshow(dw.learn_imgs[predict])
		fig.add_subplot(4, 1, 3)
		plt.imshow(dw.learn_imgs[research])
		fig.add_subplot(4, 1, 4)
		ms = simy.calcul_matrix_similarity(dw.learn_imgs[img], dw.learn_imgs[predict])
		hidden_points = simy.activate_field_of_view(ms)
		for p in hidden_points :
			ms[p[1]][p[0]] = 0
		plt.imshow(ms)
		plt.show()

	print("Temps prediction totale: " + str(cpt_predict))
	print("Temps recherche totale: " + str(cpt_research))
