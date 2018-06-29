import matplotlib
from matplotlib import pyplot as plt
from matplotlib import path as mp

def define_shape(coords_mm) :
	coords = []
	for c in coords_mm :
		coords += [[c[0]/10, c[1]/10]]
	return mp.Path(coords)

def value_point(shapes, point) :
	for i, s in enumerate(shapes) :
		if s.contains_point(point) :
			return float(i) + 1
	return 0

carre = define_shape([[40, 40], [60, 40], [60, 60], [40, 60]])
tri = define_shape([[80, 80], [120, 90], [90, 120]])
shapes = [carre, tri]
tab = [[value_point(shapes, [i, j]) for i in range(15)] for j in range(15)]
plt.imshow(tab)
plt.show()