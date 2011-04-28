###############################################################################
#
# game_manager.py
#
###############################################################################

from common import *


#------------------------------------------------------------------------------
#
# Manager class
#
# The game manager handles all of the configuration options
# for the game.  It simply loads the configuration from the
# config file directly into a dictionary.
#
#------------------------------------------------------------------------------

class Manager:

#------------------------------------------------------------------------------
# __init__
#------------------------------------------------------------------------------

	def __init__(self, config_file_name):

		# Load the config file and eval the config options
		try:
			config = open(config_file_name, 'r')
			self.config_options = eval(config.read())
			config.close()
		except:
			raise PacmanError('Manager: Configuration file failed to load')

		# Set the number of levels
		self.num_levels = len(self.config_options['level_files'])

#------------------------------------------------------------------------------
# get_next_level()
#------------------------------------------------------------------------------

	def get_next_level(self):
		"Returns the file name for the next level"

		level_file_name = self.config_options['level_files'][self.next_level]

		# Keep track of the sequnce of level files
		self.next_level = (self.next_level + 1) % self.num_levels

		return level_file_name
