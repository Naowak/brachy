#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-

import os

from ProgressBar import ProgressBar 
import Img_Density as imd
import Zoomed_Tree as zt
import Quartil as qt
import matplotlib.pyplot as plt

NB_LEARN_SLICE = 1
NB_TEST_SLICE = 14

class Main :
	def __init__(self, path, method) :

		self.path = path
		self.learn_imgs = list()
		self.test_imgs = list()
		self.nb_learn_imgs = 0
		self.nb_test_imgs = 0

		self.extract_img_density(NB_LEARN_SLICE, NB_TEST_SLICE)
		print(str(len(self.learn_imgs)) + " quarts images d'apprentissage chargées.")
		print(str(len(self.test_imgs)) + " images de tests chargées.")

		if method == "zt_dt" :
			self.zoomed_tree = zt.Zoomed_Tree(self.learn_imgs)
			self.zoomed_tree.predict_all_imgs(self.test_imgs, plot=False)

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
				for i in indice_test :
					images += list_img_density[i].extract_images()
				return images

			nb_slice = len(list_img_density)
			if nb_slice_learn + nb_slice_test > nb_slice :
				print("NB_SLICE = " + str(nb_slice))
				print("Error : pas asser de slice pour ce qui est demandé.")
				raise Exception

			indice_learn = get_indice_slice_learn(nb_slice, nb_slice_learn)
			indice_test = [i for i in list(range(nb_slice)) if i not in indice_learn]
			indice_test = indice_test[:nb_slice_test]

			quart_img_learn = extract_img_learn(list_img_density, indice_learn)[:500]
			img_test = extract_img_test(list_img_density, indice_test)
			return quart_img_learn, img_test

		print("Chargement des images à partir de " + self.path)
		list_img_density = get_list_img_density(self)
		self.learn_imgs, self.test_imgs = extract_and_seperate_img(list_img_density, nb_learn_slice, nb_test_slice)


if __name__ == '__main__':
	path = "../../../working_dir/"
	method = "zt_dt"
	main = Main(path, method)



