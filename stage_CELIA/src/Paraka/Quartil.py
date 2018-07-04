class location :
	NE = "Nord Est"
	NO = "Nord Ouest"
	SO = "Sud Ouest"
	SE = "Sud Est"


class Quartil :

	def __init__(self, img, filename_dose, location) :
		self.my_img = img
		self.filename_dose = filename_dose
		self.location = location

	def __len__(self) :
		return len(self.my_img)

	def __getitem__(self, key) :
		return self.my_img[key]

	def __setitem__(self, key, item) :
		self.my_img[key] = item

	def __str__(self) :
		string = "Filename : " + self.filename_dose + "\n"
		string += "Location : " + self.location
		return string