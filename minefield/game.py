#############################################################################
# Minefield Game
#
# Purpose: To test explicit Q-value reinforcement learning using a simple
# world. The goal is that we will use this test to be able to better reason
# about how reinforcement learning works so the knowledge can be applied
# to the much more complicated Pac-Man system.
#
#############################################################################

# Module Imports
import psyco
psyco.full()

import sys
import pprint 
import random
import math

# Set up a pretty printer object
pp = pprint.PrettyPrinter()

# Globals (will be set by the configuration file)
XDIM = 0
YDIM = 0
EPSILON = 0
CONVERGENCE_RATE = 1.0
REPEAT = 1.0
MAX = 1.0
GAMMA = 0.1
TESTS = 1
CUTOFF = 1
OUT = (1, 100)

# Constants
PLAYER = 'O'
GOAL = 'X'
SPACE = '-'
PIT = '#'
DOWN = (0,1)
UP = (0,-1)
LEFT = (-1, 0)
RIGHT = (1,0)
dir = (UP, DOWN, LEFT, RIGHT)
dirname = {UP: 'u', DOWN: 'd', LEFT: 'l', RIGHT: 'r'}

# The reward function returns the reward of the current state.
def reward(s):
	if s == GOAL:
		return 100.0
	elif s == PIT:
		return -100.0
	else:
		return -1.0

# The epsilon function returns the probability of exploration.
# It takes i (the games count) and j (the move count).
# Based on the global EPSILON, it picks a function to use.
def epsilon(i, j):
	if EPSILON == 'constant':
		return MAX
	elif EPSILON == 'i':
		return MAX*math.exp(-i/CONVERGENCE_RATE)
	elif EPSILON == 'ij':
		return MAX*(1-math.exp(-j/(CONVERGENCE_RATE*(i+1))))
	elif EPSILON == 'repeat':
		return MAX*(1-math.exp(-j/(CONVERGENCE_RATE*((i % REPEAT)+1))))

# Returns True if a position is within the board and false otherwise.
def isvalid(pos):
	if pos[0] < 0 or pos[0] >= XDIM or pos[1] < 0 or pos[1] >= YDIM:
		return False
	else:
		return True

# Applies a move to a position to return a new position.
def apply_move(pos, move):
	return (pos[0] + move[0], pos[1] + move[1])

# Lookup a value in a dictionary and get the key.
def reverse_lookup(d, v):
	for i in d.keys():
		if d[i] == v:
			return i
	
# Print the board with the type of each position.
def printboard(game, player_pos):
	for i in range(YDIM):
		outstr = ''
		for j in range(XDIM):
			if player_pos == (j, i):
				outstr += PLAYER
			else:
				outstr += game[(j, i)]
		print outstr

# Print the board with the best direction of each position.
# The best direction is determined by the qval dictionary.
def printboard_dirs(game, qval):
	for i in range(YDIM):
		outstr = ''
		for j in range(XDIM):
			if game[(j, i)] != SPACE:
				outstr += game[(j, i)]
			else:
				max_val = max(qval[(j, i)].values())
				outstr += dirname[reverse_lookup(qval[(j, i)], max_val)]
		print outstr

# Read the level file and set the XDIM and YDIM.
# Returns the game board and the starting position.
def read_level(level):
	global XDIM
	global YDIM

	inFile = open(level, 'r')
	lines = inFile.readlines()
	inFile.close()
	lines = [i.strip() for i in lines]

	header = lines[0].split()
	XDIM = int(header[0])
	YDIM = int(header[1])
	START = (int(header[2]), int(header[3]))

	print '(XDIM, YDIM) = ', (XDIM, YDIM)
	print 'START = ', START
	print

	game = {}
	for i in range(YDIM):
		for j in range(XDIM):
			game[(j, i)] = lines[1+i][j]

	return game, START

# Read the config file and set all of the globals needed for execution.
def read_config(config):
	global EPSILON
	global CONVERGENCE_RATE
	global REPEAT
	global MAX
	global GAMMA
	global TESTS
	global CUTOFF
	global OUT

	inFile = open(config, 'r')
	config_dict = eval(inFile.read())
	inFile.close()

	print config_dict

	EPSILON = config_dict['EPSILON']
	CONVERGENCE_RATE = config_dict['CONVERGENCE_RATE']
	REPEAT = config_dict['REPEAT']
	MAX = config_dict['MAX']
	GAMMA = config_dict['GAMMA']
	TESTS = config_dict['TESTS']
	CUTOFF = config_dict['CUTOFF']
	OUT = config_dict['OUT']

	print 'EPSILON',EPSILON
	print 'CONVERGENCE_RATE', CONVERGENCE_RATE
	print 'REPEAT', REPEAT
	print 'MAX', MAX
	print 'GAMMA', GAMMA
	print 'TESTS', TESTS
	print 'CUTOFF', CUTOFF
	print 'OUT', OUT


# The main function performs initialization, learning, and reporting.
def main():
	# Get the args
	if len(sys.argv) < 3:
		print len(sys.argv)
		print 'Usage: '+sys.argv[0]+' level config'
		sys.exit(1)
	level = sys.argv[1]
	config = sys.argv[2]

	# Read the input files.
	game, START = read_level(level)
	read_config(config)

	# Initialize the state
	cur_pos = START
	prev_action = -1
	prev_pos = -1

	# Initialize the data structures that track results.
	reward_list = []
	reward_total = 0
	reward_cnt = 0

	# Initialize q-value dictionary.
	qval = {}
	times = {}
	for i in range(YDIM):
		for j in range(XDIM):
			pos = (j, i)
			qval[pos] = {}
			times[pos] = {}
			for k in dir:
				if isvalid(apply_move(pos, k)):
					qval[pos][k] = 0.0
					times[pos][k] = 0
	# Run the training.
	# For each game.
	for i in range(TESTS):
		# Output current results every once in awhile.
		if i % OUT[1] == 0:
			sys.stderr.write(str(i))
			sys.stderr.write(' : '+str(epsilon(i, 0)))
			if len(reward_list) > 1:
				sys.stderr.write(' : '+str(reward_list[-1]))
			sys.stderr.write('\n')

		# For each move in the game.
		for j in range(CUTOFF):
			# Get the reward for this state.
			cur_reward = reward(game[cur_pos])
			reward_total += cur_reward

			# Decide to explore or exploit.
			randvar = random.random()
			if randvar < epsilon(i, j):
				# Explore
				cur_action = qval[cur_pos].keys()[random.randint(0, len(qval[cur_pos])-1)]
			else:
				# Exploit
				max_var = max(qval[cur_pos].values())
				cur_action = reverse_lookup(qval[cur_pos], max_var)

			
			# Update the Q-Value table.
			if prev_pos != -1:
				last_qval = qval[prev_pos][prev_action]
				max_qval = max(qval[cur_pos].values())
				qval[prev_pos][prev_action] = last_qval + (cur_reward + (GAMMA * max_qval) - last_qval) / (times[cur_pos][cur_action] + 1.0)

			# Update the times count for this state-action pair.
			times[cur_pos][cur_action] += 1

			# If at a terminal state, then restart a new game.
			if game[cur_pos] == GOAL or game[cur_pos] == PIT:
				prev_pos = -1
				prev_action = -1
				cur_pos = START

				reward_cnt = (reward_cnt + 1) % OUT[1]
				if reward_cnt == 0:
					reward_list.append(reward_total/OUT[1])
					reward_total = 0
				break
			else:
				# Go to next state.
				prev_pos = cur_pos
				prev_action = cur_action
				cur_pos = apply_move(cur_pos, cur_action)

	# Output the q-values after training.
	print
	print 'Q-Value Table:'
	pp.pprint(qval)
	print
	printboard(game, START)
	print
	printboard_dirs(game, qval)
	print
	if OUT[0] == 1:
		for i in range(len(reward_list)):
			print i*OUT[1], reward_list[i]
		pp.pprint(reward_list)

if __name__ == '__main__':
	main()


