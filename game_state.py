###############################################################################
#
# game_state.py
#
###############################################################################

from common import *
import level_parser, rect


#------------------------------------------------------------------------------
#
# State class
#
# This class holds the entire state of the game, including the
# rects for the agents, the level and all of its attributes,
# and agent attributes.
#
#------------------------------------------------------------------------------

class State:

#------------------------------------------------------------------------------
# __init__
#------------------------------------------------------------------------------

	def __init__(self, filename=None):

		# Create a level object
		if filename:
			self.level = level_parser.Level(filename)
		else:
			self.level = level_parser.Level()

		# Create data structures to keep track of ghost attributes
		self.ghost_rect	= {}
		self.ghost_mode = {}
		self.ghost_timer = {}
		self.current_ghost_direction = {}
		self.next_ghost_direction = {}

		# Initialize attributes for Pac-Man
		self.pacman_lives = 3
		self.score = 0
		self.level_number = 0

		# Initially, all of the agents are immobile
		self.pacman_immobile = True
		self.ghost_immobile = [True] * GHOSTS

#------------------------------------------------------------------------------
# load_level()
#------------------------------------------------------------------------------

	def load_level(self, filename, tile_size):
		"Loads the level that corresponds to the given filename and initializes the rects"

		# Parse the level file
		self.level.parse_file(filename)

		# Create a rect for Pac-Man
		self.pacman_rect = rect.Rect(self.level.pacman_home, (tile_size, tile_size))

		# Total number of pellets originally for this level
		self.total_pellets = self.level.num_pellets

		# Create the ghost rects
		for i in range(GHOSTS):
			self.ghost_rect[i] = rect.Rect(self.level.ghost_home[i], (tile_size, tile_size))



