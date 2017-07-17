# -*- coding: utf-8 -*-
import sys
import numpy as np
import matplotlib.pyplot as plt
from contourage import *

# Parametres coupe
xcutcm = np.array([2.5])
ycutcm = 2.5                  
zcutcm = 0.5


########################### Recuperation des informations ###########################


def get_header_info(f):
    """ Parse les informations contenues dans le header du fichier .dat
    [Return] Quadruplet (coord, dim_vector, nb_vector, maillage)

    [Params]
    f : descripteur de fichier
    """
    coord = np.zeros([6])

    for i in range (10):

        a = f.readline()
    
        if i ==1:
            a = a[:].split()
            coord[0] = a[5]
            coord[1] = a[9]

        elif i ==2:
            a = a[:].split()
            coord[2] = a[3]
            coord[3] = a[7]
    
        elif i ==3:
            a = a[:].split()
            coord[4] = a[3]
            coord[5] = a[7]
    
        elif i ==4:
            a = a[:].split()
            b = a[6]
            c = a[10]
            d = a[14]
    
    Lx = abs(coord[1]-coord[0])
    Ly = abs(coord[3]-coord[2])
    Lz = abs(coord[5]-coord[4])
    dimensions = (Lx, Ly, Lz)

    lf = int(float(b[:3]))
    mf = int(float(c[:3]))
    nf = int(float(d))
    n_points = (lf, mf, nf)

    xm = np.linspace(coord[0]- coord[1]/2,coord[1]- coord[1]/2, lf)
    ym = np.linspace(coord[2] - coord[3]/2, coord[3] - coord[3]/2, mf)
    zm = np.linspace(coord[4], coord[5], nf)
    maillage = (xm, ym, zm)

    return (coord, dimensions, n_points, maillage)    


def get_dose(f, n_points):
    """ Parse le fichier .dat caracterisant le dépot de dose
    [Return] Un tableau en deux dimensions representant le dépot de dose

    [Params]
    f : descripteur de fichier
    n_points : triplet (lf, mf, nf) qui définit le nombre de points de chaque axe
    """
    (lf, mf, nf) = n_points
    
    dose_matrix = np.zeros([lf, mf])

    for i in range (lf):

        d = np.zeros([mf])

        for j in range (mf):
            a = f.readline()
            a = a[:].split()
            a = np.asanyarray(a)
            a = a.astype(np.float)
            d[j] = a[3]

        dose_matrix[i,:] = d[:]
        
        # Formatage different Python/Fortran lors de l'écriture de la fusion (saut de ligne)
        last_pos = f.tell()
        a = f.readline()
        if (a != " \n"):
            f.seek(last_pos)
    
    a = f.readline()

    return dose_matrix


########################### Affichage ###########################


def afficher_coupe_verticale(f, ax, dose_matrix, maxhom, coord, maillage, dimensions, n_points):
    """ Affiche une coupe verticale

    [Params]
    - f : descripteur de fichier
    - ax : l'axe correspondant à la figure
    - dose_matrix : la matrice des doses
    - maxhom : la dose maximale en un point
    - coord : vecteur de taille 6 contenant les informations sur le maillage
    - maillage : triplet (xm, ym, zm) 
    - dim_vector : triplet (Lx, Ly, Lz) qui définit la dim de chaque axe
    - n_points : triplet  (lf, mf, nf) qui définit le nombre de points sur chaque axe
    """
    (xm, ym, zm) = maillage
    (Lx, Ly, Lz) = dimensions
    (lf, mf, nf) = n_points
    
    # Calcul de la coupe
    xcut = np.zeros([len(xcutcm)])
    for i in range (len(xcutcm)):
        xcut[i] = np.int(lf*(float(xcutcm[i])-coord[0])/Lx)
    
    ycut = int(mf*(ycutcm-coord[2])/Ly)
    zcut = int(nf*(zcutcm-coord[5])/Lz)

    # Affichage de la coupe
    ax.plot(xm, dose_matrix[ycut,:]/maxhom, 'r', linewidth=2, label='M1')
    ax.set_ylim(ymax = 1.2, ymin = 0)
    ax.set_xlabel('Depth [cm]')
    ax.set_ylabel('Dose [a.u.]')
 
    for k in xcut:
        k = int(k)
        
    for i in range(len(xcut)):         
        if i == 0:
            ax.plot(ym, dose_matrix[:,xcut[i]]/maxhom, 'g' , linewidth=2, label='M1')
        else:
            ax.plot(ym, dose_matrix[:,xcut[i]]/maxhom, linewidth=2)
        ax.set_ylim(ymax = 1.1, ymin = 0)
        ax.set_xlabel('Off Axis Distance [cm]')
        ax.set_ylabel('Dose [a.u.]')
        plt.legend(loc='best')


def afficher_coupe_horizontale(f, ax, dose_matrix, maxhom, coord):
    """ Affiche une coupe horizontale

    [Params]
    - f : descripteur de fichier
    - ax : l'axe correspondant à la figure
    - dose_matrix : la matrice des doses
    - maxhom : la dose maximale en un point
    - coord : vecteur de taille 6 contenant les informations sur le maillage
    """
    levelsXZ = (0.05, 0.25, 0.5, 0.85, 0.95)

    CS = ax.contour(dose_matrix/maxhom, levelsXZ, extent=[coord[0], coord[1], coord[2], coord[3]], linewidths=2)
    ax.clabel(CS, inline=1, inline_spacing=1, fontsize=15, linestyles='dashed') 

    ax.set_xlabel('Depth [cm]', fontsize=17)
    ax.set_ylabel('Off Axis Distance [cm]', fontsize=17)
    ax.set_title('Coupe horizontale', fontsize=17)
    ax.set_aspect('equal')
    

def afficher_dose(filename_dose, contourage=None):
    """ Affiche une coupe horizontale et verticale à partir d'un fichier de données .dat
    [Params] filename : nom du fichier de données représentant le dépot de dose (.dat)
    """
    f = open(filename_dose, "r")

    # Parsing, recuperation des informations du header et de dose_matrix
    (coord, dim_vector, n_points, maillage) = get_header_info(f)
    dose_matrix = get_dose(f, n_points)
    maxhom = np.amax(dose_matrix)

    # Affichage
    fig1, ax1 = plt.subplots()
    #fig2, ax2 = plt.subplots()
    afficher_coupe_horizontale(f, ax1, dose_matrix, maxhom, coord)
    #afficher_coupe_verticale(f, ax2, dose_matrix, maxhom, coord, maillage, dim_vector, n_points)

    if contourage is not None:
        plot_contourage(ax1, contourage, 'orange')
    
    fig1.show()
    #fig2.show()
    f.close()
    

########################### Main ###########################
    

def usage(argv):
    if (len(sys.argv) != 2): 
        err_msg = "Usage : python generate_multisource.py filename\n"
        sys.stderr.write(err_msg)
        sys.exit(1)


def main():
    usage(sys.argv)
    filename = sys.argv[1]
    lancer_affichage(filename)
    

if __name__ == "__main__":
    main()
