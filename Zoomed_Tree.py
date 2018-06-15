#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-

import zoomed_image as zi
import matplotlib.pyplot as plt
import Decision_Tree as dt
import Img_Density as imd
import Similarity as simy
from Bcolor import bcolors
import Stats
import random
import time
import math

from ProgressBar import ProgressBar


def show_img(img) :
	plt.imshow(img)
	plt.show()

ZOOM_ROOT = 32

class Root() :
	def __init__(self) :
		self.sons = list()
		self.type = "root"
		self.profondeur = -1
		self.id_imgs = list()
		self.dict_sim = None
		self.decision_tree = None

class Node() :
	def __init__(self, representant, profondeur) :
		self.sons = list()
		self.type = "node"
		self.representant = representant
		self.profondeur = profondeur
		self.id_imgs = list()
		self.dict_sim = None
		self.decision_tree = None

	def __str__(self) :
		return str(self.representant)

class Leaf() :
	def __init__(self, img, identifiant) :
		self.type = "leaf"
		self.img = img
		self.identifiant = identifiant
		self.z_img = zi.Zoomed_Image(img)

class Zoomed_Tree() :
	""" Défini l'arbre qui zoom dans les images"""

	def __init__(self, list_img = list(), split_method = "random", symmetric_similarity="true") :
		self.root = Root()
		self.imgs = list()
		self.dict_sim = None

		self.split_method = split_method
		self.symmetric_similarity = symmetric_similarity

		if len(list_img) != 0 :
			print("Ajout des images d'apprentissage dans l'arbre zoomé.")
			for img in list_img :
				self.add_img(img)
			self.compute_all_decision_tree()

	def compute_all_decision_tree(self) :

		def create_decision_tree_on_node(self, node) :

			def extract_id_img_from_node(node) :

				def get_all_imgs_from_node(node) :

					def recursive_research(node) :
						if node.type == "leaf" :
							return [node.identifiant]
						res = []
						for son in node.sons :
							res += recursive_research(son)
						return res

					return recursive_research(node)

				if node.sons[0].type == "leaf" :
					#cas où on atteint les feuilles
					#on a trouvé l'image
					leaf = node.sons[0]
					return [leaf.identifiant]
				else :
					#pas d'image égale, on obtient le noeud père le plus bas
					id_imgs = get_all_imgs_from_node(node)
					return id_imgs

			node.id_imgs = extract_id_img_from_node(node)
			node.decision_tree = dt.Decision_Tree(None, node.id_imgs, self.dict_sim, self.imgs, None,\
				 split_method = self.split_method, \
				 symmetric_similarity = self.symmetric_similarity)
			node.decision_tree.create_tree()

		def recursive_compute_decision_tree(self, node) :
			if node.sons[0].type == "leaf" :
				create_decision_tree_on_node(self, node)
			else :
				create_decision_tree_on_node(self, node)
				for son in node.sons :
					recursive_compute_decision_tree(self, son)

		def compute_similarity(self) :

			def compute_similarity_img1_img2(self, img1, img2) :
				if self.symmetric_similarity == "true":
					return simy.symmetric_similarity_between_two_imgs(img1, img2)
				else :
					return simy.similarity_between_two_imgs(img1, img2)

			nb_imgs = len(self.imgs)
			self.dict_sim = simy.Dict_Sim(nb_imgs)
			avancement = 0
			fin = (nb_imgs * (nb_imgs - 1)) / 2
			progress_bar = ProgressBar(avancement, fin)
			for i in range(nb_imgs) :
				for j in range(i+1, nb_imgs) :
					img1 = self.imgs[i]
					img2 = self.imgs[j]
					score_sim, inter_sim = compute_similarity_img1_img2(self, img1, img2)
					self.dict_sim.set_similarity(i, j, score_sim)
					avancement += 1
					progress_bar.updateProgress(avancement, "")

		node = self.root
		print("Calcul des similarités entre " + str(len(self.imgs)) +" images...")
		compute_similarity(self)
		print("Calcul des Arbre Métriques...")
		recursive_compute_decision_tree(self, node)

	def add_img(self, img) :

		def find_node_and_add_leaf(self, leaf) :

			def add_node_to_node(node, leaf, profondeur) :
				zoom = get_zoom_child(node)
				representant = leaf.z_img.extract_zoomed_img(zoom)
				new_node = Node(representant, profondeur)
				node.sons += [new_node]
				return new_node

			def add_leaf_to_node(self, node, leaf) :
				"""Return False s'il y avait déjà l'image dans la database"""
				for existing_leaf in node.sons :
					if self.are_equal(existing_leaf.img, leaf.img) :
						#image déjà existante
						return False
				node.sons.append(leaf)
				return True

			def get_zoom_child(node) :
				zoom = ZOOM_ROOT / pow(2, node.profondeur + 1)
				return zoom

			def recursive_find_and_add(self, node, leaf, profondeur) :
				if len(node.sons) == 0 :
					#cas racine initiale
					node = add_node_to_node(node, leaf, profondeur+1)
					is_new_image = add_leaf_to_node(self, node, leaf)
					if is_new_image :
						self.imgs += [leaf.img]
					return node

				while node.sons[0].type != "leaf" :
					#on s'arrete si mon fils est une feuille
					#si je suis dans la boucle, tous mes fils sont des node
					zoom = get_zoom_child(node)
					#on prends le zoom accordé au fils de node. 
					#vu qu'on le compare à ses fils
					img_leaf = leaf.z_img.extract_zoomed_img(zoom)

					node_found = False

					for son in node.sons :
						if self.are_equal(son.representant, img_leaf) :
							#on trouve un noeud avec un représentant égale
							node = son
							node_found = True
							break
					if not node_found :
						#Aucun noeud ne lui correspond, on créer le sien
						#on peut le renvoyer car on est sur que c'est ce noeud
						node = add_node_to_node(node, leaf, profondeur+1)
						is_new_image = add_leaf_to_node(self, node, leaf)
						if is_new_image :
							self.imgs += [leaf.img]
						return node
					profondeur += 1

				#On trouve un noeud avec au moins une feuille
				zoom = get_zoom_child(node)
				#on prends le zoom accordé au fils de node. 
				#vu qu'on le compare à ses fils
				while zoom > 1 :
					#on peut encore zoomer, donc on créer un niveau de plus
					leaf_present = node.sons[0]
					node.sons = list() #clean des fils, on enlève les leaf, on mets des nodes
					new_node_left = add_node_to_node(node, leaf_present, profondeur+1)
					add_leaf_to_node(self, new_node_left, leaf_present)

					img_leaf = leaf.z_img.extract_zoomed_img(zoom)

					if not self.are_equal(new_node_left.representant, img_leaf) :
						## Situation impossible en théorie : notre dernier zoom = l'image
						#alors on peut créer un noeud en plus
						new_node_right = add_node_to_node(node, leaf, profondeur+1)
						is_new_image = add_leaf_to_node(self, new_node_right, leaf)
						if is_new_image :
							self.imgs += [leaf.img]
						return new_node_right

					#Les images sont égales, donc un niveau de plus
					node = new_node_left
					zoom = get_zoom_child(node)
					profondeur += 1

				if zoom <= 1 :
					#il n'y a pas plus bas que un, donc on amasse les feuilles
					is_new_image = add_leaf_to_node(self, node, leaf)
					if is_new_image :
						self.imgs += [leaf.img]
					return node

			node = self.root
			profondeur = -1
			node = recursive_find_and_add(self, node, leaf, profondeur)

		identifiant = len(self.imgs)
		leaf = Leaf(img, identifiant)
		find_node_and_add_leaf(self, leaf)

	def find_closest_img(self, img, plot=False) :

		def find_closest_node(self, z_img) :

			def get_zoom_node(node) :
					zoom = ZOOM_ROOT / pow(2, node.profondeur)
					return zoom

			node = self.root
			while node.sons[0].type != "leaf" :
				node_found = False
				for son in node.sons :
					zoom = get_zoom_node(son)
					if self.are_equal(son.representant, z_img.extract_zoomed_img(zoom)) :
						node = son
						node_found = True
						break
				if not node_found :
					#il n'existe pas de noeud lui étant égale zoomé, 
					#on prends le noeud le plus proche connu
					#on va étudier toutes ses feuilles
					return node
			return node

		def get_zoom_node(node) :
			zoom = ZOOM_ROOT / pow(2, node.profondeur)
			return zoom

		def plot_result(img, prediction) :
			score, intervale = simy.similarity_between_two_imgs(img, prediction)
			segment_result = simy.get_disque_segment(img, intervale)
		
			fig = plt.figure()
			fig.add_subplot(1, 3, 1)
			plt.imshow(img)

			fig.add_subplot(1, 3, 2)
			plt.imshow(prediction)

			fig.add_subplot(1, 3, 3)
			plt.imshow(segment_result)

			plt.show()

		z_img = zi.Zoomed_Image(img)
		node = find_closest_node(self, z_img)
		prediction, score, dt_node, nb_visit, intervale = node.decision_tree.predict(img)
		if plot :
			plot_result(img, prediction)

		return prediction, score, intervale

	def predict_all_imgs(self, imgs, plot=False) :

		def predict_one_img(self, img) :
			quart_imgs = imd.extract_quartil(img)
			quart_pred = []
			quart_interval = []
			score = 0
			for q_img in quart_imgs :
				q_pred, q_score, q_intervale = self.find_closest_img(q_img)
				score += q_score
				quart_pred += [q_pred]
				quart_interval += [q_intervale]
			prediction = imd.recompose_into_img(quart_pred)
			result_img = simy.get_full_disque(quart_interval)
			return prediction, score, result_img

		def plot_result(img, prediction, difference) :
			fig = plt.figure()
			fig.add_subplot(3, 1, 1)
			plt.imshow(img)
			
			fig.add_subplot(3, 1, 2)
			plt.imshow(prediction)

			fig.add_subplot(3, 1, 3)
			plt.imshow(difference)
			plt.show()

		nb_prediction = len(imgs)
		print("Prédiction de " + str(nb_prediction) + " images en cours...")
		progress_bar = ProgressBar(0, nb_prediction)
		stats = Stats.Stats(len(self.imgs))

		list_prediction = list()
		list_score = list()
		list_difference = list()

		for i, img in enumerate(imgs) :
			begin = time.time()
			prediction, score, difference = predict_one_img(self, img)
			end = time.time()

			list_prediction += [prediction]
			list_score += [score]
			list_difference += [difference]

			temps = end - begin
			stats.add_test(score, temps)
			pourcentage = (score / (2*math.pi))

			progress_bar.updateProgress(i+1, "")

			if plot :
				plot_result(img, prediction, difference)

		print(bcolors.OKGREEN)
		print(stats)
		print(bcolors.ENDC)
		return list_prediction, list_score, list_difference

	def __str__(self) :

		def img_str(img, cpt) :
			string = ""
			for line in img :
				string += "  "*cpt + str(line) + "\n"
			return string

		def recursive_str(node, cpt) :
			string = ""
			if node.type != "leaf" :
				for son in node.sons :
					if son.type == "leaf" :
						string += img_str(son.img, cpt) + "\n"
					else :
						string += img_str(son.representant, cpt) +"\n"
						string += str(son.decision_tree)
						string += recursive_str(son, cpt+1)

				return string
			return ""

		node = self.root
		return recursive_str(node, 0)

	def are_equal(self, img1, img2) :
		""" Return true si img1 == img2, False sinon"""
		def are_imgs_equal(img1, img2) : 
			size1 = len(img1)
			size2 = len(img2)
			if size1 != size2 : 
				print("Image de taille différentes donc non égales.")
				print("Taille img1 : " + str(size1))
				print("Taille img2 : " + str(size2))
				raise ValueError
			for i in range(size1) :
				for j in range(size2) :
					if img1[i][j] != img2[i][j] :
						return False
			return True

		def are_imgs_symmetric_equal(img1, img2) :

			def symetric_img(img) :
				len_first = len(img)
				len_second = len(img[0])
				return [[img[j][i] for j in range(len_second)] for i in range(len_first)]

			symmetric_img2 = symetric_img(img2)
			return are_imgs_equal(img1, img2) or are_imgs_equal(img1, symmetric_img2)

		if self.symmetric_similarity == "true":
			return are_imgs_symmetric_equal(img1, img2)
		else :
			return are_imgs_equal(img1, img2)

def create_random_img(size_x, size_y) :
	return [[random.choice([0, 0, 0, 0, 1, 1, 2]) for i in range(size_x)] for j in range(size_y)]



if __name__ == '__main__':
	zt = Zoomed_Tree()
	NB_IMG = 50
	NB_TEST = 10
	size_img = 32
	#train
	imgs = [create_random_img(size_img, size_img) for _ in range(NB_IMG)]
	for img in imgs :
		zt.add_img(img)
	zt.compute_all_decision_tree()


	#test
	test = [create_random_img(size_img,size_img) for _ in range(NB_TEST)]
	nb = 0
	total_temps = 0
	for img in test :
		t = time.time()
		ci = zt.find_closest_img(img, plot=True)
		temps_operation = time.time()-t
		total_temps += temps_operation
		nb += len(ci)
	print("Nombre d'image moyenne à départager : " + str(float(nb/NB_TEST)))
	print("Temps moyen de l'opération : " + str(float(total_temps/NB_TEST)))
