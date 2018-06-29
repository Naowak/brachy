#
# file : start.sh
# date : mercredi 14 juin 2017, 15:06:38 (UTC+0200)
# author : thibault <thibault@enseirb-matmeca.fr>
# description :
#
#!/bin/bash

# Entrer manuellement le chemin absolu vers l'executable ./lance_KIDS pour lancer M1
# Exemple : /home/thibault/KIDS_cythi/lance_KIDS
EXEC_PATH="/home/naowak/Documents/brachy/KIDS_cythi/lance_KIDS"

usage()
{
    echo "usage: $0 slice_directory densite_lu?"
    exit 1
}


# Boucle principale
if [ $# -ne 2 ]
then
    usage
else
    # Recuperation param et deplacement
    if [ $2 -eq 0 ]
    then
        SLICE_DIRECTORY=$1/densite_constante
    else
        SLICE_DIRECTORY=$1/densite_lu
    fi

    cd $SLICE_DIRECTORY

    # Nettoyage du repertoire
    rm -rf *.dat 2> /dev/null
    rm -rf logbook.txt 2> /dev/null

    # Lancement de M1
    $EXEC_PATH $SLICE_DIRECTORY/config_KIDS.don > logbook.txt

    # Nettoyage des fichiers parasites
    rm *.mtv *.mgr
    rm cepxs.list
    rm dose.dat
    rm rho_*
    rm materiau*
    rm HU*
    rm recapitulatif_energie.dat

    exit 0
fi
