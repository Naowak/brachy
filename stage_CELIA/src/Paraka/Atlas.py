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

NB_LEARN_SLICE = 0
NB_TEST_SLICE = 4

class Save_Model :
	def __init__(self, main) :
		self.learn_imgs = main.learn_imgs
		self.first_indice_slice = main.first_indice_slice
		self.model = main.model
		self.nb_learn_imgs = main.nb_learn_imgs

	def copy_into(self, main) :
		main.learn_imgs = self.learn_imgs
		main.first_indice_slice = self.first_indice_slice
		main.model = self.model
		main.nb_learn_imgs = self.nb_learn_imgs

class Save_Test :
	def __init__(self, main) :
		self.test_imgs = main.test_imgs
		self.first_indice_slice = main.first_indice_slice
		self.nb_test_imgs = main.nb_test_imgs
		self.slices_test = main.slices_test

	def copy_into(self, main) :
		main.test_imgs = self.test_imgs
		main.first_indice_slice = self.first_indice_slice
		main.nb_test_imgs = self.nb_test_imgs
		main.slices_test = self.slices_test

class Atlas :
	def __init__(self, param) :

		self.learn_imgs = None
		self.test_imgs = None
		self.slices_test = None
		self.first_indice_slice = None
		self.model = None
		self.nb_learn_imgs = 0
		self.nb_test_imgs = 0
		self.sources = None

		#param
		self.method = None
		self.path = None
		self.split_method = None
		self.load_model = None
		self.save_model = None
		self.path_save = None
		self.symmetric_similarity = None
		self.path_test = None
		self.nb_img_for_each_slice = None
		self.plot = None
		self.ask_help = None
		self.save_result = None
		self.config_file = None
		self.density_file = None

		self.extract_param(param)
		if self.ask_help == "true" :
			self.help()
			exit()

	def run(self, plot=False, save_result=False) :

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

		def make_all_test(self, plot=False, save_result=False) :

			def test_slice(self, indice_slice, plot=False, save_result=False) :

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

					list_prediction = []
					list_score = []
					list_difference = []

					if len(img_from_slice) > 0 :
						result = self.model.predict_all_imgs(img_from_slice)
						list_prediction = result[0]
						list_score = result[1]
						list_difference = result[2]
					else :
						print("No image to predict")

					return list_prediction, list_score, list_difference

				def calcul_img_success(self, indice_slice, list_score) :

					def get_value_pixel(score) :
						return 255 * (score/(2*math.pi))

					def reverse_img_into_symmetric(img) :
						return [[img[i][j] for i in range(len(img))] for j in range(len(img[0]))]

					img_slice = self.slices_test[indice_slice]
					size_x, size_y = (len(img_slice), len(img_slice[0]))
					img_success = [[0 for i in range(size_x)] for j in range(size_y)]

					debut, fin = find_indice_debut_fin_img(self, indice_slice)
					for cpt, i in enumerate(list(range(debut, fin))) :
						(img, c_abs, c_ord) = self.test_imgs[i]
						img_success[c_abs][c_ord] = get_value_pixel(list_score[cpt])

					img_success = reverse_img_into_symmetric(img_success)

					return img_success

				def calcul_img_recompt(self, indice_slice, list_difference) :

					def do_recompt(img_recompt, difference, c_abs, c_ord) :
						size_x, size_y = (len(difference), len(difference[0]))
						translation_x, translation_y = (size_x/2, size_y/2)

						for i in range(size_x) :
							for j in range(size_y) :
								if difference[i][j] == 0 :
									#un point à recalculer
									img_recompt[c_abs + i - translation_x][c_ord + j - translation_y][0] += 1
								if difference[i][j] != -1 :
									img_recompt[c_abs + i - translation_x][c_ord + j - translation_y][1] += 1

					def transform_img_recompt(img_recompt) :
						size_x, size_y = (len(img_recompt), len(img_recompt[0]))
						for i in range(size_x) :
							for j in range(size_y) :
								if img_recompt[i][j][1] > 0 :
									img_recompt[i][j] = float(img_recompt[i][j][0]) / img_recompt[i][j][1] * 255
								else :
									img_recompt[i][j] = 0

					def reverse_img_into_symmetric(img) :
						return [[img[i][j] for i in range(len(img))] for j in range(len(img[0]))]

					img_slice = self.slices_test[indice_slice]
					size_x, size_y = (len(img_slice), len(img_slice[0]))
					img_recompt = [[[0, 0] for i in range(size_x)] for j in range(size_y)]

					debut, fin = find_indice_debut_fin_img(self, indice_slice)
					for cpt, i in enumerate(list(range(debut, fin))) :
						(img, c_abs, c_ord) = self.test_imgs[i]
						difference = list_difference[cpt]
						do_recompt(img_recompt, difference, c_abs, c_ord)
					transform_img_recompt(img_recompt)
					img_recompt = reverse_img_into_symmetric(img_recompt)

					return img_recompt

				def plot_result(self, indice_slice, list_score, list_difference) :
					img_success = calcul_img_success(self, indice_slice, list_score)
					img_recompt = calcul_img_recompt(self, indice_slice, list_difference)

					fig = plt.figure()
					fig.add_subplot(3, 1, 1)
					plt.imshow(self.slices_test[indice_slice])

					fig.add_subplot(3, 1, 2)
					plt.imshow(img_success)

					fig.add_subplot(3, 1, 3)
					plt.imshow(img_recompt)
					plt.show()

				def save_img_result(self, indice_slice, list_score, list_difference, dir_result="./result/") :
					img_success = calcul_img_success(self, indice_slice, list_score)
					img_recompt = calcul_img_recompt(self, indice_slice, list_difference)

					fig = plt.figure()
					fig.add_subplot(3, 1, 1)
					plt.imshow(self.slices_test[indice_slice])

					fig.add_subplot(3, 1, 2)
					plt.imshow(img_success)

					fig.add_subplot(3, 1, 3)
					plt.imshow(img_recompt)

					if not os.path.exists(dir_result) :
						os.makedirs(dir_result)
						
					name = dir_result + "result_slice_" + str(indice_slice) + ".png"
					fig.savefig(name)

				list_prediction, list_score, list_difference = make_predictions(self, indice_slice)
				if len(list_prediction) > 0 :
					if plot :
						plot_result(self, indice_slice, list_score, list_difference)
					if save_result :
						save_img_result(self, indice_slice, list_score, list_difference)
				else :
					print("Aucune image dans cette slice")
				return list_difference


			list_difference = []
			for i in range(len(self.slices_test)) :
				result = test_slice(self, i, plot, save_result)
				list_difference += result
			return list_difference

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
		result = make_all_test(self, plot, save_result)	
		return result, self.sources, self.slices_test[0] #ici result est une liste d'image représentant les zone à recalculer

	def fsave_model(self, dir_save) :
		print("Sauvegarde du modèle dans " + dir_save + "...")

		#dossier non existant, on le créer
		if not os.path.exists(dir_save) :
			os.makedirs(dir_save)

		file_model = dir_save + "model.dat"
		file_img_test = dir_save + "tests.dat"

		save_model = Save_Model(self)
		save_test = Save_Test(self)
		#on sauvegade différements les images de tests du model

		with open(file_model, "w+") as output :
			pickle.dump(save_model, output, pickle.HIGHEST_PROTOCOL)

		with open(file_img_test, "w+") as output :
			pickle.dump(save_test, output, pickle.HIGHEST_PROTOCOL)

	def fload_model(self, dir_load) :

		def load_train(self, dir_load) :
			print("Chargement du modèle à partir de " + dir_load + "...")
			file_model = dir_load + "model.dat"
			with open(file_model, "r") as input :
				save_model = pickle.load(input)
				save_model.copy_into(self)

		def load_test(self, dir_load) :

			def load(self, file_img_test) :
				with open(file_img_test, "r") as input :
					save_test = pickle.load(input)
					save_test.copy_into(self)

			if self.path_test != None :
				# On charge une sauvgarde d'image de test
				print("Chargement des images de tests à partir de " + self.path_test + "...")
				file_img_test = self.path_test
				load(self, file_img_test)

			elif self.config_file and self.density_file :
				self.extract_slice_test()

			else :
				file_img_test = dir_load + "tests.dat"
				load(self, file_img_test)

		load_train(self, dir_load)
		load_test(self, dir_load)

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

		def extract_and_seperate_img(list_img_density, nb_slice_learn, nb_slice_test, nb_img_slice) :

			def get_indice_slice_learn(size_list_img_density, nb_slice_learn) :
				parcour = list(range(-nb_slice_learn//2+1, nb_slice_learn//2+1, 1))
				indices = [size_list_img_density//2 + elem for elem in parcour]
				return indices

			def extract_img_learn(list_img_density, indice_learn, nb_img_slice) :
				images = list()
				for i in indice_learn :
					images += list_img_density[i].extract_quart_images()[:nb_img_slice]
				return images

			def extract_img_test(list_img_density, indice_test, nb_img_slice) :
				images = list()
				first_indice_for_each_slice = [0]
				for i in indice_test :
					first_indice_for_each_slice += [len(images)]
					images += list_img_density[i].extract_images()[:nb_img_slice]
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

			quart_img_learn = extract_img_learn(list_img_density, indice_learn, nb_img_slice)
			result = extract_img_test(list_img_density, indice_test, nb_img_slice)
			img_test = result[0]
			first_indice_slice = result[1]

			slices_test = [list_img_density[i].extract_slice() for i in indice_test]
			return quart_img_learn, img_test, slices_test, first_indice_slice

		
		print("Chargement des images à partir de " + self.path)
		list_img_density = get_list_img_density(self)
		result = extract_and_seperate_img(list_img_density, nb_learn_slice, nb_test_slice, self.nb_img_for_each_slice)

		self.learn_imgs = result[0]
		self.test_imgs = result[1]
		self.slices_test = result[2]
		self.first_indice_slice = result[3]

		print(str(len(self.learn_imgs)) + " quarts images d'apprentissage chargées.")
		print(str(len(self.test_imgs)) + " images de tests chargées.")

	def extract_slice_test(self) :

		def get_img_density(self) :
			img_density = None
			if self.config_file and self.density_file :
				print("Chargement des images à partir de " + self.density_file + " et " + self.config_file) 
				img_density = imd.Img_Density(self.density_file, self.config_file)
			return img_density
		
		def extract_test_img(self, img_density) :
			imgs = img_density.extract_images()
			return imgs

		img_density = get_img_density(self)
		self.test_imgs = extract_test_img(self, img_density)
		self.slices_test = [img_density.extract_slice()]
		self.first_indice_slice = [0, len(self.test_imgs)]
		self.sources = img_density.extract_sources()

	def extract_param(self, options) :

		def take_value(param, name_param, default_value) :
			try :
				if param[name_param] :
					return param[name_param]
			except KeyError :
				return default_value

		param = dict()
		args = options.split(" ")
		for elem in args :
			tab = elem.split("=")
			param[tab[0]] = tab[1]

		self.method = take_value(param, "method", "zt_dt")
		self.split_method = take_value(param, "split_method", "random")
		self.load_model = take_value(param, "load_model", "false")
		self.save_model = take_value(param, "save_model", "false")
		self.path_save = take_value(param, "path_save", "./save/")
		self.path = take_value(param, "path", "../../../working_dir/")
		self.symmetric_similarity = take_value(param, "symmetric", "true")
		self.path_test = take_value(param, "path_test", None)
		self.nb_img_for_each_slice = int(take_value(param, "nb_img_slice", 10000))
		self.plot = take_value(param, "plot", "false")
		self.ask_help = take_value(param, "help", "false")
		self.save_result = take_value(param, "save_result", "true")
		self.config_file = take_value(param, "config_file", "")
		self.density_file = take_value(param, "density_file", "")

	def help(self) :
		print("method=value --- values = [zt_dt, dt]")
		print("split_method=value --- values = [random, farest_point]")
		print("load_model=value --- values = [false, true]")
		print("save_model=value --- values = [false, true]")
		print("path_save=value --- default = ./save/")
		print("path=value --- default = ../../../working_dir/")
		print("symmetric=value --- values = [true, false]")
		print("path_test=value --- default = None")
		print("nb_img_slice=value --- default = 10000")
		print("plot=value --- value = [false, true]")
		print("save_result=value --- value = [true, false]")
		print("config_file=value --- value = \"\"")
		print("density_file=value --- value = \"\"")

if __name__ == '__main__':

	main = Atlas(sys.argv)
	plot = main.plot == "true"
	save_result = main.save_result == "true"
	main.run(plot = plot, save_result = save_result)



