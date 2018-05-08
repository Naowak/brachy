#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-

import Img_Density as imd
import Similarity as simy
import Decision_Tree as dt
from ProgressBar import ProgressBar
import os
import sys


NB_LEARN_IMGS = 1500
NB_TEST_IMGS = 0


class Extract_Data :

	def __init__(self, path, load = False, path_save = None, nb_learn_imgs = NB_LEARN_IMGS, nb_test_imgs = NB_TEST_IMGS) :
		self.path = path
		self.list_img_density = list()
		self.learn_imgs = list()
		self.test_imgs = list()
		self.nb_imgs = 0
		self.nb_learn_imgs = 0
		self.nb_test_imgs = 0
		self.dict_sim = None

		if load == False :
			if nb_learn_imgs == 0 :
				print("Impossible d'effectuer un apprentissage avec 0 images d'entrainement.")
				exit()
			self.extract_img_density(nb_learn_imgs, nb_test_imgs)
			self.dict_sim = simy.Dict_Sim(self.nb_imgs)
			self.compute_similarity_between_all_learn_imgs()
			self.save()
		else :
			self.dict_sim = simy.Dict_Sim()
			self.load(path)

		self.decision_tree = dt.Decision_Tree(None, list(range(self.nb_learn_imgs)), self.dict_sim, self.learn_imgs)
		self.compute_decision_tree()

		# if path_save != None :
		# 	self.save(path_save)

	# ----------------------------------- Extraction des donnée ------------------------------------

	def extract_img_density(self, nb_learn_imgs, nb_test_imgs) :

		def get_list_img_density(self) :
			directories = os.listdir(self.path)
			for directory in directories :
				dir_path = self.path + directory + "/densite_lu/"
				files = os.listdir(dir_path)
				if len(files) > 0 :
					#il y a au moins un fichier
					density_file = dir_path + "densite_hu.don"
					config_file = dir_path + "config_KIDS.don"
					self.list_img_density += [imd.Img_Density(density_file, config_file)]

		def extract_learn_imgs_from_first_img_density(self, img_density, nb_imgs) :
			if len(img_density.sub_imgs) < nb_imgs :
				#S'il on demande trop d'image qu'il n'y en as
				nb_imgs = len(img_density.sub_imgs)
			self.learn_imgs = img_density.sub_imgs[:nb_imgs]
			#on met à jour la variable contenant le nombre d'image d'apprentissage
			self.nb_learn_imgs = len(self.learn_imgs)

		def extract_test_imgs_from_lefted_img_density(self, list_img_density, nb_imgs) :
			for img_d in list_img_density :
				if len(img_d.sub_imgs) + len(self.test_imgs) > nb_imgs :
					#On dépasse le nombre d'image de test
					self.test_imgs += img_d.sub_imgs[:nb_imgs - len(self.test_imgs)]
				else :
					self.test_imgs += img_d.sub_imgs
			#on met à jour la variable contenant le nombre d'image de test
			self.learn_imgs = remove_duplicates(self.learn_imgs)
			self.nb_test_imgs = len(self.test_imgs)

		def remove_duplicates(imgs) :
			def are_imgs_equal(img1, img2) :
				for i in range(len(img1)) :
					line1 = img1[i]
					line2 = img2[i]
					for j in range(len(line1)) :
						if line1[j] != line2[j] :
							return False
				return True

			duplicates = []
			for i in range(len(imgs)) :
				for j in range(i + 1, len(imgs)) :
					if are_imgs_equal(imgs[i], imgs[j]) :
						duplicates += [j]

			return [imgs[i] for i in range(len(imgs)) if i not in duplicates]

		get_list_img_density(self)
		extract_learn_imgs_from_first_img_density(self, self.list_img_density[0], nb_learn_imgs)
		extract_test_imgs_from_lefted_img_density(self, self.list_img_density[1:], nb_test_imgs)
		self.nb_imgs = self.nb_test_imgs + self.nb_learn_imgs

	# ---------------------------------- Pré-Calcul sur les données ------------------------------


	def compute_similarity_between_all_learn_imgs(self) :
		print("Calcul des similartés entre toutes nos images d'entrainement...")
		avancement = 0
		fin = self.nb_learn_imgs*(self.nb_learn_imgs-1)/2
		progress_bar = ProgressBar(avancement, fin)
		for ind_first in range(self.nb_learn_imgs) :
			for ind_second in range(ind_first + 1, self.nb_learn_imgs) :
				score_sim = simy.similarity_between_two_imgs(self.learn_imgs[ind_first], self.learn_imgs[ind_second])
				self.dict_sim.set_similarity(ind_first, ind_second, score_sim)
				avancement += 1
				progress_bar.updateProgress(avancement, "")

	def compute_decision_tree(self) :
		print("Calcul de l'arbre de décision...")
		self.decision_tree.create_tree()


	# ------------------------------------ Save & Load --------------------------------------------

	def save(self, save_directory = "./data/") :
		print("Sauvegarde des images et similarités dans " + save_directory + " ...")

		def save_imgs(imgs, directory) :
			for i in range(len(imgs)) :
				file_name = directory + "img_" + str(i)
				with open(file_name, "w+") as f :
					f.write(str(imgs[i]))

		def create_env(save_directory, path_learn, path_test) :
			if not os.path.exists(save_directory) :
				os.makedirs(save_directory)
			if not os.path.exists(path_learn) :
				os.makedirs(path_learn)
			if not os.path.exists(path_test) :
				os.makedirs(path_test)

		path_learn = save_directory + "learn_imgs/"
		path_test = save_directory + "test_imgs/"
		create_env(save_directory, path_learn, path_test)

		save_imgs(self.learn_imgs, path_learn)
		save_imgs(self.test_imgs, path_test)
		self.dict_sim.save_similarity(save_directory)

	def load(self, save_directory = "./data/") :
		print("Chargement des images à partir de " + save_directory + "...")

		def is_int(value) :
			try :
				int(value)
				return True
			except :
				return False

		def load_img(file_name) :
			with open(file_name, "r") as f :
				res = f.read()
				return [[int(i) for i in a if is_int(i)] for a in res.split("]") if len(a) > 0]

		def load_all_imgs_in_directory(directory) :
			list_files = os.listdir(directory)
			if len(list_files) <= 0 :
				return []
			list_imgs = [None for _ in range(len(list_files))]
			avancement = 0
			fin = len(list_files)
			progress_bar = ProgressBar(avancement, fin)
			for f in list_files :
				tmp = f.split("_")
				if len(tmp) != 2 :
					#ce n'est pas une image car elles sont écrites sous la forme img_nb
					#on passe donc à l'image suivante
					continue
				if tmp[0] == "img" :
					#c'est une image
					ind_img = int(tmp[1])
					list_imgs[ind_img] = load_img(directory + f)
				avancement += 1
				progress_bar.updateProgress(avancement, "")
			return list_imgs

		path_learn = save_directory + "learn_imgs/"
		path_test = save_directory + "test_imgs/"
		path_similarity = save_directory + "similarity.don"

		print("Chargement des images d'apprentissage...")
		self.learn_imgs = load_all_imgs_in_directory(path_learn)
		print("Chargement des images de tests...")
		self.test_imgs = load_all_imgs_in_directory(path_test)
		self.dict_sim.load_similarity(path_similarity)

		self.nb_learn_imgs = len(self.learn_imgs)
		self.nb_test_imgs = len(self.test_imgs)
		self.nb_imgs = self.nb_test_imgs + self.nb_learn_imgs





if __name__ == "__main__" :

	def parse_arg(argv) :
		if "help" in argv :
			print("Arguments optionnels:")
			print("    path_save=my_path - Sauvegarde dans my_path, même si my_path n'existe pas")
			print("    path_load=my_path - Chargement des données à partir de my_path")
			exit()
		load = False	
		path_load = "../../../working_dir/"
		path_save = None
		for arg in argv :
			if arg[:10] == "path_load=" :
				path_load = arg[10:]
				load = True
			elif arg[:10] == "path_save=" :
				path_save = arg[10:]
		return load, path_load, path_save


	load, path_load, path_save = parse_arg(sys.argv)
	ed = Extract_Data(path_load, load = load, path_save = path_save)
	# print(ed.decision_tree)