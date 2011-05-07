###############################################################################
#
# evolve.py
#
###############################################################################

###############################################################################
#
# EECS 749 : Final Project - Learning Pac-Man
# Date     : 05/04/2011
# Authors  : Fabrice Baijot, Adam Smith, Jim Stevens, Hsueh-Chien Cheng
# Version  : 3.1415
# Language : Python, version 2.6 and PyGame, version 1.7
# System   : tortilla.ece.umd.edu
# Site     : Dept. of Computer Science
#            The University of Maryland-College Park, College Park, MD
#
# Description:
#
# 
# Usage:
#
# python evolve.py
#
# Please see the README for more information.
#
###############################################################################

import subprocess
import random
import sys
import time

import ecspy
from ecspy import ec
from ecspy import terminators
from ecspy import observers

# Constants
population_size = 15
rounds = 50
#training_iterations = 1000000
#results_games = 15

training_iterations = 1000000
results_games = 15

# Bounds for parameters
HIDDEN_LOW = 1
HIDDEN_HIGH = 25
LOWER_BOUNDS = [0,HIDDEN_LOW,0]
UPPER_BOUNDS = [1,HIDDEN_HIGH,1]

bounds = ecspy.ec.Bounder(LOWER_BOUNDS, UPPER_BOUNDS)


# Open devnull to redirect subprocess stdout.
devnull = open('/dev/null', 'w')

# Starting dictionary for NN learning.
learning_start = 'learning/nn_default.txt'
config_training = 'config/awesome_nn_train.txt'
config_results = 'config/awesome_nn.txt'

round_number = 0


def read_dict(filename):
	try:
		inFile = open(filename, 'r')
		dictionary = eval(inFile.read())
		inFile.close()
		return dictionary
	except:
		print 'Failed to read file:',filename
		sys.exit(1)

def write_dict(dictionary, filename):
	try:
		outFile = open(filename, 'w')
		outFile.write(str(dictionary))
		outFile.close()
	except:
		print 'Failed to write file:',filename
		sys.exit(1)

def training_file(num):
	return 'tmp/training_'+str(num)+'.txt'
def config_file(num):
	return 'tmp/config_'+str(num)+'.txt'
def score_file(num):
	return 'scores/'+str(num)+'.txt'

def generator(random, args):
	# [gamma, num_hidden, max_epsilon]
	return [random.random(), random.uniform(HIDDEN_LOW, HIDDEN_HIGH), random.random()]

def evaluator(candidates, args):
	global round_number
	round_number += 1

	# Train the candidate solutions.
	print 'Round',round_number,'training'
	sp_list = []
	for i in range(len(candidates)):
		# Get parameters
		cur_gamma = candidates[i][0]
		cur_hidden = int(round(candidates[i][1]))
		cur_ep_max = candidates[i][2]

		# Apply any additional constraints.
		if cur_hidden < HIDDEN_LOW:
			cur_hidden = HIDDEN_LOW
		if cur_hidden > HIDDEN_LOW:
			cur_hidden = HIDDEN_HIGH

		# generate learning dictionary, write it to tmp file
		learn_dict = read_dict(learning_start)
		learn_dict['gamma'] = cur_gamma
		learn_dict['neuralnets']['nc_list'][1] = cur_hidden
		learn_dict['epsilon_params']['max_value'] = cur_ep_max
		write_dict(learn_dict, training_file(i))

		# generate config dictionary (with training mode), write to file
		config_dict = read_dict(config_training)
		config_dict['training_file_start'] = training_file(i)
		config_dict['training_file_end'] = training_file(i)
		config_dict['training_iterations'] = training_iterations
		write_dict(config_dict, config_file(i))

		# run training mode
		#p = subprocess.Popen(['python', 'main.py', '../tmp/config_'+str(i)])
		p = subprocess.Popen(['python', 'main.py', '../tmp/config_'+str(i)], stdout=devnull)
		sp_list.append(p)

	# wait until everyone is done training
	for i in range(len(candidates)):
		p = sp_list[i]
		p.wait()

	# Run the results collection mode to see how it does.
	print 'Round',round_number,'results'
	sp_list = []
	for i in range(len(candidates)):

		# generate config dictionary for results mode, write to file
		config_dict = read_dict(config_results)
		config_dict['training_file_start'] = training_file(i)
		config_dict['score_file'] = score_file(i)
		config_dict['results_games'] = results_games
		write_dict(config_dict, config_file(i))

		# run results mode
		#p = subprocess.Popen(['python', 'main.py', '../tmp/config_'+str(i)])
		p = subprocess.Popen(['python', 'main.py', '../tmp/config_'+str(i)], stdout=devnull)
		sp_list.append(p)

	# wait until everyone is done running results
	for i in range(len(candidates)):
		p = sp_list[i]
		p.wait()

	# Collect the results and put them in the fitness vector.
	fitness = []
	for i in range(len(candidates)):
		# read score in and place in fitness vector
		score_dict = read_dict(score_file(i))
		fitness.append(score_dict['score'])

	return fitness


#p = subprocess.Popen(['python', 'main.py', 'awesome_nn'], stdout=devnull)
#p2 = subprocess.Popen(['python', 'main.py', 'awesome_nn'], stdout=devnull)
#p.wait()
#p2.wait()

rand = random.Random()
rand.seed(int(time.time()))
ga = ec.GA(rand)
#ga.observer = observers.screen_observer
ga.terminator = terminators.evaluation_termination
ga.variator = ecspy.variators.gaussian_mutation
ga.observer = observers.file_observer
statsFile = open('tmp/stats.csv', 'w')
indivFile = open('tmp/indiv.csv', 'w')
final_pop = ga.evolve(evaluator=evaluator,
                      generator=generator,
                      #bounder=bounds,
                      max_evaluations=population_size * rounds,
                      num_elites=1,
                      pop_size=population_size,
                      num_bits=10,
                      statistics_file=statsFile,
                      individuals_file=indivFile)

outputFile = open('result_'+str(training_iterations)+'.txt', 'w')
for ind in final_pop:
	print(str(ind))
	outputFile.write(str(ind)+'\n')
outputFile.close()
