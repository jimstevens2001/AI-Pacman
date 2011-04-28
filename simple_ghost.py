###############################################################################
#
# simple_ghost.py
#
###############################################################################

from common import *
import random, copy, time, path_finder



#------------------------------------------------------------------------------
#
# Ghost class
#
# This class implements a configurable AI for each ghost.
# The class can have random behavior, follow a set path, chase
# Pac-Man, or any combination thereof.  The keys to this
# flexibility are its random number generator and the
# difficulty set in the config options. 
#
#------------------------------------------------------------------------------

class Ghost:

#------------------------------------------------------------------------------
# __init__()
#------------------------------------------------------------------------------

	def __init__(self, id, state, game):

		# Set up references
		self.state = state
		self.game = game

		# Set up ghost attributes; coming out is used when the ghost comes out of the pen
		self.id = id
		self.probability = game.manager.config_options['difficulty']
		self.coming_out = False
		self.last_mode = NORMAL

		# Set up a RNG object
		self.random = random.Random()

		# The only sure way to figure out when we've been reset to our starting position is to keep
		# track of Pac-Man's lives and the level number
		self.pacman_lives = 0
		self.level_number = 0

		# Set up important positions we need to know
		self.setup_beacons()

		# Initialize goal
		self.goal = (-1,-1)

		# This is used to return to the ghost pen
		self.path_moves = []

		# This will determine when we make a decision
		self.decision_count = 0

		if game.manager.config_options['ghost_pattern']:
			self.reseed_rng()

		self.pf = path_finder.PF(game)

#------------------------------------------------------------------------------
# setup_beacons()
#------------------------------------------------------------------------------

	def setup_beacons(self):
		"Reaffirms the home position for the ghost and the position of the pen"

		# The center of the ghost pen is PINKY's home position
		self.pen = self.state.level.ghost_home[PINKY]

		# We get the tile size
		tile_size = self.game.manager.config_options['tile_size']

		# We need the precise position of the pen for A*
		self.pen = (self.pen[0] / tile_size * tile_size, self.pen[1] / tile_size * tile_size)

		# We need to get our new home in case the level changed
		self.home = self.state.level.ghost_home[self.id]

#------------------------------------------------------------------------------
# reseed_rng()
#------------------------------------------------------------------------------

	def reseed_rng(self):
		"Reseeds the Random Number Generator (RNG) if pacman dies or clears \
		 the level"

		# We only want to reseed the RNG if Pac-Man died or cleared a level
		if self.pacman_lives != self.state.pacman_lives or self.level_number != self.state.level_number:
			self.random.seed(self.id)
			self.pacman_lives = self.state.pacman_lives
			self.level_number = self.state.level_number

#------------------------------------------------------------------------------
# get_next_move()
#------------------------------------------------------------------------------

	def get_next_move(self):
		"Sets the next move for the ghost"

		# Confirm our home hasn't changed (new level would do that)
		if self.level_number != self.state.level_number:
			self.setup_beacons()

		# If we're doing a set pattern, reseed our RNG now
		if self.game.manager.config_options['ghost_pattern']:
			self.reseed_rng()

		# This will help save cycles on our machine by not making a full decision every time this function is called.
		# We will make a decision every time a reach a new tile.  However, if we're immobile or in EYES mode,
		# we have to make a decision immediately.
		if not self.state.ghost_immobile[self.id] and self.state.ghost_mode[self.id] != EYES and\
		       self.decision_count % (self.game.manager.config_options['tile_size'] / self.game.manager.config_options['ghost_velocity']):
			self.decision_count += 1
			return
		self.decision_count += 1

		# Suddenly change directions if we change modes (except if we're eyes)
		if self.state.ghost_mode[self.id] != self.last_mode and self.state.ghost_mode[self.id] != EYES:
			self.last_mode = self.state.ghost_mode[self.id]
			self.path_moves = []
			self.game.set_ghost_direction(self.id, -self.state.current_ghost_direction[self.id])

		# If we have reached our goal, we reset some parameters that might have given us a goal to begin with
		if self.state.ghost_rect[self.id].topleft == self.goal:
			self.coming_out = False

		# Get our current position
		current_position = self.state.ghost_rect[self.id].topleft

		# If we are at the home position, let's get out
		if (self.id != BLINKY and current_position == self.home) or current_position == self.pen or self.coming_out:
			self.coming_out = True
			self.goal = self.state.level.ghost_home[BLINKY]
			self.game.set_ghost_direction(self.id, self.bring_me_out())

		# If we are in EYES mode, let's go back to the pen
		elif self.state.ghost_mode[self.id] == EYES:
			self.goal = self.pen
			self.game.set_ghost_direction(self.id, self.take_me_to_the_pen())

		# Let's walk around, chase Pac-Man, that kind of thing
		else:
			self.game.set_ghost_direction(self.id, self.walk_me())

#------------------------------------------------------------------------------
# bring_me_out()
#------------------------------------------------------------------------------

	def bring_me_out(self):
		"Brings the ghost out of the pen"

		# Get the ghost's current position
		current_position = self.state.ghost_rect[self.id].topleft

		# Get the Manhattan distance from our goal
		manhattan_distance = (self.goal[0] - current_position[0], self.goal[1] - current_position[1])

		# Let's focus on lateral movement: if we're a tile away, we need to move laterally.  Otherwise let's move vertically
		if abs(manhattan_distance[0]) == self.game.manager.config_options['tile_size']:
			# Lateral movement
			if manhattan_distance[0] < 0:
				return LEFT
			else:
				return RIGHT
		else:
			# Vertical movement
			if manhattan_distance[1] < 0:
				return UP
			else:
				return DOWN

#------------------------------------------------------------------------------
# walk_me()
#------------------------------------------------------------------------------

	def walk_me(self):
		"Takes the ghost around the maze"

		# Get our current direction and position
		current_direction = self.state.current_ghost_direction[self.id]
		current_position = self.state.ghost_rect[self.id].topleft

		# Set our new direction to the next direction by default.  This will not 
		# change if we're mobile and our current direction != next direction
		new_direction = self.state.next_ghost_direction[self.id]

		possible_directions = [UP, DOWN, LEFT, RIGHT]

		# If we're vulnerable, we don't want to chase Pac-Man
		if self.state.ghost_mode[self.id] == VULNERABLE:
			chase_probability = 0
		else:
			chase_probability = self.probability

		# If we're mobile, most of the time we want to keep moving in our 
		# current direction
		if not self.state.ghost_immobile[self.id]:

			# If we don't have a next direction set that is different from the 
			# current direction, we might want to set one so that we don't 
			# always wait till we hit a wall to change directions
			if current_direction == self.state.next_ghost_direction[self.id]:
				probability = self.random.random()

				# Chase Pac-Man with a certain probability
				if probability < chase_probability:
					manhattan_distance = (self.state.pacman_rect.topleft[0] - current_position[0], \
										  self.state.pacman_rect.topleft[1] - current_position[1])

					if abs(manhattan_distance[0]) >= abs(manhattan_distance[1]):
						if manhattan_distance[0] < 0:
							new_direction = LEFT
						else:
							new_direction = RIGHT
					else:
						if manhattan_distance[1] < 0:
							new_direction = UP
						else:
							new_direction = DOWN

					# Let's not backtrack here
					if new_direction == -current_direction:
						new_direction = current_direction
		else:
			valid = False
			new_direction = 0

			# Here we are immobile so we need to find a new direction that is valid
			while new_direction == -current_direction or not valid:
				new_direction = self.random.choice(possible_directions)
				valid = self.game.checker.is_valid_move(str(self.id), current_position, new_direction)
				possible_directions.remove(new_direction)

				if not possible_directions:
					new_direction = -current_direction
					break

		return new_direction

#------------------------------------------------------------------------------
# find_direction()
#------------------------------------------------------------------------------

	def find_direction(self, move):
		"Finds the direction to go with the given move"

		# Only one item in the move is non-zero, and it is either positive or negative
		# Negative means left for lateral direction and up for vertical direction
		if move[0] < 0:
			return LEFT
		elif move[0] > 0:
			return RIGHT
		elif move[1] < 0:
			return UP
		elif move[1] > 0:
			return DOWN
		else:
			raise PacmanError("Simple ghost: cannot figure out direction in find_direction")

#------------------------------------------------------------------------------
# take_me_to_the_pen()
#------------------------------------------------------------------------------

	def take_me_to_the_pen(self):
		"Takes the ghost back to the pen"

		# Get the ghost's current position
		current_position = self.state.ghost_rect[self.id].topleft

		# If there is anything in the self.path_moves list, then we have
		# already calculated the path to the goal and merely need to follow it.
		# Otherwise, we need to compute the path to the ghost pen.
		if self.path_moves:
			# Here we are already in the process of following the path back to
			# the pen.

			# If we are close to our current goal, move on to the next one
			if self.path_moves[0] == current_position:
				self.path_moves.pop(0)

			# Look at the location at the front of the list, this is our current goal
			next_location = self.path_moves[0]

			# Calculate our distance from that location
			distance = (next_location[0] - current_position[0], next_location[1] - current_position[1])

			# Find the direction to get there
			next_direction = self.find_direction(distance)

			return next_direction

		else:
			# Here we need to figure out the path to the pen, so we call A*.
			# The path is only needed to be computed once, and will be saved
			# and followed on all subsequent calls to take_me_to_the_pen().
			self.path_moves = self.pf.astar(current_position, self.goal)

			# Now start following the path
			return self.take_me_to_the_pen()

