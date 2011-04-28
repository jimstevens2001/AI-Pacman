###############################################################################
#
# ai_pacman_qval.py
#
###############################################################################

from common import *
import pprint, random, os, math

#------------------------------------------------------------------------------
#
# Ghost class
#
# This class implements an explicit state table method of
# Q-learning for the Pac-Man AI. As of now it can still be
# expanded to include more state.
#
#------------------------------------------------------------------------------

CLOSE 			= 5

UP_SAFE			= 0x1
DOWN_SAFE		= 0x2
LEFT_SAFE		= 0x4
RIGHT_SAFE		= 0x8

UP_PELLETS		= 0x10
DOWN_PELLETS	= 0x20
LEFT_PELLETS	= 0x40
RIGHT_PELLETS	= 0x80

DEATH			= 0x100
LEVEL_CLEAR		= 0x200
GOT_PELLET		= 0x400

DEFAULT_QDICT = { UP: 0.0, DOWN: 0.0, LEFT: 0.0, RIGHT: 0.0 }
DEFAULT_TIMES = { UP: 0, DOWN: 0, LEFT: 0, RIGHT: 0 }

PRINT_PELLETS = {UP_PELLETS: 'UP_PELLETS', DOWN_PELLETS: 'DOWN_PELLETS', LEFT_PELLETS: 'LEFT_PELLETS', RIGHT_PELLETS: 'RIGHT_PELLETS'}

#------------------------------------------------------------------------------
# compare_q()
#------------------------------------------------------------------------------

def compare_q(x, y):
        if x[1] < y[1]:
                return -1
        elif x[1] == y[1]:
                return 0
        else:
                return 1

class Pacman:

#------------------------------------------------------------------------------
# __init__()
#------------------------------------------------------------------------------

	def __init__(self, state, game_engine):
		self.state = state
		self.game = game_engine

		# Initialize the training data
		self.training_data = {}
		self.load_training_data()

		# Initialize the various components of the learning algorithm
		# Qvals is a dictionary for the Q-values, times holds the number
		# of times a state-action pair has been seen, and gamma is the
		# discount rate.
		self.qvals = self.training_data['qvals']
		self.times = self.training_data['times']
		self.gamma = self.training_data['gamma']

		self.decision_count = 0
		self.prev_action = None
		self.prev_state = None

		self.tmp_counter = 0
		self.call_counter = 0

#------------------------------------------------------------------------------
# load_training_data()
#------------------------------------------------------------------------------

	def load_training_data(self):
		"Loads the training set file"
		try:
			experience = open(self.game.manager.config_options['training_file_start'], 'r')
			self.training_data = eval(experience.read())
			experience.close()
		except:
			raise PacmanError('AI Pac-Man: Training set file failed to load')

#------------------------------------------------------------------------------
# save_training_data()
#------------------------------------------------------------------------------

	def save_training_data(self):
		"Saves the training data to a file"
		try:
			experience = open(self.game.manager.config_options['training_file_end'], 'w')
			pprint.pprint(self.training_data, experience, 4)
			experience.close()
		except:
			# Training data is very valuable, so in case the writing failed, we need a backup plan
			experience = open('training_backup.txt', 'w')
			pprint.pprint(self.training_data, experience, 4)
			experience.close()
			raise PacmanError('AI Pac-Man: Training set file specified in config file was inaccessible, \
							   saved to training_backup.txt instead')

#------------------------------------------------------------------------------
# get_next_move()
#------------------------------------------------------------------------------

	def get_next_move(self):
		"Sets the next move for Pac-Man"

		# Update the move counter
		self.call_counter += 1

		# If we are in our home position, we should make a decision right away
		if self.state.pacman_rect.topleft == self.state.level.pacman_home:
			self.game.set_pacman_direction(self.make_decision())
			self.call_counter = 0

		# We only want to make new decision every time we reach a new tile
		if self.call_counter == (self.game.manager.config_options['tile_size'] / self.game.manager.config_options['pacman_velocity']):
			self.game.set_pacman_direction(self.make_decision())
			self.call_counter = 0

		# If a terminal state is found (level cleared or death), then Pac-Man needs to see the state so he can be rewarded
		# properly for the state to update the learning data.
		elif self.check_terminal_state():
			self.game.set_pacman_direction(self.make_decision())
			self.call_counter = 0

#------------------------------------------------------------------------------
# check_terminal_state()
#------------------------------------------------------------------------------

	def check_terminal_state(self):
		"This function returns true if Pac-Man dies or clears a level"

		# Check for any collision with a ghost
		for i in range(GHOSTS):
			if self.state.pacman_rect.colliderect(self.state.ghost_rect[i]) and self.state.ghost_mode[i] == NORMAL:
				return DEATH

		# Check whether we've cleared the level
		if self.state.level.num_pellets == 1 and (self.game.updater.is_pellet(self.state.pacman_rect.topleft) or \
				self.game.updater.is_power_pellet(self.state.pacman_rect.topleft)):
			return LEVEL_CLEAR

		return 0

#------------------------------------------------------------------------------
# organize_pellets_by_direction()
#------------------------------------------------------------------------------

	def organize_pellets_by_direction(self):
		"This function finds the closes pellet to Pac-Man in any direction"

		# Get Pac-Man's current position
		pacman_position = self.state.pacman_rect.topleft

		# Get his corresponding tile coordinates
		tile_position = self.game.checker.get_tile_coordinates(pacman_position)

		# Get the tile size
		tile_size = self.game.manager.config_options['tile_size']

		# Set an arbitrarily large initial minimum distance
		minimum = 999

		# Initialize the possible pellet positions
		pellet_positions = {LEFT_PELLETS: 0, RIGHT_PELLETS: 0, UP_PELLETS: 0, DOWN_PELLETS: 0}

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
								pellet_positions[LEFT_PELLETS] = 1
								pellet_positions[RIGHT_PELLETS] = 0
								pellet_positions[UP_PELLETS] = 0
								pellet_positions[DOWN_PELLETS] = 0
							# It is to our right
							elif distance_x > 0:
								pellet_positions[LEFT_PELLETS] = 0
								pellet_positions[RIGHT_PELLETS] = 1
								pellet_positions[UP_PELLETS] = 0
								pellet_positions[DOWN_PELLETS] = 0
						else:

							# It is above us
							if distance_y < 0:
								pellet_positions[LEFT_PELLETS] = 0
								pellet_positions[RIGHT_PELLETS] = 0
								pellet_positions[UP_PELLETS] = 1
								pellet_positions[DOWN_PELLETS] = 0
							# It is below us
							elif distance_y > 0:
								pellet_positions[LEFT_PELLETS] = 0
								pellet_positions[RIGHT_PELLETS] = 0
								pellet_positions[UP_PELLETS] = 0
								pellet_positions[DOWN_PELLETS] = 1

		return pellet_positions

#------------------------------------------------------------------------------
# divide_ghosts_by_direction()
#------------------------------------------------------------------------------

	def divide_ghosts_by_direction(self):
		"This function finds out whether this is a ghost in any direction"

		# Initialize the possible positions and values
		ghost_positions = {UP_SAFE: True, DOWN_SAFE: True, LEFT_SAFE: True, RIGHT_SAFE: True}

		# Get Pac-Man's current tile coordinates
		pacman_tile = self.game.checker.get_tile_coordinates(self.state.pacman_rect.topleft)

		# Look at each ghost, and figure out whether it is closer than CLOSE tiles to Pac-Man
		for i in range(GHOSTS):

			# First, get the ghost's tile coordinates
			ghost_tile = self.game.checker.get_tile_coordinates(self.state.ghost_rect[i].topleft)

			# Then figure out the Manhattan distance
			distance_x = ghost_tile[0] - pacman_tile[0]
			distance_y = ghost_tile[1] - pacman_tile[1]

			# If the ghost is close and can eat us, then determine where he is
			if abs(distance_x) <= CLOSE and abs(distance_y) <= CLOSE and self.state.ghost_mode[i] == NORMAL:
				# He is to our left
				if distance_x <= 0:
					ghost_positions[LEFT_SAFE] = False
				# To our right
				else:
					ghost_positions[RIGHT_SAFE] = False
				# Above
				if distance_y <= 0:
					ghost_positions[UP_SAFE] = False
				# Below
				else:
					ghost_positions[DOWN_SAFE] = False

		return ghost_positions

#------------------------------------------------------------------------------
# simplify_states()
#------------------------------------------------------------------------------

	def simplify_state(self):
		"Simplify the real state into the simple state"

		# The state is represented using bit masks
		simplified_state = 0

		# Find the closest pellets and add this information to the state
		pellet_split = self.organize_pellets_by_direction()
		for position in pellet_split:
			if pellet_split[position]:
				simplified_state |= position

		# Figure out whether we are eating a pellet right now
		if self.game.updater.is_pellet(self.state.pacman_rect.topleft):
			simplified_state |= GOT_PELLET

		# Check whether we just died
		#for i in range(GHOSTS):
		#	if self.state.pacman_rect.colliderect(self.state.ghost_rect[i]) and self.state.ghost_mode[i] == NORMAL:
		#		simplified_state |= DEATH

		# Check whehter we cleared the level
		#if self.state.level.num_pellets == 0:
		#	simplified_state |= LEVEL_CLEAR

		return simplified_state

#------------------------------------------------------------------------------
# get_reward()
#------------------------------------------------------------------------------

	def get_reward(self, state):
		"Compute the reward for the current simplified state"
		# The following is commented out for now but could easily be reintegrated
		"""if (state & DEATH):
			return -1000
		elif (state & LEVEL_CLEAR):
			return 1000
		else:
			reward = 0
			for i in [UP_PELLETS, DOWN_PELLETS, LEFT_PELLETS, RIGHT_PELLETS]:
				if (state & i):
					reward -= 1
				else:
					reward += 1"""

		# Only give rewards for pellets
		if (state & GOT_PELLET):
			return 100.0
		else:
			return -10.0

#------------------------------------------------------------------------------
# reverse_lookup()
#------------------------------------------------------------------------------

	def reverse_lookup(self, d, v):
		"This function finds the key corresponding to a value in a dictionary"
		for i in d.keys():
			if d[i] == v:
				return i

#------------------------------------------------------------------------------
# make_decision()
#------------------------------------------------------------------------------

	def make_decision(self):
		"This function make a decision for the next action"

		# Get the simplified state
		cur_state = self.simplify_state()

		# Add it to the state table if it is not already in there
		if cur_state not in self.qvals:
			self.qvals[cur_state] = dict(DEFAULT_QDICT)
			self.times[cur_state] = dict(DEFAULT_TIMES)

		# Get the reward for the current state
		cur_reward = self.get_reward(cur_state)

		# Generate a random number to choose between exploring and exploiting
		randvar = random.random()

		# Compare the random number to our policy
		if randvar < self.get_epsilon():
			# We are exploring

			# Get our current direction and position
			current_direction = self.state.current_pacman_direction
			current_position = self.state.pacman_rect.topleft

			possible_directions = [UP, DOWN, LEFT, RIGHT]

			valid = False
			new_direction = 0
			# Here we are immobile so we need to find a new direction that is valid
			while new_direction == -current_direction or not valid:
				new_direction = random.choice(possible_directions)
				valid = self.game.checker.is_valid_move('pacman', current_position, new_direction)
				possible_directions.remove(new_direction)
				if not possible_directions:
					new_direction = -current_direction
					break

			cur_action = new_direction
		else:
			# Exploit
			current_position = self.state.pacman_rect.topleft
			cur_qval_items = self.qvals[cur_state].items()
			cur_qval_items.sort(compare_q, reverse=True)

			valid_moves = []
			for i in cur_qval_items:
				if self.game.checker.is_valid_move('pacman', current_position, i[0]):
					if valid_moves and i[1] > valid_moves[0]:
						valid_moves.pop(0)
					valid_moves.append(i[0])
			if len(valid_moves) > 1 and -self.state.current_pacman_direction in valid_moves:
				valid_moves.remove(-self.state.current_pacman_direction)
			cur_action = valid_moves[0]

		if self.prev_action != None:
			# Get the Q-value for the last state
			last_qval = self.qvals[self.prev_state][self.prev_action]
			# Get the maximum Q-value for the current state
			max_qval = max(self.qvals[cur_state].values())
			# Update the Q-value for the previous state
			self.qvals[self.prev_state][self.prev_action] = last_qval + (cur_reward + (self.gamma * max_qval) - last_qval) \
					/ (self.times[self.prev_state][self.prev_action] + 1.0)

			# Update the times count
			self.times[cur_state][self.prev_action] += 1

		# If we died or cleared a level last time, we do not want update the next Q-val
		if self.check_terminal_state():
			self.prev_action = None
			self.prev_state = None
			print 'game ended',self.training_data['games_count']
			self.training_data['games_count'] += 1
		else:
			self.prev_state = cur_state
			self.prev_action = cur_action


		# Update the decision count.
		self.decision_count += 1

		return cur_action

#------------------------------------------------------------------------------
# get_epsilon()
#------------------------------------------------------------------------------

	def get_epsilon(self):
		"Computes epsilon (the probability of exploration)"

		# M: maximum epsilon value
		M = self.training_data['epsilon_params']['max_value']

		# C: Convergence Rate
		C = self.training_data['epsilon_params']['convergence_rate']

		# A: Repeat number (repeat the decay after A games)
		A = self.training_data['epsilon_params']['repeat_number']

		# Set the games count and the decision count.
		i = self.training_data['games_count']
		j = self.decision_count

		# Compute the current epsilon value.
		# In simple terms this is an exponential decay towards 1 as j increases.
		# The i value is used to modify the exponential curve as system plays more
		# games so that an inexperienced agent will explore towards the beginning of
		# the game and an experienced agent will exploit early in the game (we assume
		# that they have learned that part of the game) and explore later in the game. 
		# The convergence rate controls how fast the curve shifts as the agent becomes
		# more experienced. Finally, the repeat number is used to determine after how
		# many games the agent should repeat this curve. This is useful because it is
		# effectively 
		ep = M*(1 - math.exp(-(j+1)/(C * ((i % A)+1))))

		return ep
