class Quartil :
	"""Classe utilisée pour représenter un quart d'image classique dans
	notre base de donnée"""
	
	def __init__(self, img) :

		def copy_img(img) :
			tab = []
			for i in range(len(img)) :
				tab += [list(img[i])]
			return tab

		def symetric_img(img) :
			len_first = len(img)
			len_second = len(img[0])
			return [[img[j][i] for j in range(len_second)] for i in range(len_first)]

		self.img_one = copy_img(img)
		self.img_two = symetric_img(img)

	def __eq__(self, img) :

		def are_imgs_equal(img1, img2) :
			for i in range(len(img1)) :
				line1 = img1[i]
				line2 = img2[i]
				for j in range(len(line1)) :
					if line1[j] != line2[j] :
						return False
			return True

		return are_imgs_equal(self.img_one, img) \
			or are_imgs_equal(self.img_two, img)