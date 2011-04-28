###############################################################################
#
# game_engine.py
#
###############################################################################

import game_state, consistency_checker, state_updater, game_manager
from common import *

#------------------------------------------------------------------------------
#
# Game class
#
# The is the game engine.  It creates helper objects and
# outsources all of its tasks to them.  It contains the game
# manager with its config options, the consistency checker
# that enforces the rules of the game, and the state updater
# that handles all changes to the game state.
#
#------------------------------------------------------------------------------

class Game:

#------------------------------------------------------------------------------
# __init__
#------------------------------------------------------------------------------

	def __init__(self, draw, state, config_file_name):

		# The game engine has a manager, consistency checker, and state updater
		self.manager = game_manager.Manager(config_file_name)
		self.checker = consistency_checker.Checker(self.manager, state)
		self.updater = state_updater.Updater(self.checker, self.manager, draw, state)

#------------------------------------------------------------------------------
# set_drawing_object()
#------------------------------------------------------------------------------

	def set_drawing_object(self, draw):
		"Sets up a reference to the drawing class"

		self.updater.draw = draw

		# Set up the drawing context (most of it is in the config file)
		draw.set_drawing_parameters(self.manager.config_options)

#------------------------------------------------------------------------------
# set_pacmant_direction()
#------------------------------------------------------------------------------

	def set_pacman_direction(self, direction):
		"Sets the next direction of pacman"

		# When Pac-Man makes a move request, it simply sets its next direction.  The
		# semantics of this are that Pac-Man is expressing a wish to move in this direction
		# in the future, whenever that direction is valid.
		self.updater.state.next_pacman_direction = direction

#------------------------------------------------------------------------------
# set_ghost_direction()
#------------------------------------------------------------------------------

	def set_ghost_direction(self, ghost_id, direction):
		"Sets the next direction for a ghost"

		if ghost_id not in range(GHOSTS):
			raise PacmanError("Game: Ghost ID out of range in set_ghost_direction")

		# The ghost direction is set with the same semantics as Pac-Man's
		self.updater.state.next_ghost_direction[ghost_id] = direction

#------------------------------------------------------------------------------
# update_agents()
#------------------------------------------------------------------------------

	def update_agents(self):
		"Updates the whole state using current knowledge of agent actions"

		# We simply call on the state updater for this
		self.updater.update_all()



