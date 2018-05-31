#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-

import zoomed_image as zi
import matplotlib.pyplot as plt
import random


def show_img(img) :
	plt.imshow(img)
	plt.show()

ZOOM_ROOT = 8

class Zoomed_Tree() :
	""" Défini l'arbre qui zoom dans les images"""

	class Root() :
		def __init__(self) :
			self.sons = list()
			self.type = "root"
			self.profondeur = -1

	class Node() :
		def __init__(self, representant, profondeur) :
			self.sons = list()
			self.type = "node"
			self.representant = representant
			self.profondeur = profondeur

	class Leaf() :
		def __init__(self, img) :
			self.type = "leaf"
			self.img = img
			self.z_img = zi.Zoomed_Image(img)


	def __init__(self) :
		self.root = Zoomed_Tree.Root()

	def add_img(self, img) :

		def find_node_and_add_leaf(self, leaf) :

			def add_node_to_node(node, leaf, profondeur) :
				zoom = get_zoom_child(node)
				representant = leaf.z_img.extract_zoomed_img(zoom)
				new_node = Zoomed_Tree.Node(representant, profondeur)
				node.sons += [new_node]
				return new_node

			def add_leaf_to_node(node, leaf) :
				for existing_leaf in node.sons :
					if are_imgs_equal(existing_leaf.img, leaf.img) :
						#image déjà existante
						print("Image déjà présente dans la base de donnée.")
						return
				node.sons.append(leaf)

			def are_imgs_equal(img1, img2) : 
				size1 = len(img1)
				size2 = len(img2)
				if size1 != size2 : 
					print("Image de taille différentes donc non égales.")
					print("Taille img1 : " + str(size1))
					print("Taille img2 : " + str(size2))
					raise ValueError
					return False
				for i in range(size1) :
					for j in range(size2) :
						if img1[i][j] != img2[i][j] :
							return False
				return True

			def get_zoom_child(node) :
				zoom = ZOOM_ROOT / pow(2, node.profondeur + 1)
				return zoom

			def recursive_find_and_add(node, leaf, profondeur) :
				if len(node.sons) == 0 :
					#cas racine initiale
					node = add_node_to_node(node, leaf, profondeur+1)
					add_leaf_to_node(node, leaf)
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
						if are_imgs_equal(son.representant, img_leaf) :
							#on trouve un noeud avec un représentant égale
							node = son
							node_found = True
							break
					if not node_found :
						#Aucun noeud ne lui correspond, on créer le sien
						#on peut le renvoyer car on est sur que c'est ce noeud
						node = add_node_to_node(node, leaf, profondeur+1)
						add_leaf_to_node(node, leaf)
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
					add_leaf_to_node(new_node_left, leaf_present)

					img_leaf = leaf.z_img.extract_zoomed_img(zoom)

					if not are_imgs_equal(new_node_left.representant, img_leaf) :
						## Situation impossible en théorie : notre dernier zoom = l'image
						#alors on peut créer un noeud en plus
						new_node_right = add_node_to_node(node, leaf, profondeur+1)
						add_leaf_to_node(new_node_right, leaf)
						return new_node_right

					#Les images sont égales, donc un niveau de plus
					node = new_node_left
					zoom = get_zoom_child(node)
					profondeur += 1

				if zoom <= 1 :
					#il n'y a pas plus bas que un, donc on amasse les feuilles
					add_leaf_to_node(node, leaf)
					return node

			node = self.root
			profondeur = -1
			node = recursive_find_and_add(node, leaf, profondeur)

		leaf = Zoomed_Tree.Leaf(img)
		find_node_and_add_leaf(self, leaf)

	def find_closest_img(self, img) :

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

		def get_zoom_node(node) :
				zoom = ZOOM_ROOT / pow(2, node.profondeur)
				return zoom
		
		def find_closest_node(self, z_img) :
			node = self.root
			while node.sons[0].type != "leaf" :
				node_found = False
				for son in node.sons :
					zoom = get_zoom_node(son)
					if are_imgs_equal(son.representant, z_img.extract_zoomed_img(zoom)) :
						node = son
						node_found = True
						break
				if not node_found :
					#il n'existe pas de noeud lui étant égale zoomé, 
					#on prends le noeud le plus proche connu
					#on va étudier toutes ses feuilles
					return node
			return node

		def find_best_brothers(node, z_img) :

			def get_max_brothers_from_score(score) :
				score = sorted(score,key=lambda l:l[0], reverse=True)
				max_score = score[0][0]
				brothers = []
				for s in score :
					if s[0] == max_score :
						brothers += [s[1]]
					else :
						break
				return brothers

			def compute_score(node, z_img) :
				def nb_pixel_egal(img1, img2) :
					cpt = 0
					for i in range(len(img1)) :
						for j in range(len(img1[0])) :
							if img1[i][j] == img2[i][j] :
								cpt += 1
					return cpt

				score = []
				zoom = get_zoom_node(node.sons[0])
				img = z_img.extract_zoomed_img(zoom)
				for son in node.sons :
					score += [nb_pixel_egal(img, son.representant), son]
				return score

			score = compute_score(node, z_img)
			return get_max_brothers_from_score(score)

		def get_all_imgs_from_node(node) :

			def recursive_research(node) :
				if node.type == "leaf" :
					return node.img
				return [recursive_research(son) for son in node.sons]

			return recursive_research(node)

		z_img = zi.Zoomed_Image(img)
		node = find_closest_node(self, z_img)
		if node.sons[0].type == "leaf" :
			#cas où on atteint les feuilles
			#on a trouvé l'image
			leaf = node.sons[0]
			return leaf.img
		else :
			#pas d'image égale, on obtient le noeud père le plus bas
			imgs = get_all_imgs_from_node(node)
			return imgs


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
						string += recursive_str(son, cpt+1)
				return string
			return ""

		node = self.root
		return recursive_str(node, 0)



def create_random_img(size_x, size_y) :
	return [[random.choice([0, 1]) for i in range(size_x)] for j in range(size_y)]



if __name__ == '__main__':
	zt = Zoomed_Tree()
	NB_IMG = 50
	imgs = [create_random_img(8, 8) for _ in range(NB_IMG)]
	for img in imgs :
		zt.add_img(img)
	print(zt)



