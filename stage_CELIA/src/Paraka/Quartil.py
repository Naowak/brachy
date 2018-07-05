#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-

class Quartil :

	def __init__(self, img, filename_dose, location, pos_source) :
		self.my_img = img
		self.filename_dose = filename_dose
		self.location = location # location = "NO", "NE", "SO", "SE"
		self.source = pos_source
		all_slice_dose = self.extract_dose()
		self.dose = self.extract_dose_zone_influence(all_slice_dose)
		print(self.dose)

	def extract_dose(self) :
		size = len(self.my_img)
		dose_all_img = None

		with open(self.filename_dose, "r") as f :
			for line in f :
				tab = [elem for elem in line.split(" ") if elem != ""]
				if line[:2] == " #" :
					if "NBX" in tab :
						nbx = int(tab[tab.index("NBX") + 2])
						nby = int(tab[tab.index("NBY") + 2])
						dose_all_img = [[0 for j in range(nby)] for i in range(nbx)]
				elif len(tab) == 7 :
						x = int(tab[4]) - 1
						y = int(tab[5]) - 1
						dose = int(tab[3])
						dose_all_img[x][y] = dose
		return dose_all_img

	def extract_dose_zone_influence(self, all_slice_dose) :

		def rotation(img, nb) :
			""" Effectue nb rotation à 90 degrees sur l'images"""
			def rotate_90_degrees(img) :
				tmp = list(zip(*reversed(img)))
				return [list(line) for line in tmp]
			for _ in range(nb) :
				img = rotate_90_degrees(img)
			return img

		rayon = len(self.my_img)
		quart_dose = None
		x_source = self.source[0]
		y_source = self.source[1]

		if self.location == "NO" :
			cols = all_slice_dose[x_source - rayon : x_source]
			quart_dose = [col[y_source - rayon : y_source] for col in cols]
			quart_dose = rotation(quart_dose, 2)

		elif self.location == "NE" :
			cols = all_slice_dose[x_source : x_source + rayon]
			quart_dose = [col[y_source - rayon : y_source] for col in cols]
			quart_dose = rotation(quart_dose, 1)

		elif self.location == "SO" :
			cols = all_slice_dose[x_source - rayon : x_source]
			quart_dose = [col[y_source : y_source + rayon] for col in cols]

		elif self.location == "SE" :
			cols = all_slice_dose[x_source : x_source + rayon]
			quart_dose = [col[y_source : y_source + rayon] for col in cols]
			quart_dose = rotation(quart_dose, 3)

		return quart_dose





	def __len__(self) :
		return len(self.my_img)

	def __getitem__(self, key) :
		return self.my_img[key]

	def __setitem__(self, key, item) :
		self.my_img[key] = item

	def __str__(self) :
		string = "Filename : " + self.filename_dose + "\n"
		string += "Location : " + self.location
		string += "Source : " + str(self.source)
		string += "Dose :\n" + str(self.dose)
		return string

