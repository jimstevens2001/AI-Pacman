###############################################################################
#
# features_nn.py
#
###############################################################################

from common import *
import path_finder

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

# TODO: This affects both ghost and pellet features. Do we want separate sight distances for each?
SIGHT_DISTANCE = 3

class Features:

#------------------------------------------------------------------------------
# __init__()
#------------------------------------------------------------------------------

	def __init__(self, state, game):

		self.state = state
		self.game = game


		self.features = {}
		self.reset_features()

		self.using = {'get_direction_to_closest_ghost': False,       # Binary Ghosts
					  'get_distance_to_each_ghost': False,           # Manhattan distance to each ghost
					  'get_maze_distance_to_nearest_ghost': True,    # Maze ghost
					  'get_distance_to_pellets': False,              # Manhattan distance to each pellet
					  'get_direction_to_closest_pellet': True,       # Binary pellets
					  'get_maze_distance_to_nearest_pellet': False,  # Maze pellet distance
					  'get_maze_direction_to_nearest_pellet': False} # Maze pellet direction (super binary pellets)

		self.pf = path_finder.PF(self.game)

#------------------------------------------------------------------------------
# reset_features()
#------------------------------------------------------------------------------

	def reset_features(self):
		"Resets all the features"

		self.ghost_visible = False

		# These are the features that will be used
		self.features = {'ghost_distance_UP': 1.0,		# Minimum distance from any ghost above Pac-Man
						 'ghost_distance_DOWN': 1.0,		# Minimum distance from any ghost below Pac-Man
						 'ghost_distance_LEFT': 1.0,		# Minimum distance from any ghost to the left Pac-Man
						 'ghost_distance_RIGHT': 1.0,	# Minimum distance from any ghost to the right Pac-Man
						 'binary_pellet_distance_UP': 1.0,		# Minimum distance from any pellet above Pac-Man
						 'binary_pellet_distance_DOWN': 1.0,	# Minimum distance from any pellet below Pac-Man
						 'binary_pellet_distance_LEFT': 1.0,	# Minimum distance from any pellet to the left Pac-Man
						 'binary_pellet_distance_RIGHT': 1.0,	# Minimum distance from any pellet to the right Pac-Man
						 'maze_pellet_distance_UP': 1.0,
						 'maze_pellet_distance_DOWN': 1.0,
						 'maze_pellet_distance_LEFT': 1.0,
						 'maze_pellet_distance_RIGHT': 1.0,
						 'maze_pellet_direction_UP': 1.0,
						 'maze_pellet_direction_DOWN': 1.0,
						 'maze_pellet_direction_LEFT': 1.0,
						 'maze_pellet_direction_RIGHT': 1.0}

#------------------------------------------------------------------------------
# get_features_list()
#------------------------------------------------------------------------------

	def make_features_list(self, f):
		"Transforms the feature dictionary f into a list of feature values with a known order"

		features_list = []

		if self.using['get_distance_to_each_ghost'] or self.using['get_maze_distance_to_nearest_ghost']:
			features_list.append( f['ghost_distance_UP'] )
			features_list.append( f['ghost_distance_DOWN'] )
			features_list.append( f['ghost_distance_LEFT'] )
			features_list.append( f['ghost_distance_RIGHT'] )
		if self.using['get_distance_to_pellets'] or self.using['get_direction_to_closest_pellet']:
			features_list.append( f['binary_pellet_distance_UP'] )
			features_list.append( f['binary_pellet_distance_DOWN'] )
			features_list.append( f['binary_pellet_distance_LEFT'] )
			features_list.append( f['binary_pellet_distance_RIGHT'] )
		if self.using['get_maze_distance_to_nearest_pellet']:
			features_list.append( f['maze_pellet_distance_UP'] )
			features_list.append( f['maze_pellet_distance_DOWN'] )
			features_list.append( f['maze_pellet_distance_LEFT'] )
			features_list.append( f['maze_pellet_distance_RIGHT'] )
		if self.using['get_maze_direction_to_nearest_pellet']:
			features_list.append( f['maze_pellet_direction_UP'] )
			features_list.append( f['maze_pellet_direction_DOWN'] )
			features_list.append( f['maze_pellet_direction_LEFT'] )
			features_list.append( f['maze_pellet_direction_RIGHT'] )
		
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
		if self.using['get_direction_to_closest_ghost']:
			self.get_direction_to_closest_ghost()
		if self.using['get_distance_to_each_ghost']:
			self.get_distance_to_each_ghost()
		if self.using['get_maze_distance_to_nearest_ghost']:
			self.get_maze_distance_to_nearest_ghost()
		if self.using['get_distance_to_pellets']:
			self.get_distance_to_pellets()
		if self.using['get_direction_to_closest_pellet']:
			self.get_direction_to_closest_pellet()
		if self.using['get_maze_distance_to_nearest_pellet']:
			self.get_maze_distance_to_nearest_pellet()
		if self.using['get_maze_direction_to_nearest_pellet']:
			self.get_maze_direction_to_nearest_pellet()

		# Return the features we computed
		return self.features

#------------------------------------------------------------------------------
# get_direction_to_closest_ghost()
#------------------------------------------------------------------------------

	def get_direction_to_closest_ghost(self):
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
							self.features['ghost_distance_LEFT'] = -1.0
							self.features['ghost_distance_RIGHT'] = 1.0
							self.features['ghost_distance_UP'] = 1.0
							self.features['ghost_distance_DOWN'] = 1.0
						# The ghost is to our right
						else:
							self.features['ghost_distance_LEFT'] = 1.0
							self.features['ghost_distance_RIGHT'] = -1.0
							self.features['ghost_distance_UP'] = 1.0
							self.features['ghost_distance_DOWN'] = 1.0
					else:
						# The ghost is above us
						if distance_y <= 0:
							self.features['ghost_distance_LEFT'] = 1.0
							self.features['ghost_distance_RIGHT'] = 1.0
							self.features['ghost_distance_UP'] = -1.0
							self.features['ghost_distance_DOWN'] = 1.0
						# The ghost is below us
						else:
							self.features['ghost_distance_LEFT'] = 1.0
							self.features['ghost_distance_RIGHT'] = 1.0
							self.features['ghost_distance_UP'] = 1.0
							self.features['ghost_distance_DOWN'] = -1.0

#------------------------------------------------------------------------------
# get_distance_to_each_ghost()
#------------------------------------------------------------------------------

	def get_distance_to_each_ghost(self):
		"Computes the distance from each ghost in any direction"

		# First get the current position of Pac-Man
		pacman_position = self.state.pacman_rect.topleft

		# We are not interested in ghost that are farther than SIGHT_DISTANCE tiles away
		tile_size = self.game.manager.config_options['tile_size']
		maximum = SIGHT_DISTANCE * tile_size

		self.features['ghost_distance_UP']    = 1.0
		self.features['ghost_distance_DOWN']  = 1.0
		self.features['ghost_distance_LEFT']  = 1.0
		self.features['ghost_distance_RIGHT'] = 1.0

		xdim = self.state.level.level_dim[0]
		ydim = self.state.level.level_dim[1]

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
				if manhattan_distance > maximum:
					continue

				manhattan_distance = float(manhattan_distance) / (maximum) - 1.0

				# If the lateral distance is greater than the vertical distance, then it is to our side
				# otherwise it is above or below us
				if abs(distance_x) >= abs(distance_y):

					# If the distance is negative, the ghost is to our left
					if distance_x <= 0:
						if manhattan_distance < self.features['ghost_distance_LEFT']:
							self.features['ghost_distance_LEFT'] = manhattan_distance
					# The ghost is to our right
					else:
						if manhattan_distance < self.features['ghost_distance_RIGHT']:
							self.features['ghost_distance_RIGHT'] = manhattan_distance
				else:
					# The ghost is above us
					if distance_y <= 0:
						if manhattan_distance < self.features['ghost_distance_UP']:
							self.features['ghost_distance_UP'] = manhattan_distance
					# The ghost is below us
					else:
						if manhattan_distance < self.features['ghost_distance_DOWN']:
							self.features['ghost_distance_DOWN'] = manhattan_distance

#------------------------------------------------------------------------------
# get_direction_to_closest_pellet()
#------------------------------------------------------------------------------

	def get_direction_to_closest_pellet(self):
		"Computes the distance from each the closest pellet in each direction \
		and the number of pellets in each direction"

		# Get pacman's current position
		pacman_position = self.state.pacman_rect.topleft

		# Get Pac-Man's current tile position
		tile_position = self.game.checker.get_tile_coordinates(self.state.pacman_rect.topleft)

		# Get the tile size
		tile_size = self.game.manager.config_options['tile_size']

		# Our initial minimum is arbitrarily large
		minimum = 999999

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

							# TODO: the 1.0s and -1.0s should be inverted to match the rest of the style of this module
							# If the distance is negative, the pellet is to our left
							if distance_x < 0:
								self.features['binary_pellet_distance_LEFT'] = 1.0
								self.features['binary_pellet_distance_RIGHT'] = -1.0
								self.features['binary_pellet_distance_UP'] = -1.0
								self.features['binary_pellet_distance_DOWN'] = -1.0
							# It is to our right
							elif distance_x > 0:
								self.features['binary_pellet_distance_LEFT'] = -1.0
								self.features['binary_pellet_distance_RIGHT'] = 1.0
								self.features['binary_pellet_distance_UP'] = -1.0
								self.features['binary_pellet_distance_DOWN'] = -1.0
						else:

							# It is above us
							if distance_y < 0:
								self.features['binary_pellet_distance_LEFT'] = -1.0
								self.features['binary_pellet_distance_RIGHT'] = -1.0
								self.features['binary_pellet_distance_UP'] = 1.0
								self.features['binary_pellet_distance_DOWN'] = -1.0
							# It is below us
							elif distance_y > 0:
								self.features['binary_pellet_distance_LEFT'] = -1.0
								self.features['binary_pellet_distance_RIGHT'] = -1.0
								self.features['binary_pellet_distance_UP'] = -1.0
								self.features['binary_pellet_distance_DOWN'] = 1.0

#------------------------------------------------------------------------------
# get_direction_to_closest_pellet()
#------------------------------------------------------------------------------

	def get_distance_to_pellets(self):
		"Computes the distance from each the closest pellet in each direction \
		and the number of pellets in each direction"

		# Get pacman's current position
		pacman_position = self.state.pacman_rect.topleft

		# Get Pac-Man's current tile position
		tile_position = self.game.checker.get_tile_coordinates(self.state.pacman_rect.topleft)

		# Get the tile size
		tile_size = self.game.manager.config_options['tile_size']

		self.features['binary_pellet_distance_UP']    = 1.0
		self.features['binary_pellet_distance_DOWN']  = 1.0
		self.features['binary_pellet_distance_LEFT']  = 1.0
		self.features['binary_pellet_distance_RIGHT'] = 1.0

		xdim = self.state.level.level_dim[0]
		ydim = self.state.level.level_dim[1]

		# Look at every tile in the game to find pellets
		for row in range(ydim):
			for col in range(xdim):

				# Get the tile's ID
				tile_id = self.state.level.level_layout[row][col]

				# If the tile is a pellet, then look at it
				if tile_id == '2' or tile_id == '3':

					# Find the Manhattan distance between Pac-Man and the pellet
					distance_x = col - tile_position[0]
					distance_y = row - tile_position[1]
					manhattan_distance = float(abs(distance_x)) /  xdim + float(abs(distance_y)) / ydim - 1.0

					# If the lateral distance is greater than the vertical distance, than it is to our side
					# otherwise it is above or below us
					if abs(distance_x) >= abs(distance_y):

						# If the distance is negative, the pellet is to our left
						if distance_x < 0:
							if manhattan_distance < self.features['binary_pellet_distance_LEFT']:
								self.features['binary_pellet_distance_LEFT'] = manhattan_distance
						# It is to our right
						elif distance_x > 0:
							if manhattan_distance < self.features['binary_pellet_distance_RIGHT']:
								self.features['binary_pellet_distance_RIGHT'] = manhattan_distance
					else:

						# It is above us
						if distance_y < 0:
							if manhattan_distance < self.features['binary_pellet_distance_UP']:
								self.features['binary_pellet_distance_UP'] = manhattan_distance
						# It is below us
						elif distance_y > 0:
							if manhattan_distance < self.features['binary_pellet_distance_DOWN']:
								self.features['binary_pellet_distance_DOWN'] = manhattan_distance

#------------------------------------------------------------------------------
# 
#------------------------------------------------------------------------------

	def get_maze_distance_to_nearest_ghost(self):
		"This function returns the maze distance to the nearest ghost in each \
		 direction. This is useful because telling Pac-Man the direction to each \
		 ghost tells him nothing about the maze."

		# First get the current position of Pac-Man
		pacman_position = self.state.pacman_rect.topleft

		# We are not interested in ghost that are farther than SIGHT_DISTANCE tiles away
		tile_size = self.game.manager.config_options['tile_size']
		maximum = SIGHT_DISTANCE * tile_size

		self.features['ghost_distance_UP']    = 1.0
		self.features['ghost_distance_DOWN']  = 1.0
		self.features['ghost_distance_LEFT']  = 1.0
		self.features['ghost_distance_RIGHT'] = 1.0

		xdim = self.state.level.level_dim[0]
		ydim = self.state.level.level_dim[1]

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

				if manhattan_distance > maximum:
					continue

				manhattan_distance = 1.0 * float(manhattan_distance) / (maximum) - 1.0

				# TODO: The path returned is normalized to only be on each tile.
				#       Do we need to consider this somehow?
				path = self.pf.astar(pacman_position, ghost_position)
				path.pop(0) # The first item in the list is Pac-Man's current location
				path_distance = len(path)

				# sometimes when pacman dies, he shares the same position as the ghost
				if path_distance == 0:
					ghost_maze_position = ghost_position
				# TODO: Turning this off seems to make Pac-Man way better
				elif path_distance > 2*SIGHT_DISTANCE:
					# The ghost is within SIGH_DISTANCE tiles of manhattan distance, but further according to moves in the maze.
					continue
				else:
					ghost_maze_position = path[0]

				distance_x = ghost_maze_position[0] - pacman_position[0]
				distance_y = ghost_maze_position[1] - pacman_position[1]

				normalized_path_distance = 1.0 * float(path_distance * tile_size) / (2*maximum) - 1.0

				if normalized_path_distance > 1.0:
					print normalized_path_distance
					raw_input()

				# If the lateral distance is greater than the vertical distance, then it is to our side
				# otherwise it is above or below us
				if abs(distance_x) >= abs(distance_y):

					# If the distance is negative, the ghost is to our left
					if distance_x <= 0:
						if normalized_path_distance < self.features['ghost_distance_LEFT']:
							self.features['ghost_distance_LEFT'] = normalized_path_distance
					# The ghost is to our right
					else:
						if normalized_path_distance < self.features['ghost_distance_RIGHT']:
							self.features['ghost_distance_RIGHT'] = normalized_path_distance
				else:
					# The ghost is above us
					if distance_y <= 0:
						if normalized_path_distance < self.features['ghost_distance_UP']:
							self.features['ghost_distance_UP'] = normalized_path_distance
					# The ghost is below us
					else:
						if normalized_path_distance < self.features['ghost_distance_DOWN']:
							self.features['ghost_distance_DOWN'] = normalized_path_distance

#------------------------------------------------------------------------------
# get_maze_distance_to_nearest_pellet()
#------------------------------------------------------------------------------

	def get_maze_distance_to_nearest_pellet(self):
		"This function returns the maze distance to the nearest pellet in each \
		 direction. This is usefull because it takes the maze into account when \
		 finding pellets. I.e. we are giving Pac-Man the necessary information \
		 to navigate the maze and find the pellets."

		# First get the current position of Pac-Man
		pacman_position = self.state.pacman_rect.topleft

		# We are not interested in pellets that are farther than SIGHT_DISTANCE tiles away
		tile_size = self.game.manager.config_options['tile_size']
		maximum = SIGHT_DISTANCE * tile_size

		self.features['maze_pellet_distance_UP']    = 1.0
		self.features['maze_pellet_distance_DOWN']  = 1.0
		self.features['maze_pellet_distance_LEFT']  = 1.0
		self.features['maze_pellet_distance_RIGHT'] = 1.0

		xdim = self.state.level.level_dim[0]
		ydim = self.state.level.level_dim[1]

		# Look at every tile in the game to find pellets
		for row in range(ydim):
			for col in range(xdim):

				pellet_position = [col*tile_size, row*tile_size]

				# Get the tile's ID
				tile_id = self.state.level.level_layout[row][col]

				# If the tile isn't a pellet, then we don't care about it
				if tile_id != '2' and tile_id != '3' or pellet_position == pacman_position:
					continue

				# Find the Manhattan distance between Pac-Man and the pellet
				distance_x = pellet_position[0] - pacman_position[0]
				distance_y = pellet_position[1] - pacman_position[1]
				manhattan_distance = abs(distance_x) + abs(distance_y)

				# If the pellet isn't close enough, then we don't care about it.
				# We only want to calculate A* between Pac-Man and pellets he is close to.
				if manhattan_distance > maximum:
					continue

				# TODO: The path returned is normalized to only be on each tile.
				#       Do we need to consider this somehow?

				# Find the path from Pac-Man's position to the pellet
				path = self.pf.astar(pacman_position, pellet_position)
				path.pop(0) # The first item in the list is Pac-Man's current location
				path_distance = len(path)

				if path_distance == 0:
					pellet_maze_position = pellet_position
				elif path_distance > SIGHT_DISTANCE:
					continue
				else:
					pellet_maze_position = path[0]

				distance_x = pellet_maze_position[0] - pacman_position[0]
				distance_y = pellet_maze_position[1] - pacman_position[1]

				normalized_path_distance = 1.0 * float(path_distance * tile_size) / maximum - 1.0

				# If the lateral distance is greater than the vertical distance, then it is to our side
				# otherwise it is above or below us
				if abs(distance_x) >= abs(distance_y):

					# If the distance is negative, the pellet is to our left
					if distance_x <= 0:
						if normalized_path_distance < self.features['maze_pellet_distance_LEFT']:
							self.features['maze_pellet_distance_LEFT'] = normalized_path_distance
					# The pellet is to our right
					else:
						if normalized_path_distance < self.features['maze_pellet_distance_RIGHT']:
							self.features['maze_pellet_distance_RIGHT'] = normalized_path_distance
				else:
					# The pellet is above us
					if distance_y <= 0:
						if normalized_path_distance < self.features['maze_pellet_distance_UP']:
							self.features['maze_pellet_distance_UP'] = normalized_path_distance
					# The pellet is below us
					else:
						if normalized_path_distance < self.features['maze_pellet_distance_DOWN']:
							self.features['maze_pellet_distance_DOWN'] = normalized_path_distance

#------------------------------------------------------------------------------
# get_maze_direction_to_nearest_pellet()
#------------------------------------------------------------------------------

	def get_maze_direction_to_nearest_pellet(self):
		"""comment"""

		# First get the current position of Pac-Man
		pacman_position = self.state.pacman_rect.topleft

		# We are not interested in pellets that are farther than SIGHT_DISTANCE tiles away
		tile_size = self.game.manager.config_options['tile_size']
		maximum = SIGHT_DISTANCE * tile_size

		self.features['maze_pellet_direction_UP']    = 1.0
		self.features['maze_pellet_direction_DOWN']  = 1.0
		self.features['maze_pellet_direction_LEFT']  = 1.0
		self.features['maze_pellet_direction_RIGHT'] = 1.0

		xdim = self.state.level.level_dim[0]
		ydim = self.state.level.level_dim[1]

		# Our initial minimum is arbitrarily large
		minimum = 999999

		# Look at every tile in the game to find pellets
		for row in range(ydim):
			for col in range(xdim):

				pellet_position = [col*tile_size, row*tile_size]

				# Get the tile's ID
				tile_id = self.state.level.level_layout[row][col]

				# If the tile isn't a pellet, then we don't care about it
				if tile_id != '2' and tile_id != '3' or pellet_position == pacman_position:
					continue

				# Find the Manhattan distance between Pac-Man and the pellet
				distance_x = pellet_position[0] - pacman_position[0]
				distance_y = pellet_position[1] - pacman_position[1]
				manhattan_distance = abs(distance_x) + abs(distance_y)

				# We only want to calculate A* between Pac-Man and pellets he is close to.
				if manhattan_distance > maximum:
					# If the distance is a new minium and we aren't eating the pellet right now, then register it.
					if manhattan_distance < minimum and manhattan_distance != 0:
						minimum = manhattan_distance
					else:
						continue
				else:
					# TODO: The path returned is normalized to only be on each tile.
					#       Do we need to consider this somehow?
	
					# Find the path from Pac-Man's position to the pellet
					path = self.pf.astar(pacman_position, pellet_position)
					path.pop(0) # The first item in the list is Pac-Man's current location
					# TODO:	this is a bug. it will always revert to manhattan distance because the path is longer
					path_distance = len(path) * tile_size

					if path_distance == 0:
						pellet_maze_position = pellet_position
					#elif path_distance > SIGHT_DISTANCE * tile_size:
					#	continue
					else:
						pellet_maze_position = path[0]
	
					distance_x = pellet_maze_position[0] - pacman_position[0]
					distance_y = pellet_maze_position[1] - pacman_position[1]
	
					# If the distance is a new minimum and we're not eating the pellet right now, then register it
					if path_distance <= minimum and path_distance != 0:
						minimum = path_distance
					else:
						continue

				# If the lateral distance is greater than the vertical distance, then it is to our side
				# otherwise it is above or below us
				if abs(distance_x) >= abs(distance_y):

					# If the distance is negative, the pellet is to our left
					if distance_x <= 0:
							self.features['maze_pellet_direction_UP'] = 1.0
							self.features['maze_pellet_direction_DOWN'] = 1.0
							self.features['maze_pellet_direction_LEFT'] = -1.0
							self.features['maze_pellet_direction_RIGHT'] = 1.0
					# The pellet is to our right
					else:
							self.features['maze_pellet_direction_UP'] = 1.0
							self.features['maze_pellet_direction_DOWN'] = 1.0
							self.features['maze_pellet_direction_LEFT'] = 1.0
							self.features['maze_pellet_direction_RIGHT'] = -1.0
				else:
					# The pellet is above us
					if distance_y <= 0:
							self.features['maze_pellet_direction_UP'] = -1.0
							self.features['maze_pellet_direction_DOWN'] = 1.0
							self.features['maze_pellet_direction_LEFT'] = 1.0
							self.features['maze_pellet_direction_RIGHT'] = 1.0
					# The pellet is below us
					else:
							self.features['maze_pellet_direction_UP'] = 1.0
							self.features['maze_pellet_direction_DOWN'] = -1.0
							self.features['maze_pellet_direction_LEFT'] = 1.0
							self.features['maze_pellet_direction_RIGHT'] = 1.0

