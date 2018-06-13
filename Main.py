#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-

import os

from ProgressBar import ProgressBar 
import Img_Density as imd
import Zoomed_Tree as zt
import Decision_Tree as dt
import matplotlib.pyplot as plt
import Similarity as simy
import sys
import cPickle as pickle
import math

NB_LEARN_SLICE = 1
NB_TEST_SLICE = 5


class Main :
	def __init__(self) :

		self.learn_imgs = None
		self.test_imgs = None
		self.slices_test = None
		self.first_indice_slice = None
		self.model = None
		self.nb_learn_imgs = 0
		self.nb_test_imgs = 0

		self.method = None
		self.path = None
		self.split_method = None
		self.load_model = None
		self.save_model = None
		self.path_save = None
		self.symmetric_similarity = None
		self.extract_param(sys.argv)

	def run(self) :

		def create_zt_dt_method(self) :
			self.extract_img_density(NB_LEARN_SLICE, NB_TEST_SLICE)
			self.model = zt.Zoomed_Tree(self.learn_imgs, \
				split_method = self.split_method, \
				symmetric_similarity = self.symmetric_similarity)

		def create_dt_method(self) :

			def compute_similarity(self) :

				def compute_similarity_img1_img2(self, img1, img2) :
					if self.symmetric_similarity == "true" :
						return simy.symmetric_similarity_between_two_imgs(img1, img2)
					return simy.similarity_between_two_imgs(img1, img2)

				nb_imgs = len(self.learn_imgs)
				self.dict_sim = simy.Dict_Sim(nb_imgs)
				avancement = 0
				fin = (nb_imgs * (nb_imgs - 1)) / 2
				progress_bar = ProgressBar(avancement, fin)
				for i in range(nb_imgs) :
					for j in range(i+1, nb_imgs) :
						img1 = self.learn_imgs[i]
						img2 = self.learn_imgs[j]
						score_sim, inter_sim = compute_similarity_img1_img2(self, img1, img2)
						self.dict_sim.set_similarity(i, j, score_sim)
						avancement += 1
						progress_bar.updateProgress(avancement, "")

			self.extract_img_density(NB_LEARN_SLICE, NB_TEST_SLICE)
			nb_imgs = len(self.learn_imgs)
			list_ind_img = list(range(nb_imgs))
			self.dict_sim = None
			compute_similarity(self)
			self.model = dt.Decision_Tree(None, list_ind_img, self.dict_sim, self.learn_imgs, None, \
				split_method = self.split_method, \
				symmetric_similarity = self.symmetric_similarity)
			self.model.create_tree()

		def make_all_test(self, plot=False) :

			def test_slice(self, indice_slice, plot=False) :

				def find_indice_debut_fin_img(self, indice_slice) :
					debut = self.first_indice_slice[indice_slice]
					fin = self.first_indice_slice[indice_slice + 1] 
					#on ne dépasse pas car la dernière valeur est le nombre d'images
					return debut, fin

				def make_predictions(self, indice_slice) :
					print("Test de la slice " + str(indice_slice))

					img_from_slice = list()
					debut, fin = find_indice_debut_fin_img(self, indice_slice)
					for i in range(debut, fin) :
						(img, c_abs, c_ord) = self.test_imgs[i]
						img_from_slice += [img]

					result = self.model.predict_all_imgs(img_from_slice)
					list_prediction = result[0]
					list_score = result[1]
					list_difference = result[2]

					return list_prediction, list_score, list_difference

				def calcul_img_success(self, indice_slice, list_score) :

					def get_value_pixel(score) :
						return 255 * (score/(2*math.pi))

					img_slice = self.slices_test[indice_slice]
					size_x, size_y = (len(img_slice), len(img_slice[0]))
					img_success = [[0 for i in range(size_x)] for j in range(size_y)]

					debut, fin = find_indice_debut_fin_img(self, indice_slice)
					for cpt, i in enumerate(list(range(debut, fin))) :
						(img, c_abs, c_ord) = self.test_imgs[i]
						img_success[c_abs][c_ord] = get_value_pixel(list_score[cpt])

					return img_success

				list_prediction, list_score, list_difference = make_predictions(self, indice_slice)
				if plot :
					img_success = calcul_img_success(self, indice_slice, list_score)
					plt.imshow(img_success)
					plt.show()

			for i in range(NB_TEST_SLICE) :
				test_slice(self, i, plot)

		if self.load_model == "true" :
				self.fload_model(self.path)
		else :
			if self.method == "zt_dt" :
				create_zt_dt_method(self)
			elif self.method == "dt" :
				create_dt_method(self)

		#sauvegarde des données
		if self.save_model == "true" :
			self.fsave_model(self.path_save)

		#test des données
		# self.model.predict_all_imgs(self.test_imgs)	
		make_all_test(self, plot=True)	

	def fsave_model(self, dir_save) :
		print("Sauvegarde du modèle dans " + dir_save + "...")

		#dossier non existant, on le créer
		if not os.path.exists(dir_save) :
			os.makedirs(dir_save)

		file_img_learn = dir_save + "imgs.dat"
		file_img_test = dir_save + "tests.dat"
		file_tree = dir_save + "tree.dat"

		with open(file_img_learn, "w+") as output :
			pickle.dump(self.learn_imgs, output, pickle.HIGHEST_PROTOCOL)

		with open(file_img_test, "w+") as output :
			pickle.dump(self.test_imgs, output, pickle.HIGHEST_PROTOCOL)

		with open(file_tree, "w+") as output :
			pickle.dump(self.model, output, pickle.HIGHEST_PROTOCOL)

	def fload_model(self, dir_load) :
		print("Chargement du modèle à partir de " + dir_load + "...")
		file_img_learn = dir_load + "imgs.dat"
		file_img_test = dir_load + "tests.dat"
		file_tree = dir_load + "tree.dat"

		with open(file_img_learn, "r") as input :
			self.learn_imgs = pickle.load(input)

		with open(file_img_test, "r") as input :
			self.test_imgs = pickle.load(input)

		with open(file_tree, "r") as input :
			self.model = pickle.load(input)

	def extract_img_density(self, nb_learn_slice, nb_test_slice) :

		def get_list_img_density(self) :
			directories = os.listdir(self.path)
			list_img_density = list()
			for directory in directories :
				dir_path = self.path + directory + "/densite_lu/"
				files = os.listdir(dir_path)
				if len(files) > 0 :
					#il y a au moins un fichier
					density_file = dir_path + "densite_hu.don"
					config_file = dir_path + "config_KIDS.don"
					list_img_density += [imd.Img_Density(density_file, config_file)]
			return list_img_density

		def extract_and_seperate_img(list_img_density, nb_slice_learn, nb_slice_test) :

			def get_indice_slice_learn(size_list_img_density, nb_slice_learn) :
				parcour = list(range(-nb_slice_learn//2+1, nb_slice_learn//2+1, 1))
				indices = [size_list_img_density//2 + elem for elem in parcour]
				return indices

			def extract_img_learn(list_img_density, indice_learn) :
				images = list()
				for i in indice_learn :
					images += list_img_density[i].extract_quart_images()
				return images

			def extract_img_test(list_img_density, indice_test) :
				images = list()
				first_indice_for_each_slice = list()
				for i in indice_test :
					first_indice_for_each_slice += [len(images)]
					images += list_img_density[i].extract_images()
				first_indice_for_each_slice += [len(images)] #limites pour le slice par slice
				return images, first_indice_for_each_slice

			nb_slice = len(list_img_density)
			if nb_slice_learn + nb_slice_test > nb_slice :
				print("NB_SLICE = " + str(nb_slice))
				print("Error : pas asser de slice pour ce qui est demandé.")
				raise Exception

			indice_learn = get_indice_slice_learn(nb_slice, nb_slice_learn)
			indice_test = [i for i in list(range(nb_slice)) if i not in indice_learn]
			indice_test = indice_test[:nb_slice_test]

			quart_img_learn = extract_img_learn(list_img_density, indice_learn)[:50]
			result = extract_img_test(list_img_density, indice_test)
			img_test = result[0]
			first_indice_slice = result[1]

			slices_test = [list_img_density[i].extract_slice() for i in indice_test]
			return quart_img_learn, img_test, slices_test, first_indice_slice

		print("Chargement des images à partir de " + self.path)
		list_img_density = get_list_img_density(self)
		result = extract_and_seperate_img(list_img_density, nb_learn_slice, nb_test_slice)

		self.learn_imgs = result[0]
		self.test_imgs = result[1]
		self.slices_test = result[2]
		self.first_indice_slice = result[3]

		print(str(len(self.learn_imgs)) + " quarts images d'apprentissage chargées.")
		print(str(len(self.test_imgs)) + " images de tests chargées.")

	def extract_param(self, argv) :

		def take_value(param, name_param, default_value) :
			try :
				if param[name_param] :
					return param[name_param]
			except KeyError :
				return default_value

		param = dict()
		for elem in argv[1:] :
			tab = elem.split("=")
			param[tab[0]] = tab[1]

		self.method = take_value(param, "method", "zt_dt")
		self.split_method = take_value(param, "split_method", "random")
		self.load_model = take_value(param, "load_model", "false")
		self.save_model = take_value(param, "save_model", "false")
		self.path_save = take_value(param, "path_save", "./save/")
		self.path = take_value(param, "path", "../../../working_dir/")
		self.symmetric_similarity = take_value(param, "symmetric", "true")

if __name__ == '__main__':

	main = Main()
	main.run()



