###############################################################################
#
# ai_pacman.py
#
#
###############################################################################

#------------------------------------------------------------------------------
#
# Pacman Agent Class
# 
# This class implements the function approximation version of the AI Pacman.
#
#------------------------------------------------------------------------------

# Module imports
from common import *
import pprint, random, os, math, time, features, sys

# Constants
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]
DEATH = 1
LEVEL_CLEAR = 2
BIG_NUMBER = 10000000000
DEFAULT_COEFFS = { UP: 0.0, DOWN: 0.0, LEFT: 0.0, RIGHT: 0.0 }

# Comparison function for comparing q-value entries with Python's
# sort routine.
def compare_q(x, y):
        if x[1] < y[1]:
                return -1
        elif x[1] == y[1]:
                return 0
        else:
                return 1

# Main Pacman AI class.
class Pacman:

#------------------------------------------------------------------------------
# __init__()
#------------------------------------------------------------------------------

	def __init__(self, state, game_engine):
		# Set the state and game engine.
		self.state = state
		self.game = game_engine

		# Create a features object that will be used to compute the current features
		# of the state that Pacman cares about.
		self.features = features.Features(state, game_engine)
		self.feature_dict = None
		self.prev_features = {}

		# Load the training data from file.
		self.training_data = {}
		self.load_training_data()

		# Initialize other state that is used by the learning algorithm.
		self.cur_qvals = {}
		self.decision_count = 0
		self.prev_action = None
		self.prev_qval = None
		self.call_counter = 0

		# Initialize attributes for tracking results.
		self.results_mode = self.game.manager.config_options['results_mode']
		self.results_games = self.game.manager.config_options['results_games']
		self.games_count = 0
		self.average_score = 0.0
		self.average_level = 0.0

#------------------------------------------------------------------------------
# load_training_data()
#------------------------------------------------------------------------------

	def load_training_data(self):
		"Loads the training set file and initializes the training_data dictionary"
		try:
			experience = open(self.game.manager.config_options['training_file_start'], 'r')
			self.training_data = eval(experience.read())
			experience.close()

		except:
			raise PacmanError('AI Pac-Man: Training set file failed to load')

		# Make shorter references to the data that is used a lot.
		self.theta = self.training_data['theta']
		self.times = self.training_data['times']
		self.gamma = self.training_data['gamma']

		# If a feature that is needed is not in the theta dictionary, then add and initialize it.
		for feature in self.features.features.keys():
			if feature not in self.theta:
				self.theta[feature] = dict(DEFAULT_COEFFS)

		# If a direction is not in the times dictionary, then add and initialize it.
		for dir in DIRECTIONS:
			if dir not in self.times:
				self.times[dir] = 0

#------------------------------------------------------------------------------
# save_training_data()
#------------------------------------------------------------------------------

	def save_training_data(self):
		"Saves the training data to a file"

		# Do not write the results out if the system is in results mode.
		# This means that the user should bump up the iterations count in the config file.
		if self.results_mode:
			print 'Error from pacman.save_training_data().'
			print 'Not enough iterations in config file to finish the games for results mode.'
			print 'The system will not output the training data to file.'
			return

		# Otherwise, proceed with writing the file out.
		try:
			experience = open(self.game.manager.config_options['training_file_end'], 'w')
			pprint.pprint(self.training_data, experience, 4)
			experience.close()
		except:
			experience = open('training_backup.txt', 'w')
			pprint.pprint(self.training_data, experience, 4)
			experience.close()
			raise PacmanError('AI Pac-Man: Training set file specified in config file was inaccessible, \
							   saved to training_backup.txt instead')

#------------------------------------------------------------------------------
# compute_results()
#------------------------------------------------------------------------------

	def compute_results(self, status):
		"Computes the average score and level count for the AI Pac-Man."

		# Only do these tasks if we are keeping track of the results.
		if not self.results_mode:
			return

		# Check to see if Pac-Man has died and ran out of lives.
		if status == DEATH and self.state.pacman_lives == 1:
			# Reinitialize this object so it does not learn between games.
			self.load_training_data()

			# Update the games count and the average score
			self.average_score += (self.state.score - self.average_score) / float(self.games_count + 1)
			self.average_level += (self.state.level_number - self.average_level) / float(self.games_count + 1)
			self.games_count += 1
			print 'Completed',self.games_count,'out of',self.results_games

		# If a results collection run is over, output the averages and end execution.
		if self.games_count == self.results_games:
			print 'Testing run ended.'
			print 'Games:', self.games_count
			print 'Average score:', self.average_score
			print 'Average level achieved:', self.average_level
			sys.exit(1)


#------------------------------------------------------------------------------
# get_next_move()
#------------------------------------------------------------------------------

	def get_next_move(self):
		"Sets the next move for Pac-Man"

		# The call_counter is used to keep Pac-Man from making decisions constantly.
		self.call_counter += 1

		# This condition makes Pac-Man make a decision when the call_counter is equal to tile_size / pacman_velocity, which is
		# equivalent to saying that Pac-Man makes one decision per tile.
		if self.call_counter == (self.game.manager.config_options['tile_size'] / self.game.manager.config_options['pacman_velocity']):
			self.game.set_pacman_direction(self.make_decision())
			self.call_counter = 0

		# If Pac-man is at the home position, he always makes a decision to get the level started.
		elif self.state.pacman_rect.topleft == self.state.level.pacman_home:
			self.game.set_pacman_direction(self.make_decision())
			self.call_counter = 0

		# If a terminal state is found (level cleared or death), then Pac-Man needs to see the state so he can be rewarded
		# properly for the state to update the learning data.
		elif self.check_terminal_state():
			self.game.set_pacman_direction(self.make_decision())
			self.call_counter = 0


#------------------------------------------------------------------------------
# get_reward()
#------------------------------------------------------------------------------

	def get_reward(self):
		"Compute the reward for the current simplified state"

		# Note: This function returns a tuple of the reward and the relevant feature set.
		# We found that our algorithm performs much better if we only update the theta values
		# for features related to the reward.

		# Death
		status = self.check_terminal_state()
		if status == DEATH:
			return (-10000, 'ghost')

		# Give a negative reward for having ghosts even go near Pacman.
		# This will teach him to avoid ghosts even better.
		pacman_position = self.state.pacman_rect.topleft
		tile_size = self.game.manager.config_options['tile_size']
		minimum = 1000
		for i in range(GHOSTS):
			if self.state.ghost_mode[i] == NORMAL:
				ghost_position = self.state.ghost_rect[i].topleft
				distance_x = ghost_position[0] - pacman_position[0]
				distance_y = ghost_position[1] - pacman_position[1]
				manhattan_distance = abs(distance_x) + abs(distance_y)
				if manhattan_distance < minimum:
					minimum = manhattan_distance

		# Return -1000 for a ghost being right next to Pacman and -500 for a ghost being
		# two tiles away from Pacman.
		if (minimum / tile_size) == 1:
			return (-1000, 'ghost')
		elif (minimum / tile_size) == 2:
			return (-500, 'ghost')


		# Return 100 for Pacman eating a pellet and -10 for not eating a pellet.
		if self.game.updater.is_pellet(self.state.pacman_rect.topleft):
			return (100, 'pellet')
		else:
			return (-10, 'pellet')
	


#------------------------------------------------------------------------------
# compute_qvals()
#------------------------------------------------------------------------------

	def compute_qvals(self):
		"Compute the qvals for the current state"
		for action in DIRECTIONS:
			self.cur_qvals[action] = self.compute_qval(action)


#------------------------------------------------------------------------------
# compute_qval()
#------------------------------------------------------------------------------

	def compute_qval(self, action):
		"Based on the current features and action coefficients, compute the current qval"

		# The current Q-Value is the dot product of the features vector and the theta
		# vector for the current action.
		qval = 0
		for feature in self.feature_dict.keys():
			value = self.feature_dict[feature]
			coeff = self.theta[feature][action]
			qval += (value * coeff)
		return qval


#------------------------------------------------------------------------------
# get_policy_action()
#------------------------------------------------------------------------------

	def get_policy_action(self):
		"Get the next move according to our policy"

		# Our policy is epsilon greedy with the extension that Pac-Man will
		# only take valid moves and will not go backwards unless a ghost is in
		# front of him or backwards is the only valid move.

		# Get the current position and sorted Q-Values list.
		current_position = self.state.pacman_rect.topleft
		cur_qval_items = self.cur_qvals.items()
		cur_qval_items.sort(compare_q, reverse=True)

		# Initialize the current action to backwards. Without a ghost in front of Pacman, 
		# this only occurs if Pacman cannot go any other direction.
		cur_action = -self.state.current_pacman_direction

		# Loop until a valid action is found. Moves with better Q-Values will come first in
		# the cur_qval_items list.
		valid_moves = []
		for i in cur_qval_items:
			if i[0] == -self.state.current_pacman_direction and not self.feature_dict['ghost_distance_'+MOVE_LOOKUP[-i[0]]]:
				# Skip backwards if no ghosts are in front of Pacman.
				continue
			if self.game.checker.is_valid_move('pacman', current_position, i[0]):
				cur_action = i[0]
				break
		
		return cur_action



#------------------------------------------------------------------------------
# check_terminal_state()
#------------------------------------------------------------------------------

	def check_terminal_state(self):
		"Returns true when Pac-Man dies or clears a level"

		# For each ghost, see if Pacman is colliding with the ghost.
		for i in range(GHOSTS):
			if self.state.pacman_rect.colliderect(self.state.ghost_rect[i]) and self.state.ghost_mode[i] == NORMAL:
				return DEATH

		# If there is one pellet left and that pellet is touching Pacman, then the level is clear.
		if self.state.level.num_pellets == 1 and (self.game.updater.is_pellet(self.state.pacman_rect.topleft) or \
				self.game.updater.is_power_pellet(self.state.pacman_rect.topleft)):
			return LEVEL_CLEAR

		return 0


#------------------------------------------------------------------------------
# make_decision()
#------------------------------------------------------------------------------

	def make_decision(self):
		"Make decision actually updates the theta values and returns the next action"

		# Get the feature values for the current state.
		cur_reward = self.get_reward()
		self.feature_dict = self.features.get_features()

		# Compute the Q-Value estimates for the current state.
		# This updates the cur_qvals dictionary.
		self.compute_qvals()

		# Get the next action according to our policy.
		greedy_action = self.get_policy_action()

		randvar = random.random()
		if randvar < self.get_epsilon():
			# Explore

			# Get our current direction and position
			current_direction = self.state.current_pacman_direction
			current_position = self.state.pacman_rect.topleft

			# Out of the possible directions, pick a random one that is valid.
			# If all other directions are invalid, then go backwards.
			possible_directions = list(DIRECTIONS)
			valid = False
			new_direction = 0
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
			cur_action = greedy_action

		# If this is not the first move of a game and results mode is not on, then update
		# the thetas for the approximation for each feature. The equation used here is
		# described in detail in our project report.
		if self.prev_action != None and not self.results_mode:
			last_qval = self.prev_qval
			max_qval = self.cur_qvals[greedy_action]
			for feature in self.prev_features.keys():
				if cur_reward[1] in feature:
					self.theta[feature][self.prev_action] += (cur_reward[0] + (self.gamma * max_qval) - last_qval) \
							* (self.prev_features[feature] / (self.times[self.prev_action] + 1.0))

		# Update the times count for the current action.
		self.times[cur_action] += 1


		# If we are in a terminal state, then reset the state for the learning algorithm so
		# what is happening now does not propagate into the next game.
		status = self.check_terminal_state()
		if status in [DEATH, LEVEL_CLEAR]:
			self.prev_qval = None
			self.prev_action = None
			self.prev_features = {}
			self.decision_count = 0

			# Print a message to help monitor training.
			print 'finished game ',self.training_data['games_count'], {DEATH: 'DEATH', LEVEL_CLEAR:'LEVEL_CLEAR'}[status]
			self.training_data['games_count'] += 1

			self.compute_results(status)

		else:
			# Update the state for the next decision.
			self.prev_qval = self.cur_qvals[cur_action]
			self.prev_action = cur_action
			self.prev_features = dict(self.feature_dict)
			self.decision_count += 1


		# Return the action that was picked.
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

