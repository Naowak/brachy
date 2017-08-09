#!/usr/bin/env python
# -*- coding: utf-8 -*-
# cythi_app.py
""" Script qui permet de lancer l'application cythi """
# Author : Thibault PARPAITE, Cyrille BEAUCHESNE
# Copyright (c) 2017, CELIA Bordeaux
# This file is part of cythi, released under a BSD license.

import sys
sys.path.append("./ressources/")
sys.path.append("./src/GUI")
sys.path.append("./src/previsualisation/")
sys.path.append("./src/HDV/")

from MainGUI import *

if __name__ == "__main__":
    app = MainApplication(None)
    app.title("Cythi")
    app.mainloop()
