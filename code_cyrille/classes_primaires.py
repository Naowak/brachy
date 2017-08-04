# -*- coding: utf-8 -*-

__author__ = 'Cyrille'


# ***********   DESCRIPTION DU PROGRAMME  **************

### Ce fichier contient la définition de la plupart des classes qui seront utilisées pour manipuler les fichiers
### de dépôt de dose, de densités ainsi que de découpages.
### On s'assure ainsi de créer des objets contenant les informations qui nous intéressent et qui sont faciles à manipuler.


###


# IMPORTATION DES LIBRAIRIES SCIENTIFIQUES

from numpy import array, loadtxt, sort, linspace, zeros, append, shape, amax
from matplotlib import pyplot as plt, cm





# DÉFINITION DES CLASSES

class contourage_a_partir_de_fichier:

    """ *** CLASSE TEMPORAIRE EN ATTENDANT LA PARTIE DU CODE DE THIBAULT ***


    Permet d'extraire un contourage d'un fichier TXT.

    [args]
        - fichier_contourage : Le nom du fichier TXT contenant le contourage. Celui-ci est organisé de la manière suivante :
                              0,0,0,0,1,1,1,0,0,0...
                              0,0,0,1,1,1,1,1,0,0...
                              0,0,0,1,1,1,1,0,0,0...
                              ...
                              Cet arangement doit avoir les mêmes dimensions que celui du dépôt de dose. Un 1 zéro signifie
                              que ce pixel est contenu dans le contourage. Un 0 signifie qu'il ne l'est pas.
        - nom_organe [optionnel] : Nom que l'on donne au contourage.

    [attributs]
        - matrice : Matrice en 3D sous forme de 'array numpy' contenant un 1 si ce pixel est contenu dans le contourage
                    et un 0 s'il ne l'est pas.
        - nom : Nom donné à l'organe en argument.

    [méthodes] : Pas important. Pour le moment, seuls la fonction d'initialisation ainsi que ses attributs nous sont utiles"""

    def __init__(self,fichier_contourage,nom_organe='Écrire nom organe',DICOM_id=None):
        self.nom = nom_organe
        self.matrice = array([loadtxt(fichier_contourage, dtype=int, delimiter=",")])
        self.id = DICOM_id
    def afficher(self,slice):
        plt.imshow(self.matrice[slice], origin='lower')
        plt.show()



### Désormais, les classes prenent en argument d'autres classes



class Doses:
    """ Classe contenant les infos pertinentes sur une matrice de doses donnée en argument
    *** DOIT PRÉALABLEMENT AVOIR ÉTÉ AJUSTÉE À LA TAILLLE DE LA MATRICE DE CONTOURAGE (ne pas prendre la matrice réduite) ***

    Arguments :

    - matrice_dose : matrice contenant les doses. elle est ajustée à la taille du contourage.
    - slice_id : identifiant de la slice de laquelle a été tiré les doses


    Attributs :

    - matrice : matrice donnée en argument et qui contient les doses. elle doit être ajustée au contourage.
    - slice_id : identifiant de la slice (donnée en argument) de laquelle a été tiré les doses
    - dim : doublet (y,x) donnant le nombre de points en x et y de la matrice

    À AJOUTER : D'AUTRES CARACTÉRISTIQUES SUR LA MATRICE DE DOSES, COMME LA TAILLE DES VOXELS, etc"""
    def __init__(self,matrice_doses, slice_id=None):
        self.matrice = array([matrice_doses])
        self.slice_id = slice_id
        self.dim = matrice_doses.shape
    def afficher(self): # Afficher le dépôt de dose
        plt.imshow(self.matrice, origin='lower')
        plt.show()



class classe_contourage:
    """ Classe contenant les infos pertinentes sur une matrice booléenne du contourage donnée en argument

    Arguments :

    - matrice_contourage : matrice booléenne d'un contourage
    - nom_organe : nom de la ROI correspondant au découpage
    - decoupage_id : identifiant de la région d'intérêt dans la slice donnée. ex : 1.2.840.113619.2.278.3.176243969.786.1462166632.515.88. None par défaut.
    - couleur : couleur de la courbe qui sera tracée pour cet organe.

    Attributs :

    - nom : nom de l'organe donné en argument.
    - matrice : matrice adaptée au contourage et qui contient les doses.
    - id : identifiant de la région d'intérêt dans la slice donnée. ex : 1.2.840.113619.2.278.3.176243969.786.1462166632.515.88. None par défaut.
    - couleur : couleur de la courbe qui sera tracée pour cet organe."""
    def __init__(self,matrice_contourage,nom_organe='Écrire nom organe',decoupage_id=None, couleur='Entrer couleur'):
        self.nom = nom_organe
        self.matrice = array([matrice_contourage])
        self.id = decoupage_id
        self.couleur = couleur
    def afficher(self): # Pour afficher le contourage
        plt.imshow(self.matrice, origin='lower')
        plt.show()





class Doses_dans_contourage:

    """ Permet de comparer un dépôt de dose et un contourage et d'extraire les doses qui font parti de ce même contourage

    [args]
        doses : objet 'doses' créé par la classe correspondante un peu plus haut dans ce code.
        contourage : objet 'contourage' créé par la classe ci-haut.

    [attributs]
        nbx, nby : nombre de points en x et y dans la matrice de doses
        liste : Liste contenant toutes les doses présentes dans le contourage passé en argument, et ce en ordre croissant.
                Comme dans un HDV on ne se soucie pas de la position absolue des pixels ayant reçus une certaine dose,
                'liste' est simplement en 1D.
                ex : [2.3415, 2.4925, ...]
        nom : Vient de l'attribut 'nom' associé à l'objet 'contourage' reçu en argument. Bref c'est le nom du contourage.
        nb_voxels : Le nombre entier de voxels présents dans le contourage (nombre d'éléments dans l'attribut 'liste').
        dose_max : La dose maximale présente dans le contourage (valeur maximale de l'attribut 'liste').
        v_voxel : Volume physique d'un voxel en cm^3

    [méthodes] : Vide pour l'instant. """


    def __init__(self,doses,contourage):

        self.nbx = doses.dim[1]
        self.nby = doses.dim[0]

        liste_doses_dans_contourage = []

        matrice_doses = doses.matrice
        for y in range(self.nbx):  # On lance 2 boucles 'FOR' pour analyser chaques éléments de la array 'contourage'
            for x in range(self.nby):
                if contourage.matrice[y][x] == 1:                        # Si un voxel de la array du contourage est égal à 1
                                                                            # (s'il est dans le découpage),
                    liste_doses_dans_contourage.append(matrice_doses[y][x])  # on l'ajoute à une liste contenant toutes
                                                                            # les valeurs de doses reçues
                                                                            # par les voxels à l'intérieur du découpage.

        #self.x_min = doses.x_min  # Récupération des valeurs maximales et minimales de x, y et z
        #self.x_max = doses.x_max
        #self.y_min = doses.y_min
        #self.y_max = doses.y_max
        #self.z_min = doses.z_min
        #self.z_max = doses.z_max
        self.liste = sort(liste_doses_dans_contourage)
        self.nom = contourage.nom
        self.nb_voxels = len(liste_doses_dans_contourage)
        self.dose_max = self.liste[-1]
        #self.v_voxel = #((self.x_max - self.x_min)/self.nbx)*\
                       #((self.y_max - self.y_min)/self.nby)*\
                       #((self.z_max - self.z_min)/self.nbz)
        self.v_voxel = 1 # À CHANGER!




class HDV_cumulatif:

    """ Permet de créer les données nécessaire au traçage d'une HDV cumulatif à partir de la liste des doses contenues dans un contourage.
        NOTE : LES DONNÉES CRÉÉES DANS L'AXE DES VOLUMES SONT EN NOMBRE DE VOXELS. POUR AVOIR UN VOLUME RELATIF OU ABSOLU, IL FAUT MULTIPLIER
        PAR LA FACTEUR APPROPRIÉ (ÉTAPE RÉALISÉE DANS LE CODAGE DE L'INTERFACE).

    [args]
        - classe_doses_dans_contourage : objet 'doses_dans_contourage' du contourage dont on veut tracer le HDV.
        - n : nombre de subdivisions dans le traçage des points.

    [attributs]
        - v_voxel : volume physique d'un voxel en cm^3
        - axe_dose : matrice 'array numpy' 1D contenant des points espacés également entre 0 et la dose maximale.
                    Ce sont les coordonnées en x dans le HDV cumulatif.
        - axe_volume : Contient les coordonnées en y associées à chaque point de 'axe_dose' (en nombre de voxels).
        - dose_max : dose maximale dans la liste de doses dans le découpage.
        - nb_voxels : nombre entier de voxels dans le découpage.
        - n : nombre de subdivisions entrées en argument.
        - nom : nom du contourage venant de l'attribut 'nom' de l'objet 'classe_doses_dans_contourage' passé en argument.

    [méthodes]
        - afficher : affiche le HDV à l'écran."""


    def __init__(self,classe_doses_dans_contourage,n):
        self.v_voxel = classe_doses_dans_contourage.v_voxel

        self.dose_max = classe_doses_dans_contourage.dose_max
        self.nb_voxels = classe_doses_dans_contourage.nb_voxels        # Nombre de voxels contenus dans le découpage
        liste_doses_dans_contourage = classe_doses_dans_contourage.liste
        self.n = n
        self.nom = classe_doses_dans_contourage.nom

        if self.dose_max != 0:
            axe_doses = linspace(0,self.dose_max,n+1)  # On crée l'axe des points contenant les doses
            axe_volume = [self.nb_voxels]  # On crée d'abord l'axe des volumes en nombre de voxels. On multipliera ensuite par le facteur approprié
                                      # tout dépendant si l'on veut le volume relatif ou absolu.


            iddc = 0

            for iad in range(1,n+1):  # On lance une boucle 'FOR' sur tous les éléments dans la liste 'axe_dose'.
                while True:
                    if liste_doses_dans_contourage[iddc] < axe_doses[iad]:  # On compte le nombre de doses
                                                                                                                #  dans le découpage qui sont
                                                                                                                #  inférieures à une certaine valeur
                                                                                                    # d'indice 'i' dans l'axe des doses créée plus tôt.
                        iddc += 1
                    else :
                        axe_volume.append(self.nb_voxels-iddc)
                        break  # On arrête la boucle si on excède un certaine valeur
            axe_volume = array(append(axe_volume,[0]),dtype=float)
            self.axe_volume = axe_volume
            self.axe_doses = append(axe_doses,[self.dose_max])

        else:
            self.axe_doses = array([])
            self.axe_volume = array([])
            #print 'Contourage de la ROI ' + self.nom + """ situé à l'extérieur de la zone réduite."""


    def afficher(self):
        plt.plot(self.axe_doses,self.axe_volume)
        plt.show()





class HDV_differentiel:

    """ Permet de créer les données nécessaire au traçage d'une HDV différentiel à partir de la liste des doses contenues dans un contourage.
        NOTE : LES DONNÉES CRÉÉES DANS L'AXE DES VOLUMES SONT EN NOMBRE DE VOXELS. POUR AVOIR UN VOLUME RELATIF OU ABSOLU, IL FAUT MULTIPLIER
        PAR LA FACTEUR APPROPRIÉ (ÉTAPE RÉALISÉE DANS LE CODAGE DE L'INTERFACE).

    [args]
        - classe_doses_dans_contourage : objet 'doses_dans_contourage' du contourage dont on veut tracer le HDV.
        - n : nombre de subdivisions dans le traçage des points.

    [attributs]
        - v_voxel : volume physique d'un voxel en cm^3
        - axe_dose : matrice 'array numpy' 1D contenant des points espacés également entre 0 et la dose maximale.
                    Ce sont les coordonnées en x dans le HDV cumulatif.
        - axe_volume : Contient les coordonnées en y associées à chaque point de 'axe_dose'.
        - dose_max : dose maximale dans la liste de doses dans le découpage.
        - nb_voxels : nombre entier de voxels dans le découpage.
        - n : nombre de subdivisions entrées en argument.
        - nom : nom du contourage venant de l'attribut 'nom' de l'objet 'classe_doses_dans_contourage' passé en argument.

    [méthodes]
        - afficher : affiche le HDV à l'écran."""



    def __init__(self,classe_doses_dans_contourage,n):
        self.v_voxel = classe_doses_dans_contourage.v_voxel
        self.dose_max = classe_doses_dans_contourage.dose_max
        self.nb_voxels = classe_doses_dans_contourage.nb_voxels

        self.n = n
        self.nom = classe_doses_dans_contourage.nom

        if self.dose_max != 0:
            axe_doses = linspace(0,self.dose_max,n+1)
            axe_volume = []

            a = 1  # Indice dans l'axe des doses reçues (linspace)
            c = 0  # Compteur du nombre de doses dans un certain intervalle
            d = 0  # Indice dans la liste de doses dans le volume (ex: de 1 à 822)

            while True:
                if classe_doses_dans_contourage.liste[d] <= axe_doses[a]:
                    c += 1
                    d += 1
                    if d == self.nb_voxels:
                        axe_volume.append(c)
                        break
                else:
                    axe_volume.append(c)
                    a += 1
                    c = 0

            def doubler_elements_liste(liste):
                nouvelle_liste = []
                for element in liste:
                    nouvelle_liste += [element]*2
                return nouvelle_liste

            self.axe_doses = array(doubler_elements_liste(axe_doses)[1:])
            self.axe_volume = array(doubler_elements_liste(axe_volume) + [0])

        else:
            self.axe_doses = array([])
            self.axe_volume = array([])
            print 'Contourage de la ROI ' + self.nom + """ situé à l'extérieur de la zone réduite."""


    def afficher(self):
        plt.plot(self.axe_doses, self.axe_volume)
        plt.show()


class Lecteur_fichier_contraintes:
    def __init__(self, fichier_contraintes):
        col_start = 0
        self.dict_contraintes = {}
        lignes_fichier = fichier_contraintes.readlines()[col_start:]

        get_ROI_id = True
        for ligne in lignes_fichier:
            if get_ROI_id == True:
                ROI_id = int(ligne[:-1])
                self.dict_contraintes[ROI_id] = {}
                get_ROI_id = False
            elif ligne != '\n':
                mots = ligne.split(':')
                dp = mots[0].split()[0]
                contrainte = float(mots[1].split()[0])
                self.dict_contraintes[ROI_id][dp] = contrainte
            else:
                get_ROI_id = True
        fichier_contraintes.close()


if __name__ == '__main__':

    # TESTS
    f = open('cf.txt', 'r')
    t = Lecteur_fichier_contraintes(f)
    print t.dict_contraintes

