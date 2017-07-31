#
# file : start.sh
# date : mercredi 14 juin 2017, 15:06:38 (UTC+0200)
# author : thibault <thibault@enseirb-matmeca.fr>
# description :
#
#!/bin/bash

usage()
{
    echo "usage: $0 output_dir_name config_file densite_lu_filename"
    echo "ex: $0 prostate prostate.don densite_hu_prostate.don"
    exit 1
}


# Boucle principale
if [ $# -l 2 ]
then
    usage
else
    # Chemins utiles
    SLICE_DIRECTORY=$1
    EXEC="$(pwd)/lance_KIDS"

    # Nettoyage et creation du repertoire contenant les resultats
    rm -rf $RESDIR 2> /dev/null
    mkdir $RESDIR
    mkdir $RESDIR/stock

    # On copie le fichier densite_lu_filename s'il existe
    if [ $# -eq 3 ]
    then
        cp $WORKDIR/$3 $RESDIR/stock
    fi

    # Lancement de M1
    cd $RESDIR
    $EXEC $WORKDIR/KIDS.don

    # On renomme avec le header
    for file in *.dat
    do
        mv $file $1_$file
    done

    exit 0
fi
