###############################################################################
#
# consistency_checker.py
#
###############################################################################

from common import *


#------------------------------------------------------------------------------
#
# Checker class
#
# This class is used to check that each move selected by an
# agent is valid.  It also provides helper functions for those
# who might need them.
#
#------------------------------------------------------------------------------

class Checker:

#------------------------------------------------------------------------------
# __init__
#------------------------------------------------------------------------------

	def __init__(self, manager, state):

		self.manager = manager
		self.state = state

#------------------------------------------------------------------------------
# out_of_bounds()
#------------------------------------------------------------------------------

	def out_of_bounds(self, position):
		"Returns whether the given position is out of bounds. "

		# Check whether the given position has a component that is either less 
		# than 0 or greater than one dimension in terms of tiles multiplied by 
		# the tile size.  If the position is out of bounds, it returns in which
		# direction

		# TODO: I had to change <= and >= to < and >
		#       What is correct?!
		#       The wrap around code in state_updater.py sets the x position to 0 when
		#       an agent gets wrapped. According to the way this was written previously
		#       is out of bounds.
		#       Getting the A* errors because pac-man is updated before the ghosts have
		#       chance to wrap around.
		if position[0] >= self.state.level.level_dim[0] * self.manager.config_options['tile_size']:
			return RIGHT
		if position[0] < 0:
			return LEFT
		if position[1] >= self.state.level.level_dim[1] * self.manager.config_options['tile_size']:
			return DOWN
		if position[1] < 0:
			return UP

		return 0

#------------------------------------------------------------------------------
# out_of_bounds2()
#------------------------------------------------------------------------------

	# TODO: this is a hack
	def out_of_bounds2(self, position):
		"Returns whether the given position is out of bounds. "

		# Check whether the given position has a component that is either less 
		# than 0 or greater than one dimension in terms of tiles multiplied by 
		# the tile size.  If the position is out of bounds, it returns in which
		# direction

		# TODO: I had to change <= and >= to < and >
		#       What is correct?!
		#       The wrap around code in state_updater.py sets the x position to 0 when
		#       an agent gets wrapped. According to the way this was written previously
		#       is out of bounds.
		#       Getting the A* errors because pac-man is updated before the ghosts have
		#       chance to wrap around.
		if position[0] > self.state.level.level_dim[0] * self.manager.config_options['tile_size']:
			return RIGHT
		if position[0] < 0:
			return LEFT
		if position[1] > self.state.level.level_dim[1] * self.manager.config_options['tile_size']:
			return DOWN
		if position[1] < 0:
			return UP

		return 0

#------------------------------------------------------------------------------
# get_tile_coordinates()
#------------------------------------------------------------------------------

	def get_tile_coordinates(self, position):
		"Returns the tile coordinates for the given position"

		# Get the tile size
		tile_size = self.manager.config_options['tile_size']

		# Figure out whether the position is out of bounds
		is_out = self.out_of_bounds(position)

		# If we are out of bounds, we need to set the position to be in bounds
		# before calculating the tile coordinates. We do this by adjusting by one tile.
		if is_out == RIGHT:
			position = (position[0] - tile_size, position[1])
		elif is_out == LEFT:
			position = (position[0] + tile_size, position[1])
		elif is_out == DOWN:
			position = (position[0] , position[1] - tile_size)
		elif is_out == UP:
			position = (position[0] , position[1] + tile_size)

		# Calculate the tile coordinates
		x = int(position[0] / tile_size)
		y = int(position[1] / tile_size)

		return (x, y)

#------------------------------------------------------------------------------
# is_wall()
#------------------------------------------------------------------------------

	def is_wall(self, position):
		"Returns whether the tile at the given position is a wall"

		
		(x, y) = self.get_tile_coordinates(position)

		# Check whether the tile ID is greater than 100 (every tile ID 100 and above is a wall)
		return int(self.state.level.level_layout[y][x]) >= 100

#------------------------------------------------------------------------------
# is_ghost_door()
#------------------------------------------------------------------------------

	def is_ghost_door(self, position):
		"Returns whether the tile at the given position is the ghost door"

		# Get the tile coordinates
		(x, y) = self.get_tile_coordinates(position)

		# Check whether the tile ID is that of the ghost door
		return int(self.state.level.level_layout[y][x]) == 1

#------------------------------------------------------------------------------
# get_relevant_corners()
#------------------------------------------------------------------------------

	def get_relevant_corners(self, position, move, velocity):
		"Returns a tuple that contains the corners to check for collisions \
		given the move and velocity for the given position"

		# Get the tile size
		tile_size = self.manager.config_options['tile_size']

		# Depending on the direction in which the agent is going, the two relevant corners to check for events
		# will differ.  For instance, if the agent is going up, the corners will be the upper left and upper right.
		if move == UP:
			first_corner = (position[0], position[1] - velocity)
			second_corner = (position[0] + tile_size - 1, position[1] - velocity)
		elif move == DOWN:
			first_corner = (position[0], position[1] + tile_size - 1 + velocity)
			second_corner = (position[0] + tile_size - 1, position[1] + tile_size - 1 + velocity)
		elif move == LEFT:
			first_corner = (position[0] - velocity, position[1])
			second_corner = (position[0] - velocity, position[1] + tile_size - 1)
		elif move == RIGHT:
			first_corner = (position[0] + tile_size - 1 + velocity, position[1])
			second_corner = (position[0] + tile_size - 1 + velocity, position[1] + tile_size - 1)
		else:
			raise PacmanError("Checker: Invalid move in get_relevant_corners")

		return (first_corner, second_corner)

#------------------------------------------------------------------------------
# is_valid_move()
#------------------------------------------------------------------------------

	def is_valid_move(self, ai_name, position, move):
		"Returns whether the move is valid, i.e. won't hit a wall or go \
		 through the ghost door for Pac-Man"
		
		if ai_name == "pacman":
			velocity = self.manager.config_options['pacman_velocity']
		else:
			velocity = self.manager.config_options['ghost_velocity']

		# The first and second corners represent the side of the agent most
		# likely to hit a wall
		first_corner, second_corner = self.get_relevant_corners(position, move, velocity)

		# Wall
		if self.is_wall(first_corner) or self.is_wall(second_corner):
			return False

		# Ghost Door
		if ai_name == "pacman" and (self.is_ghost_door(first_corner) or self.is_ghost_door(second_corner)):
			return False

		return True
