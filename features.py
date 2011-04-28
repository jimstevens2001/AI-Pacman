###############################################################################
#
# features.py
#
###############################################################################

from common import *

#------------------------------------------------------------------------------
#
# Features class
#
# This class extracts the relevant features that will be used by
# the version of Pac-Man that uses function approximation.
# The features include distance to the closest pellet in any
# direation, and the distance to the closest ghost within three
# tiles in any direction.
#
#------------------------------------------------------------------------------


class Features:

#------------------------------------------------------------------------------
# __init__()
#------------------------------------------------------------------------------

	def __init__(self, state, game):

		self.state = state
		self.game = game


		self.features = {}
		self.reset_features()


#------------------------------------------------------------------------------
# reset_features()
#------------------------------------------------------------------------------

	def reset_features(self):
		"Resets all the features"

		self.ghost_visible = False

		# These are the features that will be used
		self.features = {'ghost_distance_UP': 0.0,		# Minimum distance from any ghost above Pac-Man
						'ghost_distance_DOWN': 0.0,		# Minimum distance from any ghost below Pac-Man
						'ghost_distance_LEFT': 0.0,		# Minimum distance from any ghost to the left Pac-Man
						'ghost_distance_RIGHT': 0.0,	# Minimum distance from any ghost to the right Pac-Man
						'pellet_distance_UP': 0.0,		# Minimum distance from any pellet above Pac-Man
						'pellet_distance_DOWN': 0.0,	# Minimum distance from any pellet below Pac-Man
						'pellet_distance_LEFT': 0.0,	# Minimum distance from any pellet to the left Pac-Man
						'pellet_distance_RIGHT': 0.0}	# Minimum distance from any pellet to the right Pac-Man

#------------------------------------------------------------------------------
# get_features_list()
#------------------------------------------------------------------------------

	def make_features_list(self, f):
		"Transforms the feature dictionary f into a list of feature values with a known order"

		features_list = []
		features_list.append( f['ghost_distance_UP'] )
		features_list.append( f['ghost_distance_DOWN'] )
		features_list.append( f['ghost_distance_LEFT'] )
		features_list.append( f['ghost_distance_RIGHT'] )
		features_list.append( f['pellet_distance_UP'] )
		features_list.append( f['pellet_distance_DOWN'] )
		features_list.append( f['pellet_distance_LEFT'] )
		features_list.append( f['pellet_distance_RIGHT'] )
		
		# Return the features we computed
		return features_list

#------------------------------------------------------------------------------
# get_features()
#------------------------------------------------------------------------------

	def get_features(self):
		"Returns the set of features that are relevant to learning"
		# First, reset all of the features
		self.reset_features()

		# Call each feature function in our list
		self.get_ghost_distances()
		self.get_pellet_distances()

		# Return the features we computed
		return self.features

#------------------------------------------------------------------------------
# get_ghost_distances()
#------------------------------------------------------------------------------

	def get_ghost_distances(self):
		"Computes the distance from each ghost in any direction"

		# First get the current position of Pac-Man
		pacman_position = self.state.pacman_rect.topleft

		# TODO: This is a bare integer that is a parameter to our system
		# We are not interested in ghost that are farther than 3 tiles away
		minimum = 3 * self.game.manager.config_options['tile_size']

		# Now look at each ghost to find the closest one in any direction
		for i in range(GHOSTS):
			# We only care to look at a ghost if it can hurt us
			if self.state.ghost_mode[i] == NORMAL:
				# Get the ghost's current position
				ghost_position = self.state.ghost_rect[i].topleft

				# Find the Manhattan distance from the ghost
				distance_x = ghost_position[0] - pacman_position[0]
				distance_y = ghost_position[1] - pacman_position[1]
				manhattan_distance = abs(distance_x) + abs(distance_y)

				# If this ghost is closer than the last closest one (or 3 tiles), then update the features
				if manhattan_distance < minimum:
					self.ghost_visible = True

					# We have a new minimum
					minimum = manhattan_distance

					# If the lateral distance is greater than the vertical distance, then it is to our side
					# otherwise it is above or below us
					if abs(distance_x) >= abs(distance_y):

						# If the distance is negative, the ghost is to our left
						if distance_x <= 0:
							self.features['ghost_distance_LEFT'] = 1.0
							self.features['ghost_distance_RIGHT'] = 0.0
							self.features['ghost_distance_UP'] = 0.0
							self.features['ghost_distance_DOWN'] = 0.0
						# The ghost is to our right
						else:
							self.features['ghost_distance_LEFT'] = 0.0
							self.features['ghost_distance_RIGHT'] = 1.0
							self.features['ghost_distance_UP'] = 0.0
							self.features['ghost_distance_DOWN'] = 0.0
					else:
						# The ghost is above us
						if distance_y <= 0:
							self.features['ghost_distance_LEFT'] = 0.0
							self.features['ghost_distance_RIGHT'] = 0.0
							self.features['ghost_distance_UP'] = 1.0
							self.features['ghost_distance_DOWN'] = 0.0
						# The ghost is below us
						else:
							self.features['ghost_distance_LEFT'] = 0.0
							self.features['ghost_distance_RIGHT'] = 0.0
							self.features['ghost_distance_UP'] = 0.0
							self.features['ghost_distance_DOWN'] = 1.0

#------------------------------------------------------------------------------
# get_pellet_distances()
#------------------------------------------------------------------------------

	def get_pellet_distances(self):
		"Computes the distance from each the closest pellet in each direction \
		and the number of pellets in each direction"

		# Get pacman's current position
		pacman_position = self.state.pacman_rect.topleft

		# Get Pac-Man's current tile position
		tile_position = self.game.checker.get_tile_coordinates(self.state.pacman_rect.topleft)

		# Get the tile size
		tile_size = self.game.manager.config_options['tile_size']

		# Our initial minimum is arbitrarily large
		minimum = 999

		if self.ghost_visible:
			return

		# Look at every tile in the game to find pellets
		for row in range(self.state.level.level_dim[1]):
			for col in range(self.state.level.level_dim[0]):

				# Get the tile's ID
				tile_id = self.state.level.level_layout[row][col]

				# If the tile is a pellet, then look at it
				if tile_id == '2' or tile_id == '3':

					# Find the Manhattan distance between Pac-Man and the pellet
					distance_x = col - tile_position[0]
					distance_y = row - tile_position[1]
					manhattan_distance = abs(distance_x) * tile_size + abs(distance_y) * tile_size

					# If the distance is a new minimum and we're not eating the pellet right now, then register it
					if manhattan_distance <= minimum and manhattan_distance != 0:

						# We have a new minimum
						minimum = manhattan_distance

						# If the lateral distance is greater than the vertical distance, than it is to our side
						# otherwise it is above or below us
						if abs(distance_x) >= abs(distance_y):

							# If the distance is negative, the pellet is to our left
							if distance_x < 0:
								self.features['pellet_distance_LEFT'] = 1.0
								self.features['pellet_distance_RIGHT'] = 0.0
								self.features['pellet_distance_UP'] = 0.0
								self.features['pellet_distance_DOWN'] = 0.0
							# It is to our right
							elif distance_x > 0:
								self.features['pellet_distance_LEFT'] = 0.0
								self.features['pellet_distance_RIGHT'] = 1.0
								self.features['pellet_distance_UP'] = 0.0
								self.features['pellet_distance_DOWN'] = 0.0
						else:

							# It is above us
							if distance_y < 0:
								self.features['pellet_distance_LEFT'] = 0.0
								self.features['pellet_distance_RIGHT'] = 0.0
								self.features['pellet_distance_UP'] = 1.0
								self.features['pellet_distance_DOWN'] = 0.0
							# It is below us
							elif distance_y > 0:
								self.features['pellet_distance_LEFT'] = 0.0
								self.features['pellet_distance_RIGHT'] = 0.0
								self.features['pellet_distance_UP'] = 0.0
								self.features['pellet_distance_DOWN'] = 1.0
