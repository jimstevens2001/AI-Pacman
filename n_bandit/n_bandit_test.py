#                          _________________________
# ________________________/ N-Armed Bandit Problems \____________________
#
# This program is meant to test different policies and/or value functions
# within the context of reinforcement learning.  It generates a number m of
# simple n-armed bandit tasks where m and n are configurable.  Each action
# out of every possible state is given a random reward taken from a configurable
# gaussian distribution.  Next, it runs through a simulation whose length
# is adjustable and applies a given policy.  Right now, only the value function
# is static: is simply takes the average of the rewards and has no foresight
# whatsoever.  After each play, or 'game', the average reward accrued is written
# to a file, with one reward per line.  Post-processing can be done by MATLAB
# to graph the rewards.
#
# MATLAB instructions:
# 1. Open the file
#         fid = fopen('<path to file>/rewards.txt', 'r');
# 2. Vector read the file in
#         y = fscanf(fid, '%g');
# 3. Close the file
#         fclose(fid);
# 4. Plot the rewards
#         plot(y);
#

import sys, os, math, random

# Number of simulation runs
PLAYS = 5000

# Number of n-armed bandit problems, i.e., the state space
STATES = 2000

# Branching factor
ARMS = 4

# Mean of the gaussian distribution
MU = 0

# Variance of the guassian distribution
SIGMA = 1

# In case there are any problems
DEBUG_LEVEL = 0


# This function takes any x and calculates its value in the normal distribution
def gaussian_distribution(x):
	value = (1 / (SIGMA * math.sqrt(2 * math.pi))) * math.exp(-((x - MU)**2) / (2*SIGMA**2))
	return value


# This function returns a list from begin to end with increments of size step
def return_range_list(begin, end, step):
	lis = []
	i = begin
	while i < end:
		lis.append(i)
		i += step
	return lis


# For debuggin purposees
def debug(message):
	if DEBUG_LEVEL > 0:
		print message


# This is epsilon for the policy.  It can be static or a PDF
def get_threshold(iterations):
	return math.exp(-iterations/600.0)
	#return 0.1


# This is the whole state space
distribution = []

# This is the value function
values = []

# This is used to figure out how many times we've visited any state
times = []

# This is used to create a sequence in the states
next = []


# This generates a gaussian distribution
# for i in return_range_list(-5, 5, 0.05):
	# f.write(str(gaussian_distribution(i)) + '\n')
	# distribution.append(gaussian_distribution(i))


# This loop generates all the states, assigns a reward to each one and creates a sequence between them
for i in range(STATES):
	distribution.append([])
	times.append([])
	values.append([])
	next.append([])
	for j in range(ARMS):
		x = random.uniform(-5*SIGMA, 5*SIGMA)
		follow = random.randint(0, STATES - 1)
		distribution[i].append(gaussian_distribution(x))
		times[i].append(0)
		values[i].append(0)
		next[i].append(follow)

debug("Distribution\n" + str(distribution))
debug("Times\n" + str(times))
debug("Next\n" + str(next))


f = open('rewards.txt', 'w')
index = -1
previous_state = -1
next_state = 0


# This iterates over the state space explorations.  At the end of each iteration, it stores the average reward in the
# file.
for k in range(PLAYS):
	average_reward = 0

	# This loop goes through the state space and keeps track of rewards
	for i in range(STATES):

		# First, let us decide if we are exploring or exploiting
		epsilon = random.random()
		#debug("Epsilon is " + str(epsilon))

		# We are exploring
		if epsilon < get_threshold(k):
			j = random.randint(0, ARMS - 1)
			reward = distribution[next_state][j]

		# We are exploiting
		else:
			value = max(values[next_state])
			reward = distribution[next_state][values[next_state].index(value)]

		#debug("Index is " + str(index))
		#debug("Reward is " + str(reward))

		# Here we want to update the value in the previous state we visited by adding an adjusted amount to its value
		# based on the reward we got in the current state
		if previous_state != -1:
			last_value = values[previous_state][index]
			#debug("The last state was seen " + str(times[previous_state][index]) + " time(s)")
			#debug("The subtration gives you " + str(reward - last_reward))
			#debug("We are adding this much to the last reward: " + str((reward - last_reward) / (times[previous_state][index] + 1)))
			values[previous_state][index] += ((reward - last_value) / (times[previous_state][index] + 1))
			#debug("Last reward was " + str(last_reward) + " and new reward is " + str(distribution[previous_state][index]))

		# Update our average reward for this run
		average_reward += ((reward - average_reward)/(i + 1))
		#debug("Average reward is " + str(average_reward))

		# Keep track of the state we just visited, we'll need it in the next iteration
		index = distribution[next_state].index(reward)

		# Update the visitation count for the current state
		times[next_state][index] += 1

		# Move on to the next state
		previous_state = next_state
		next_state = next[next_state][index]

	# Write the average reward to the file
	f.write(str(average_reward) + '\n')

# Close the file
f.close()