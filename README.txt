Authors : Thibault PARPAITE, Cyrille BEAUCHESNE
Copyright (c) 2017, CELIA Bordeaux
This file is part of cythi, released under a BSD license.

[*] Compatibilité
Logiciel fonctionnant sous Python 2.7
Bibliotheques requises :
- Tkinter
- Numpy
- Pillow
- Matplotlib
- Dicom

Pour les installer, procedure classique : $> pip install <bibliotheque>


[*] Directives d'installation
Modifier le fichier ./src/GUI/start_previsualisation.sh
En mettant le chemin absolu vers l'endroit où se trouve le code KIDS

Modifier le fichier ./src/previsualisation/generate_multisource.py
Pour changer la configuration de base du fichier .don


[*] Modifications code KIDS :
- KIDS.f90
Lignes 32 - 37
Lignes 164 - 187

- memoire.f90
Lignes 73 / 189 / 308 / 309

- densite.f90
Lignes 144 - 155


[*] Aide basique
Ce logiciel permet de visualiser les résultats obtenus à partir de l'algorithme M1. 
Il est possible de lancer des calculs de prévisualisation, puis de simuler un dépot de dose en direct avec l'histogramme dose volume (HDV) en support.
        
Marche à suivre :
1) Ouvrir patient -> Choisir un répertoire contenant des fichiers DICOM (.dsm)
2) Prévisualisation -> Choisir le répertoire de travail (où seront enregistrés les calculs)
3) Choisir le contourage cible dans le menu déroulant (ROI par défaut)
4) Lancer la prévisualisation
   - Il y la possibilité de récupérer des calculs déjà effectués
   - Une information -- Calculs en cours -- s'affiche pour indiquer que M1 est en train de tourner pour une slice donnée
   - Une fois les calculs terminés, -- Dose mode -- est activé (une icone l'indique en haut à droite de l'écran)
5) Contourage -> Cocher les contourages à visualiser sur le HDV
6) Afficher-Retirer miniature pour voir l'HDV en miniature
7) Possibilité de switch entre mode absolu et relatif
BUG : si un bug d'affichage apparait, veuillez actualiser la fenetre en appuyant plusieurs fois sur -- Afficher-Retirer miniature"
