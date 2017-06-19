# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
from contourage import *

########################
# Dataset de polygones #
########################

# Polygone regulier convexe
pol_convexe = [[4.28, 2.28], [4.31, 2.63], [4.25, 2.98], [4.13, 3.31], [3.94, 3.61], \
               [3.69, 3.86], [3.40, 4.05], [3.07, 4.18], [2.72, 4.24], [2.37, 4.22], \
               [2.03, 4.14], [1.71, 3.98], [1.43, 3.76], [1.21, 3.49], [1.05, 3.17], \
               [0.95, 2.83], [0.93, 2.48], [0.98, 2.13], [1.11, 1.80], [1.30, 1.50], \
               [1.55, 1.25], [1.84, 1.06], [2.17, 0.93], [2.52, 0.87], [2.87, 0.88], \
               [3.21, 0.97], [3.53, 1.13], [3.8, 1.35], [4.03, 1.62], [4.19, 1.94], [4.28,2.28]]

# Polygone concave
pol_concave = [[1.30, 3.62], [1.56, 3.62], [1.83, 3.59], [2.16, 3.55], [2.50, 3.50], \
               [2.74, 3.42], [2.96, 3.36], [3.18, 3.28], [3.41, 3.12], [3.53, 2.94], \
               [3.56, 2.74], [3.51, 2.57], [3.43, 2.46], [3.29, 2.48], [3.14, 2.58], \
               [2.99, 2.69], [2.84, 2.78], [2.69, 2.86], [2.54, 2.88], [2.42, 2.80], \
               [2.39, 2.67], [2.42, 2.55], [2.47, 2.43], [2.54, 2.31], [2.62, 2.16], \
               [2.70, 2.05], [2.82, 1.92], [2.87, 1.80], [2.82, 1.68], [2.70, 1.65], \
               [2.56, 1.69], [2.44, 1.75], [2.31, 1.82], [2.15, 1.90], [2.00, 2.00], \
               [1.88, 2.06], [1.76, 2.15], [1.65, 2.24], [1.52, 2.37], [1.44, 2.48], \
               [1.34, 2.61], [1.28, 2.71], [1.19, 2.85], [1.11, 2.97], [1.05, 3.10], \
               [1.02, 3.22], [1.01, 3.42], [1.14, 3.56], [1.30, 3.62]]
    

# Ugly contourage
pol_ugly  = [[0.6, 1.9], [0.6, 3.7], [1.7, 4.6], [3.1, 5.3], [4.7, 5.1], \
             [4.8, 4.3], [4.3, 3.8], [3.1, 3.8], [2.3, 3.2], [3.0, 2.3], \
             [4.9, 2.1], [4.9, 0.8], [3.2, 0.7], [2.0, 0.9], [0.6,1.9]]


#########
# Tests #
#########


def test_contourage(contourage):
    # Creation artificielle maillage et contourage
    maillage_x = np.linspace(0, 5, 20)
    maillage_y = np.linspace(0, 5, 20)
    maillage_z = np.linspace(0, 1, 1)
    maillage = (maillage_x, maillage_y, maillage_z)
    n_points = (20, 20, 1)
    dimensions = (5, 5, 1)

    # Calcul de l'appartenance au contourage pour le maillage
    appartenance_contourage = get_appartenance_contourage(n_points, maillage, contourage)
    plot_appartenance_contourage(n_points, dimensions, maillage, appartenance_contourage, contourage)


def main():
    test_contourage(pol_convexe)
    test_contourage(pol_ugly)
    test_contourage(pol_concave)
    

if __name__ == "__main__":
    main()
