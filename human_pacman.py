###############################################################################
#
# human_pacman.py
#
###############################################################################

from common import *
import pygame, sys


#------------------------------------------------------------------------------
#
# Pacman class
#
# This class has just enough functionality to respond to the
# inputs of a human player.  It only detects key presses and
# forwards the corresponding move to the game engine.
#
#------------------------------------------------------------------------------

class Pacman:

#------------------------------------------------------------------------------
# __init__()
#------------------------------------------------------------------------------

	def __init__(self, game_engine):

		# We only need a reference to the game engine for this class
		self.game = game_engine

#------------------------------------------------------------------------------
# get_next_move()
#------------------------------------------------------------------------------

	def get_next_move(self):
		"Examines the keyboard status and submits a move accordingly"

		# Get the dictionary of key presses from the event list
		keyboard_status = pygame.key.get_pressed()

		# The user hit the 'Esc' key, let's quit the program
		if keyboard_status[pygame.K_ESCAPE]:
			sys.exit(0)
		# Up - user wants to move up
		elif keyboard_status[pygame.K_UP]:
			self.game.set_pacman_direction(UP)
		# Down - user wants to move down
		elif keyboard_status[pygame.K_DOWN]:
			self.game.set_pacman_direction(DOWN)
		# Left - user wants to move left
		elif keyboard_status[pygame.K_LEFT]:
			self.game.set_pacman_direction(LEFT)
		# Right - user wants to move right
		elif keyboard_status[pygame.K_RIGHT]:
			self.game.set_pacman_direction(RIGHT)