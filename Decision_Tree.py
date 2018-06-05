#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-

import random
import Similarity as simy
from matplotlib import pyplot as plt
import time

class Decision_Tree() :
	
	def __init__(self, representant, list_ind_imgs, similarity, imgs, tests, profondeur = 0, k = 5) :
		self.list_ind_imgs = list_ind_imgs
		self.k = k
		self.tab_similarity = similarity
		self.sons = []
		self.representant = representant
		self.profondeur = profondeur
		self.imgs = imgs
		self.tests = tests
		self.max_similarity = simy.max_score_similarity()


	# ------------------------ Getter & Setter ---------------------------

	def get_score_similarity(self, ind_img1, ind_img2) :
		return self.tab_similarity.get_similarity(ind_img1, ind_img2)

	# ------------------------- Prediction -------------------------------

	def predict(self, img_to_predict) :

		nb_visit = 0

		def calcul_similarity_with_all_imgs(img_to_predict, ind_imgs, nb_visit) :
			dict_sim = {}
			for ind_img in ind_imgs :
				nb_visit += 1
				dict_sim[ind_img] = simy.symmetric_similarity_between_two_imgs(img_to_predict, self.imgs[ind_img])[0]
			return dict_sim, nb_visit

		def find_closest_img_in_cluster(img_to_predict, list_ind_imgs, nb_visit) :
			dict_sim, nb_visit = calcul_similarity_with_all_imgs(img_to_predict, list_ind_imgs, nb_visit)
			closest_img = None
			score_max = -10000
			for key, score_sim in dict_sim.items() :
				if score_sim > score_max :
					closest_img = key
					score_max = score_sim
			return closest_img, score_max, nb_visit

		def symetric_img(img) :
			len_first = len(img)
			len_second = len(img[0])
			return [[img[j][i] for j in range(len_second)] for i in range(len_first)]

		def img_to_return(img_to_predict, img_found) :
			if simy.similarity_between_two_imgs(img_to_predict, img_found)[0] < score :
				return symetric_img(img_found)
			return img_found

		if len(self.list_ind_imgs) < self.k :
			#on est sur qu'il n'y a pas de sous cluster
			closest, score, nb_visit = find_closest_img_in_cluster(img_to_predict, self.list_ind_imgs, nb_visit)
			prediction = img_to_return(img_to_predict, self.imgs[closest])
			return prediction, score, self, nb_visit

		node = self
		score_actual_representant = -10000
		#Tant que l'on est pas dans un noeud trop petit
		while len(node.list_ind_imgs) >= self.k :
			#On cherche le centre le plus proche
			centers = [son.representant for son in node.sons]
			max_center, score_sim, nb_visit = find_closest_img_in_cluster(img_to_predict, centers, nb_visit)

			#Si le centre le plus proche n'est pas plus proche que le représentant actuel, 
			#on retourne le représentant actuel
			if score_actual_representant > score_sim :
				prediction = img_to_return(img_to_predict, self.imgs[node.representant])
				return prediction, score_actual_representant, node, nb_visit
			score_actual_representant = score_sim

			#On attribut à node le bon fils
			for son in node.sons :
				if son.representant == max_center :
					node = son
					break

			#Si le score actuel égale le score max, on a retrouvé exactement la 
			#même image, donc on la retourne
			if score_actual_representant == self.max_similarity :
				prediction = img_to_return(img_to_predict, self.imgs[node.representant])
				return prediction, score_actual_representant, node, nb_visit

		indice_prediction, score, nb_visit = find_closest_img_in_cluster(img_to_predict, node.list_ind_imgs, nb_visit)
		prediction = img_to_return(img_to_predict, self.imgs[indice_prediction])
		return prediction, score, node, nb_visit

	def predict_closest_img(self, ind_img) :

		nb_visit = 0

		def calcul_similarity_with_all_imgs(ind_test, ind_imgs, nb_visit) :
			dict_sim = {}
			for ind_img in ind_imgs :
				nb_visit += 1
				dict_sim[ind_img] = simy.symmetric_similarity_between_two_imgs(self.tests[ind_test], self.imgs[ind_img])[0]
			return dict_sim, nb_visit

		def find_closest_img_in_cluster(ind_img, list_ind_imgs, nb_visit) :
			dict_sim, nb_visit = calcul_similarity_with_all_imgs(ind_img, list_ind_imgs, nb_visit)
			closest_img = None
			score_max = 0
			for key, score_sim in dict_sim.items() :
				if score_sim > score_max :
					closest_img = key
					score_max = score_sim
			return closest_img, score_max, nb_visit

		if len(self.list_ind_imgs) < self.k :
			#on est sur qu'il n'y a pas de sous cluster
			closest, score, nb_visit = find_closest_img_in_cluster(self, ind_img, self.list_ind_imgs, nb_visit)
			return closest, score, self, nb_visit

		node = self
		score_actual_representant = 0
		#Tant que l'on est pas dans un noeud trop petit
		while len(node.list_ind_imgs) >= self.k :
			#On cherche le centre le plus proche
			centers = [son.representant for son in node.sons]
			max_center, score_sim, nb_visit = find_closest_img_in_cluster(ind_img, centers, nb_visit)

			#Si le centre le plus proche n'est pas plus proche que le représentant actuel, 
			#on retourne le représentant actuel
			if score_actual_representant > score_sim :
				return node.representant, score_actual_representant, node, nb_visit
			score_actual_representant = score_sim

			#On attribut à node le bon fils
			for son in node.sons :
				if son.representant == max_center :
					node = son
					break

			#Si le score actuel égale le score max, on a retrouvé exactement la 
			#même image, donc on la retourne
			if score_actual_representant == self.max_similarity :
				return node.representant, score_actual_representant, node, nb_visit

		center, score, nb_visit = find_closest_img_in_cluster(ind_img, node.list_ind_imgs, nb_visit)
		return center, score, node, nb_visit


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

			# On calcule le centre associé à chacune de nos classes
			centers = []
			for fam in families :
				c = find_new_representant(dec_tree, fam)
				centers += [c]
			return centers

		def calcul_new_families_for_centers(dec_tree, centers, list_ind_imgs) :

			
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
				sim_max = -10000
				c = None
				for center in centers_clusters :
					score_sim = self.get_score_similarity(ind_img, center)
					if score_sim > sim_max :
						c = center
						sim_max = score_sim
				return (c, sim_max)

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
					center, sim_value = find_closest_cluster_for_an_img(dec_tree, ind_img, centers)
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
		print("Nombre d'image d'entrainement : " + str(len(self.list_ind_imgs)))
		print("K = " + str(self.k))
		print("\n")


		

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
		scores = [(simy.similarity_between_two_imgs(dw.learn_imgs[img], dw.learn_imgs[l_img])[0], l_img) for l_img in imgs]
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
		plt.imshow(ms)
		plt.show()

	print("Temps prediction totale: " + str(cpt_predict))
	print("Temps recherche totale: " + str(cpt_research))
