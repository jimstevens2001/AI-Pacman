###############################################################################
#
# state_updater.py
#
###############################################################################

from common import *
import time


#------------------------------------------------------------------------------
#
# The Updater class
#
# This class handles all of the possible changes to the state and
# their consequences.  It uses the state consistency checker
# to help with the rules of the game, and alerts the drawing
# class when significant event need to be drawn, or when
# new parameters need to be loaded.
#
#------------------------------------------------------------------------------

class Updater:

#------------------------------------------------------------------------------
# __init__()
#------------------------------------------------------------------------------

	def __init__(self, checker, manager, draw, state):

		self.checker = checker
		self.manager = manager
		self.draw = draw
		self.state = state

#------------------------------------------------------------------------------
# load_first_level()
#------------------------------------------------------------------------------

	def load_first_level(self):
		"Loads the first level"

		# Initialize the number of lives for Pac-Man and the level number
		self.state.pacman_lives = 3
		self.state.score = 0
		self.manager.next_level = 0
		self.state.level_number = 0

		# Load the level
		self.load_next_level()

#------------------------------------------------------------------------------
# load_next_level()
#------------------------------------------------------------------------------

	def load_next_level(self):
		"Loads the next level"

		# Increment the level number, load the next level and put the agents in
		# their initial positions for the new level.
		self.state.level_number += 1
		self.state.load_level(self.manager.get_next_level(), self.manager.config_options['tile_size'])
		self.reset_agents()

		# If the graphics are on, then we need to draw the next level.
		if self.manager.config_options['graphics_on']:
			self.draw.load_level()
			self.draw.draw()

			# Print a message to alert the user of how far he's gotten
			self.draw.print_message("LEVEL " + str(self.state.level_number), 2000)

#------------------------------------------------------------------------------
# reset_ghost_timer()
#------------------------------------------------------------------------------

	def reset_ghost_timer(self, ghost_id):
		"Resets the timer for the ghost that corresponds to ghost_id"

		if ghost_id not in range(GHOSTS):
			raise PacmanError("Updater: Ghost ID out of range in reset_ghost_timer")

		# Reset the vulnerability timer for the specified ghost
		self.state.ghost_timer[ghost_id] = self.manager.config_options['ghost_timer']

#------------------------------------------------------------------------------
# reset_all_ghost_timers()
#------------------------------------------------------------------------------

	def reset_all_ghost_timers(self):
		"Resets all the ghost timers"

		# Reset the vulnerability timer for each ghost
		self.state.ghost_timer = [self.manager.config_options['ghost_timer']] * 4

#------------------------------------------------------------------------------
# set_ghost_mode()
#------------------------------------------------------------------------------

	def set_ghost_mode(self, ghost_id, mode):
		"Sets the mode for the ghost identified by ghost_id"

		if ghost_id not in range(GHOSTS):
			raise PacmanError("Updater: Ghost ID out of range in set_ghost_mode")

		if mode not in range(GHOST_MODES):
			raise PacmanError("Updater: Invalid ghost mode in set_ghost_mode")

		# The ghost mode will be set to the mode that has been passed in
		# unless the mode is vulnerable and the ghost has been eaten by Pac-Man.
		# A ghost in EYES mode cannot become vulnerable again
		if not (mode == VULNERABLE and self.state.ghost_mode[ghost_id] == EYES):
			self.state.ghost_mode[ghost_id] = mode

		# If Pac-Man just ate a power pellet, start (or reset) the timer
		if mode == VULNERABLE:
			self.state.ghost_timer[ghost_id] = self.manager.config_options['ghost_timer']

#------------------------------------------------------------------------------
# set_ghost_mode_all()
#------------------------------------------------------------------------------

	def set_ghost_mode_all(self, mode):
		"Sets the mode for all the ghosts"

		if mode not in range(GHOST_MODES):
			raise PacmanError("Updater: Invalid ghost mode chosen for all in set_ghost_mode_all")

		# Give each ghost the same mode
		for i in range(GHOSTS):
			self.set_ghost_mode(i, mode)

#------------------------------------------------------------------------------
# update_all()
#------------------------------------------------------------------------------

	def update_all(self):
		"Updates the state according to all of the agents' actions"

		# First update Pac-Man
		status = self.update_pacman()

		# If no major events happened to Pac-Man (death, finished level), then 
		# apply the ghosts' actions
		i = 0
		while status == CONTINUE and i < GHOSTS:
			status = self.update_ghost(i)
			i += 1

		# Check whether anything major happened
		if status == NEXT_LEVEL:
			# Pac-Man cleared the level, we need to load the next one
			self.load_next_level()

			# If graphics are turned on, pause the game for a second to
			# show the significance of the event
			if self.manager.config_options['graphics_on']:
				time.sleep(1)

		elif status == RESET_AGENTS:
			# Pac-Man died but he is not out of lives
			self.reset_agents()

			# Print a message to alert the user that the game will start again momentarily
			if self.manager.config_options['graphics_on']:
				self.draw.print_message("GET READY", 1000)

		elif status == RESET_GAME:
			# Pac-Man is out of lives, it's game over
			if self.manager.config_options['graphics_on']:
				self.draw.print_message("GAME OVER", 4000)
			self.reset_game()

#------------------------------------------------------------------------------
# is_pellet()
#------------------------------------------------------------------------------

	def is_pellet(self, position):
		"Returns whether the tile at the given position is a pellet"

		# Get the tile size
		tile_size = self.manager.config_options['tile_size']

		# If the position is not precisely lined up with a tile position, we won't even consider it
		if position[1] % tile_size or position[0] % tile_size:
			return False
		else:
			# Check the level layout to see if the tile is a pellet
			return self.state.level.level_layout[int(position[1] / tile_size)][int(position[0] / tile_size)] == "2"

#------------------------------------------------------------------------------
# is_power_pellet()
#------------------------------------------------------------------------------

	def is_power_pellet(self, position):
		"Returns whether the tile at the given position is a power pellet"

		# Get the tile size
		tile_size = self.manager.config_options['tile_size']

		# If the position is not precisely lined up with a tile position, we won't even consider it
		if position[1] % tile_size or position[0] % tile_size:
			return False
		else:
			# Check the level layout to see if the tile is a power pellet
			return self.state.level.level_layout[int(position[1] / tile_size)][int(position[0] / tile_size)] == "3"

#------------------------------------------------------------------------------
# clear_tile()
#------------------------------------------------------------------------------

	def clear_tile(self, position):
		"Clears the given tile"

		# Get the tile size
		tile_size = self.manager.config_options['tile_size']

		# Find the tile and set its ID to 0
		self.state.level.level_layout[int(position[1] / tile_size)][int(position[0] / tile_size)] = "0"

#------------------------------------------------------------------------------
# handle_collision()
#------------------------------------------------------------------------------

	def handle_collision(self, ghost_id):
		"Handles a collision between Pac-Man and a ghost"

		# Ghost is normal, pause for a second and reset ghosts and pacman
		if self.state.ghost_mode[ghost_id] == NORMAL:
			if self.manager.config_options['graphics_on']:
				time.sleep(1)

			# Decrement Pac-Man's lives
			self.state.pacman_lives -= 1

			# If Pac-Man has no more lives, it's game over
			if self.state.pacman_lives == 0:
				return RESET_GAME
			return RESET_AGENTS

		# Ghost is vulnerable
		elif self.state.ghost_mode[ghost_id] == VULNERABLE:
			self.state.score += 200
			self.set_ghost_mode(ghost_id, EYES)
			return CONTINUE

#------------------------------------------------------------------------------
# update_pacman()
#------------------------------------------------------------------------------

	def update_pacman(self):
		"Updates the state according to Pac-Man's current action"

		# Get Pac-Man's current position
		current_position = self.state.pacman_rect.topleft

		# Get the tile size
		tile_size = self.manager.config_options['tile_size']

		# Collision with a ghost
		for i in range(GHOSTS):
			if self.state.pacman_rect.colliderect(self.state.ghost_rect[i]):
				status = self.handle_collision(i)
				if status:
					return status

		# Get relevant corners to check for events
		first_corner, second_corner = self.checker.get_relevant_corners(current_position, self.state.current_pacman_direction, 0)

		# This is for wraparound world
		if self.checker.out_of_bounds(first_corner) == RIGHT:
			self.state.pacman_rect.topleft = (0, current_position[1])
		elif self.checker.out_of_bounds(first_corner) == DOWN:
			self.state.pacman_rect.topleft = (current_position[0], 0)
		elif self.checker.out_of_bounds(first_corner) == LEFT:
			self.state.pacman_rect.topleft = (self.state.level.level_dim[0] * tile_size - tile_size, current_position[1])
		elif self.checker.out_of_bounds(first_corner) == UP:
			self.state.pacman_rect.topleft = (current_position[0], self.state.level.level_dim[1] * tile_size - tile_size)

		# Pellet
		if self.is_pellet(self.state.pacman_rect.topleft):
			self.state.level.num_pellets -= 1
			self.state.score += 10
			self.clear_tile(self.state.pacman_rect.topleft)

		# Power pellet
		if self.is_power_pellet(self.state.pacman_rect.topleft):
			self.state.level.num_pellets -= 1
			self.state.score += 50
			self.clear_tile(self.state.pacman_rect.topleft)
			self.set_ghost_mode_all(VULNERABLE)

		# Check whether the level is clear
		if self.state.level.num_pellets == 0:
			return NEXT_LEVEL

		# If the next move is valid, then set the current move to be that
		if self.checker.is_valid_move("pacman", self.state.pacman_rect.topleft, self.state.next_pacman_direction):
			self.state.current_pacman_direction = self.state.next_pacman_direction

		# Wall
		if not self.checker.is_valid_move("pacman", self.state.pacman_rect.topleft, self.state.current_pacman_direction):
			self.state.pacman_immobile = True
			return CONTINUE

		# Since the current move is valid, we are moving
		self.state.pacman_immobile = False

		# Calculate the offset for the current move
		velocity = self.manager.config_options['pacman_velocity']
		if self.state.current_pacman_direction == UP:
			position_offset = (0, -velocity)
		elif self.state.current_pacman_direction == DOWN:
			position_offset = (0, velocity)
		elif self.state.current_pacman_direction == LEFT:
			position_offset = (-velocity, 0)
		elif self.state.current_pacman_direction == RIGHT:
			position_offset = (velocity, 0)
		
		# Effect current move
		self.state.pacman_rect.topleft = (self.state.pacman_rect.topleft[0] + position_offset[0], self.state.pacman_rect.topleft[1] \
									+ position_offset[1])

		return CONTINUE

#------------------------------------------------------------------------------
# update_ghost()
#------------------------------------------------------------------------------

	def update_ghost(self, ghost_id):
		"Updates the state according to the ghost's current action"

		if ghost_id not in range(GHOSTS):
			raise PacmanError("Updater: Invalid ghost ID given to update_ghost")

		# Get the ghost's current position and the tile size
		current_position = self.state.ghost_rect[ghost_id].topleft
		tile_size = self.manager.config_options['tile_size']

		# Check the ghost's mode
		if self.state.ghost_mode[ghost_id] == VULNERABLE:
			self.state.ghost_timer[ghost_id] -= 1
			if self.state.ghost_timer[ghost_id] == 0:
				self.set_ghost_mode(ghost_id, NORMAL)
		elif self.state.ghost_mode[ghost_id] == EYES:
			if self.state.ghost_rect[ghost_id].topleft == self.state.level.ghost_home[INKY]:
				self.set_ghost_mode(ghost_id, NORMAL)

		# Get relevant corners to check for events
		first_corner, second_corner = self.checker.get_relevant_corners(current_position, self.state.current_ghost_direction[ghost_id], 0)

		# This is for wraparound world
		if self.checker.out_of_bounds(first_corner) == RIGHT:
			self.state.ghost_rect[ghost_id].topleft = (1, current_position[1])
		elif self.checker.out_of_bounds(first_corner) == DOWN:
			self.state.ghost_rect[ghost_id].topleft = (current_position[0], 1)
		elif self.checker.out_of_bounds(first_corner) == LEFT:
			self.state.ghost_rect[ghost_id].topleft = (self.state.level.level_dim[0] * tile_size - tile_size, current_position[1])
		elif self.checker.out_of_bounds(first_corner) == UP:
			self.state.ghost_rect[ghost_id].topleft = (current_position[0], self.state.level.level_dim[1] * tile_size - tile_size)

		# If the ghost's next move is valid, set its current move to be that
		if self.checker.is_valid_move(str(ghost_id), self.state.ghost_rect[ghost_id].topleft, self.state.next_ghost_direction[ghost_id]):
			self.state.current_ghost_direction[ghost_id] = self.state.next_ghost_direction[ghost_id]

		# Wall
		if not self.checker.is_valid_move(str(ghost_id), self.state.ghost_rect[ghost_id].topleft, self.state.current_ghost_direction[ghost_id]):
			self.state.ghost_immobile[ghost_id] = True
			return CONTINUE

		self.state.ghost_immobile[ghost_id] = False

		# Figure out how what offset to add to the current position
		velocity = self.manager.config_options['ghost_velocity']
		if self.state.current_ghost_direction[ghost_id] == UP:
			position_offset = (0, -velocity)
		elif self.state.current_ghost_direction[ghost_id] == DOWN:
			position_offset = (0, velocity)
		elif self.state.current_ghost_direction[ghost_id] == LEFT:
			position_offset = (-velocity, 0)
		elif self.state.current_ghost_direction[ghost_id] == RIGHT:
			position_offset = (velocity, 0)

		# Effect current move
		self.state.ghost_rect[ghost_id].topleft = (self.state.ghost_rect[ghost_id].topleft[0] + position_offset[0], \
		                            self.state.ghost_rect[ghost_id].topleft[1] + position_offset[1])

		return CONTINUE

#------------------------------------------------------------------------------
# reset_game()
#------------------------------------------------------------------------------

	def reset_game(self):
		"Resets the game"

		# Simply load the first level
		self.load_first_level()

#------------------------------------------------------------------------------
# reset_agents()
#------------------------------------------------------------------------------

	def reset_agents(self):
		"Resets all agents"

		# Set default pacman attributes
		self.state.pacman_rect.topleft = self.state.level.pacman_home
		self.state.next_pacman_direction = LEFT
		self.state.current_pacman_direction = LEFT
		self.state.pacman_immobile = True

		# Set default ghost attributes	
		self.reset_all_ghost_timers()

		for i in range(GHOSTS):
			if i != BLINKY:
				self.state.next_ghost_direction[i] = DOWN
				self.state.current_ghost_direction[i] = DOWN
			else:
				self.state.next_ghost_direction[i] = UP
				self.state.current_ghost_direction[i] = UP
			self.state.ghost_rect[i].topleft = self.state.level.ghost_home[i]
			self.state.ghost_mode[i] = NORMAL
			self.state.ghost_immobile[i] = True



