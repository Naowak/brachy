#!/usr/lib/env python2.7
#-*- coding: utf-8 -*-

import Similarity as simy
import math

class Stats :

	def __init__(self, nb_img_learn) :
		self.nb_img_done = 0
		self.score_sum = 0
		self.max_score_sim = simy.max_score_similarity()
		self.time_sum = 0
		self.nb_img_learn = nb_img_learn

	def add_test(self, score, time) :
		self.nb_img_done += 1
		self.score_sum += score
		self.time_sum += time

	def __str__(self) :

		def make_stats(self) :
			temps_moyen = self.time_sum/self.nb_img_done
			score_moyen = self.score_sum/self.nb_img_done
			score_pourcentage_moyen = (score_moyen / (2*math.pi)) * 100
			score_pourcentage_moyen -= score_pourcentage_moyen % 0.01

			return temps_moyen, score_moyen, score_pourcentage_moyen

		def display(self, temps_moyen, score_moyen, score_pourcentage_moyen) :
			string = "Modèle appris sur " + str(self.nb_img_learn) + " quarts d'images.\n"
			string += "Test réalisé sur " + str(self.nb_img_done) + " images de test.\n"
			string += "Temps moyen : " + str(temps_moyen) + " secondes.\n"
			string += "Score moyen : " + str(score_moyen) + " ---> " + str(score_pourcentage_moyen) + "%."
			return string

		temps_moyen, score_moyen, score_pourcentage_moyen = make_stats(self)
		string = display(self, temps_moyen, score_moyen, score_pourcentage_moyen)
		return string