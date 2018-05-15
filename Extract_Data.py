#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-

import Img_Density as imd
import Similarity as simy
import Decision_Tree as dt
from ProgressBar import ProgressBar
import os
import sys
import time
from matplotlib import pyplot as plt


NB_LEARN_IMGS = 1500
NB_TEST_IMGS = 2000


class Extract_Data :

	def __init__(self, path, load = False, path_save = None, nb_learn_imgs = NB_LEARN_IMGS, nb_test_imgs = NB_TEST_IMGS) :
		self.path = path
		self.list_img_density = list()
		self.learn_imgs = list()
		self.test_imgs = list()
		self.nb_imgs = 0
		self.nb_learn_imgs = 0
		self.nb_test_imgs = 0
		self.max_similarity = 0
		self.dict_sim = None

		if load == False :
			if nb_learn_imgs == 0 :
				print("Impossible d'effectuer un apprentissage avec 0 images d'entrainement.")
				exit()
			self.extract_img_density(nb_learn_imgs, nb_test_imgs)
			self.dict_sim = simy.Dict_Sim(self.nb_imgs)
			self.compute_similarity_between_all_learn_imgs()
			# self.save(path_save)
		else :
			self.dict_sim = simy.Dict_Sim()
			self.load(path)

		if path_save != None :
			self.save(path_save)

		self.decision_tree = dt.Decision_Tree(None, list(range(self.nb_learn_imgs)), self.dict_sim, self.learn_imgs, self.test_imgs)
		self.compute_decision_tree()


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
			self.learn_imgs = remove_duplicates(self.learn_imgs)
			self.nb_learn_imgs = len(self.learn_imgs)

		def extract_test_imgs_from_lefted_img_density(self, list_img_density, nb_imgs) :
			for img_d in list_img_density :
				if len(img_d.sub_imgs) + len(self.test_imgs) > nb_imgs :
					#On dépasse le nombre d'image de test
					self.test_imgs += img_d.sub_imgs[:nb_imgs - len(self.test_imgs)]
				else :
					self.test_imgs += img_d.sub_imgs
			#on met à jour la variable contenant le nombre d'image de test
			self.test_imgs = remove_duplicates(self.test_imgs)
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

			print("Suppression des duplicatas...")
			duplicates = []
			nb = len(imgs)
			avancement = 0
			fin = nb*(nb-1)/2
			progress_bar = ProgressBar(avancement, fin)
			for i in range(nb) :
				for j in range(i + 1, nb) :
					if are_imgs_equal(imgs[i], imgs[j]) :
						duplicates += [j]
					avancement += 1
				progress_bar.updateProgress(avancement, "")

			imgs_without_duplicates = [imgs[i] for i in range(nb) if i not in duplicates]
			return imgs_without_duplicates

		print("Chargement des images à partir de " + self.path)
		get_list_img_density(self)
		learn_img_density = self.list_img_density[9]
		test_img_density = self.list_img_density[:9] + self.list_img_density[10:]
		extract_learn_imgs_from_first_img_density(self, learn_img_density, nb_learn_imgs)
		extract_test_imgs_from_lefted_img_density(self, test_img_density, nb_test_imgs)
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
		self.decision_tree.display_stats()

	# --------------------------------- Prédiction ---------------------------------------------

	def predict_for_all_test_imgs(self) :

		def predict_and_compare_to_iterative_result(self, plot=False) :
			def find_iterative(self, ind_test) :
				score = [simy.similarity_between_two_imgs(self.test_imgs[ind_test], self.learn_imgs[i]) for i in range(self.nb_learn_imgs)]
				closest = None
				max_sim = -10000
				for i,s in enumerate(score) :
					if s > max_sim :
						max_sim = s
						closest = i
				return closest, max_sim

			def plot_result(self, ind_test, ind_img, ind_iterative) :
				fig = plt.figure()
				fig.add_subplot(3, 2, 1)
				plt.imshow(self.test_imgs[ind_test])

				fig.add_subplot(3, 2, 3)
				plt.imshow(self.learn_imgs[ind_img])

				fig.add_subplot(3, 2, 4)
				mat = simy.calcul_matrix_similarity(self.test_imgs[ind_test], self.learn_imgs[ind_img])
				plt.imshow(mat)

				fig.add_subplot(3, 2, 5)
				plt.imshow(self.learn_imgs[ind_iterative])

				fig.add_subplot(3, 2, 6)
				mat = simy.calcul_matrix_similarity(self.test_imgs[ind_test], self.learn_imgs[ind_iterative])
				plt.imshow(mat)

				plt.show()

			for i in range(self.nb_test_imgs) :
				t1 = time.time()
				closest_img, score_sim, dt, nb_visite = self.decision_tree.predict_closest_img(i)
				t2 = time.time()
				iterative_closest, max_sim = find_iterative(self, i)
				t3 = time.time()
				print("Score predict : " + str(score_sim))
				print("Score iterative : " + str(max_sim))
				print("Temps predict : " + str(t2 - t1))
				print("Temps iterative : " + str(t3-t2))
				print("Nombre de visite : " + str(nb_visite) + "\n")
				
				if plot :
					plot_result(self, i, closest_img, iterative_closest)

		def predict_only(self, plot = True) :

			def plot_result(self, ind_prediction, ind_test) :
				fig = plt.figure()
				fig.add_subplot(2, 1, 1)
				print(self.test_imgs[ind_test])
				plt.imshow(self.test_imgs[ind_test])
				fig.add_subplot(2, 1, 2)
				plt.imshow(self.learn_imgs[ind_prediction])
				plt.show()

			nb_visite = 0

			for i in range(self.nb_test_imgs) :
				t1 = time.time()
				prediction, score, dt, visites = self.decision_tree.predict_closest_img(i)
				nb_visite += visites
				t2 = time.time()
				print("Prédiction image test " + str(i))
				print("Score Prédiction : " + str(score))
				print("Temps pour la prédiction : " + str(t2 - t1))
				print("Nombre de calcul de similarité : " + str(visites) + "\n")

				if plot :
					plot_result(self, prediction, i)

			print("Nombre moyen de calcul de similarité par image : " + str(float(nb_visite)/self.nb_test_imgs))

		begin_predictions = time.time()
		# predict_only(self, plot=False)
		predict_and_compare_to_iterative_result(self, plot=True)
		end_predictions = time.time()
		temps_predictions = end_predictions - begin_predictions
		print("Temps de l'ensemble des prédictions : " + str(temps_predictions))
		print("Temps moyen par prédiciton : " + str(temps_predictions / self.nb_test_imgs))

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
				lines = res.split("[")
				img = []
				for line in lines :
					my_line = []
					line = line.replace(']', '')
					line = line.replace(",", '')
					for elem in line.split(" ") :
						if is_int(elem) :
							my_line += [int(elem)]
					if len(my_line) > 0 :
			 			img += [my_line]
			 	return img

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
		self.learn_imgs = load_all_imgs_in_directory(path_learn)[:NB_LEARN_IMGS]
		print("Chargement des images de tests...")
		self.test_imgs = load_all_imgs_in_directory(path_test)[:NB_TEST_IMGS]
		print("Chargement des similarités...")
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

	# def test_sim(ed) :
	# 	for i in range(ed.nb_learn_imgs) :
	# 		for j in range(i + 1, ed.nb_learn_imgs) :
	# 			sim = simy.similarity_between_two_imgs(ed.learn_imgs[i], ed.learn_imgs[j])
	# 			if sim != ed.dict_sim.get_similarity(i, j) :
	# 				print(i, j)
	# 				print(sim, ed.dict_sim.get_similarity(i,j))
	# 				return False
	# 	return True

	load, path_load, path_save = parse_arg(sys.argv)
	ed = Extract_Data(path_load, load = load, path_save = path_save)
	# test_sim(ed)
	# print(ed.decision_tree)
	ed.predict_for_all_test_imgs()