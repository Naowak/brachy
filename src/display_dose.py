# -*- coding: utf-8 -*-
import sys
import numpy as np
import matplotlib.pyplot as plt

# Parametres coupe
xcutcm = np.array([2.5])
ycutcm = 2.5                  
zcutcm = 0.5


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
    
    dimx = abs(coord[1]-coord[0])
    dimy = abs(coord[3]-coord[2])
    dimz = abs(coord[5]-coord[4])
    dim_vector = (dimx, dimy, dimz)

    nbx = int(float(b[:3]))
    nby = int(float(c[:3]))
    nbz = int(float(d))
    nb_vector = (nbx, nby, nbz)

    xm = np.linspace(coord[0]- coord[1]/2,coord[1]- coord[1]/2, nbx)
    ym = np.linspace(coord[2] - coord[3]/2, coord[3] - coord[3]/2, nby)
    zm = np.linspace(coord[4], coord[5], nbz)
    maillage = (xm, ym, zm)

    return (coord, dim_vector, nb_vector, maillage)    


def get_dose(f, nb_vector):
    """ Parse le fichier .dat caracterisant le dépot de dose
    [Return] Un tableau en deux dimensions representant le dépot de dose

    [Params]
    f : descripteur de fichier
    nb_vector : triplet (nbx, nby, nbz) qui définit le nombre de points de chaque axe
    """
    (nbx, nby, nbz) = nb_vector
    
    dose_matrix = np.zeros([nby,nbx])

    for j in range (nbx):

        d = np.zeros([nby])

        for i in range (nby):
            a = f.readline()            
            a = a[:].split()
            a = np.asanyarray(a)
            a = a.astype(np.float)
            d[i] = a[3]

        dose_matrix[:,j]= d[:]

        # Formatage different Python/Fortran lors de l'écriture de la fusion (saut de ligne)
        last_pos = f.tell()
        a = f.readline()
        if (a != " \n"):
            f.seek(last_pos)
    
    a = f.readline()

    return dose_matrix


def afficher_coupe_verticale(f, dose_matrix, maxhom, coord, maillage, dim_vector, nb_vector):
    """ Affiche une coupe verticale

    [Params]
    f : descripteur de fichier
    dose_matrix : la matrice des doses
    maxhom : la dose maximale en un point
    coord : vecteur de taille 6 contenant les informations sur le maillage
    maillage : triplet (xm, ym, zm) 
    dim_vector : triplet (dimx, dimy, dimz) qui définit la dim de chaque axe
    nb_vector : triplet  (nbx, nby, nbz) qui définit le nombre de points sur chaque axe
    """
    (xm, ym, zm) = maillage
    (dimx, dimy, dimz) = dim_vector
    (nbx, nby, nbz) = nb_vector
    
    # Calcul de la coupe
    xcut = np.zeros([len(xcutcm)])
    for i in range (len(xcutcm)):
        xcut[i] = np.int(nbx*(float(xcutcm[i])-coord[0])/dimx)
    
    ycut = int(nby*(ycutcm-coord[2])/dimy)
    zcut = int(nbz*(zcutcm-coord[5])/dimz)

    # Affichage de la coupe
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    plt.plot(xm, dose_matrix[ycut,:]/maxhom, 'r', linewidth=2, label='M1')
    plt.ylim(ymax = 1.2, ymin = 0)
    ax.set_xlabel('Depth [cm]')
    ax.set_ylabel('Dose [a.u.]')

    plt.legend(loc='best')
 
    for k in xcut:
        k = int(k)
        
    for i in range(len(xcut)):         
        fig = plt.figure(1)
        ax = fig.add_subplot(111)
           
        if i == 0:
            plt.plot(ym, dose_matrix[:,xcut[i]]/maxhom, 'g' , linewidth=2, label='M1')
        else:
            plt.plot(ym, dose_matrix[:,xcut[i]]/maxhom, linewidth=2)
        plt.ylim(ymax = 1.1, ymin = 0)
        ax.set_xlabel('Off Axis Distance [cm]')
        ax.set_ylabel('Dose [a.u.]')
        plt.legend(loc='best')


def afficher_coupe_horizontale(f, dose_matrix, maxhom, coord):
    """ Affiche une coupe horizontale

    [Params]
    f : descripteur de fichier
    dose_matrix : la matrice des doses
    maxhom : la dose maximale en un point
    coord : vecteur de taille 6 contenant les informations sur le maillage
    """
    levelsXZ = (0.05, 0.25, 0.5, 0.85, 0.95)

    fig=plt.figure(4)
    ax = fig.add_subplot(111)

    CS = plt.contour(dose_matrix/maxhom, levelsXZ, extent=[coord[0], coord[1],coord[2] - coord[3]/2, coord[3]- coord[3]/2], linewidths=2)
    lines = [ CS.collections[0]]
    labels = ['M1']
    plt.clabel(CS, inline=1, fontsize=20, linestyles='dashed') 

    m1legend = plt.legend(lines, labels, loc='best')
    ax = plt.gca().add_artist(m1legend)

    plt.rcParams.update({'font.size': 17})
    plt.xlabel('Depth [cm]', fontsize=17)
    plt.ylabel('Off Axis Distance [cm]', fontsize=17)
    

def lancer_affichage(filename):
    """ Affiche une coupe horizontale et verticale à partir d'un fichier de données .dat

    [Params]
    filename : nom du fichier de données représentant le dépot de dose (.dat)
    """
    f = open(filename, "r")

    # Parsing 
    (coord, dim_vector, nb_vector, maillage) = get_header_info(f)
    dose_matrix = get_dose(f, nb_vector)
    maxhom = np.amax(dose_matrix)

    # Affichage
    afficher_coupe_horizontale(f, dose_matrix, maxhom, coord)
    afficher_coupe_verticale(f, dose_matrix, maxhom, coord, maillage, dim_vector, nb_vector)
    plt.show()
    

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
