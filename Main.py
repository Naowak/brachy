#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-

import os

from ProgressBar import ProgressBar 
import Img_Density as imd
import Zoomed_Tree as zt
import Quartil as qt

NB_LEARN_IMG = 500
NB_TEST_IMG = 500

class Main :
	def __init__(self, path, method) :

		self.path = path
		self.learn_imgs = list()
		self.test_imgs = list()
		self.nb_learn_imgs = 0
		self.nb_test_imgs = 0

		self.extract_img_density(NB_LEARN_IMG, NB_TEST_IMG)

		if method == "zt_dt" :
			self.zoomed_tree = zt.Zoomed_Tree(self.learn_imgs)
			self.zoomed_tree.predict_all_imgs(self.test_imgs, plot=False)

	def extract_img_density(self, nb_learn_imgs, nb_test_imgs) :

		def transform_into_quartil(imgs) :
			list_quartil = list()
			for i, img in enumerate(imgs) :
				list_quartil += [qt.Quartil(img, i)]
			return list_quartil

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

		def extract_learn_imgs_from_first_img_density(self, img_density, nb_imgs) :
			if len(img_density.sub_imgs) < nb_imgs :
				#S'il on demande trop d'image qu'il n'y en as
				nb_imgs = len(img_density.sub_imgs)
			self.learn_imgs = img_density.sub_imgs[:nb_imgs]
			#on met à jour la variable contenant le nombre d'image d'apprentissage
			# self.learn_imgs = transform_into_quartil(self.learn_imgs)
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
			# self.test_imgs = transform_into_quartil(self.test_imgs)
			self.test_imgs = remove_duplicates(self.test_imgs)
			self.nb_test_imgs = len(self.test_imgs)

		def remove_duplicates(imgs) :
			print("Suppression des duplicatas...")
			duplicates = []
			nb = len(imgs)
			avancement = 0
			fin = nb*(nb-1)/2
			progress_bar = ProgressBar(avancement, fin)
			for i in range(nb) :
				for j in range(i + 1, nb) :
					if imgs[i] == imgs[j] :
						duplicates += [j]
					avancement += 1
				progress_bar.updateProgress(avancement, "")

			imgs_without_duplicates = [imgs[i] for i in range(nb) if i not in duplicates]
			return imgs_without_duplicates

		print("Chargement des images à partir de " + self.path)
		list_img_density = get_list_img_density(self)
		learn_img_density = list_img_density[9]
		test_img_density = list_img_density[:9] + list_img_density[10:]
		extract_learn_imgs_from_first_img_density(self, learn_img_density, nb_learn_imgs)
		extract_test_imgs_from_lefted_img_density(self, test_img_density, nb_test_imgs)


if __name__ == '__main__':
	path = "../../../working_dir/"
	method = "zt_dt"
	main = Main(path, method)



