###############################################################################
#
# evolve.py
#
###############################################################################

###############################################################################
#
# EECS 749 : Final Project - Learning Pac-Man
# Date     : 05/04/2011
# Authors  : Fabrice Baijot, Adam Smith, Jim Stevens, Hsueh-Chien Cheng
# Version  : 3.1415
# Language : Python, version 2.6 and PyGame, version 1.7
# System   : tortilla.ece.umd.edu
# Site     : Dept. of Computer Science
#            The University of Maryland-College Park, College Park, MD
#
# Description:
#
# 
# Usage:
#
# python evolve.py
#
# Please see the README for more information.
#
###############################################################################

import main

result = 0

def cb(val):
	global result
	result = val

#main.pacman.register_callback(cb)
main.main('config/awesome_nn.txt')
print result

