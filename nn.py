###############################################################################
#
# nn.py
#
###############################################################################

# TODO: This needs commenting

import random, math 

SIGMOID_EXTREME = 30
WEIGHT_SCALE = 1000.0

#------------------------------------------------------------------------------
#
# NN class
#
# This class contains all of the functions that are essential to our neural
# network. It is our NN toolbox.
#
#------------------------------------------------------------------------------

class NN:

	def __init__(self, nc_list, af_list):
		# The neuron count list holds the number of neurons in each layer of the
		# network. The first entry is the number of inputs to the network and
		# therefore does not correspond to actual neurons.
		self.neuron_count = nc_list

		# The activation function list tells what type of activation function to
		# use for each layer of the network. This starts at the first hidden layer
		# so index i in af_list corresponds to index i+1 in neuron_count.
		self.af_list = af_list

		# The weights dictionary is used to hold all of the weights for the connections
		# in the network. Weights is a 3D dictionary. The outer index corresponds to the
		# layer in the network. The middle index corresponds to the neuron were the connection
		# ends. The inner index corresponds to the neuron index in the previous layer where
		# the connection starts.
		self.weights = {} 

		# Deltas holds all of the delta values that are computed during back propagation.
		self.deltas = {}

		# Outputs holds the output of a neuron AFTER it has been run through the activation function.
		self.outputs = {}

		# Nets holds the output of a neuron BEFORE it has been run through the activation function.
		# This is the result of the dot product of the inputs vector and the weights vector for
		# each neuron.
		self.nets = {}

		# Note: The deltas, outputs, and nets dictionaries do not have to be saved to the 
		# learning file for the network to be recovered later.

		# Note 2: Deltas, outputs, and nets are all 2D dictionaries. The outer index
		# corresponds to the layer and the inner index corresponds to a neuron.

		# Set up a dictionary to hold the different allowed activation functions.
		self.activation = {}
		self.activation['lin'] = self.linear
		self.activation['sig'] = self.sigmoid

		# Set up a dictionary to hold the functions that compute the derivative of the
		# activation functions.
		self.dactivation = {}
		self.dactivation['lin'] = self.dlinear
		self.dactivation['sig'] = self.dsigmoid

		# The remainder of this function initializes the network's state.


		# For each layer in the network.
		for i in range(self.num_layers()):
			if i != 0:
				# If the layer is not the input layer, then
				# initialize the weights, deltas, and nets dictionaries.
				self.weights[i] = {}
				self.deltas[i] = {}
				self.nets[i] = {}

			# All layers have an output value.
			self.outputs[i] = {}

			# For each neuron in the layer.
			for j in range(self.neuron_count[i]):

				# Initialize the output of the neuron.
				self.outputs[i][j] = 0.0

				if i != 0:
					# If the layer is not the input layer, then
					# initialize the weights and net value.
					self.nets[i][j] = 0.0
					self.deltas[i][j] = 0.0
					self.weights[i][j] = {'bias': self.weight_init()}
					for k in range(self.neuron_count[i-1]):
						self.weights[i][j][k]= self.weight_init()




	def num_layers(self):
		return len(self.neuron_count)

	def weight_init(self):
		return random.uniform(-1, 1) / WEIGHT_SCALE






	# TODO: This needs to take parameters to get whatever state it needs to
	# recover the network structure and the values of the weights.
	def reconstruct( self, weights ):
		""

		if( weights != None ):
			self.weights = weights



	# TODO: This does the opposite of reconstruct
	def get_state( self ):
		return self.weights



	def sigmoid(self, x):
		"Sigmoid activation function. This is scaled to go between -1 and 1."
		if x <= -SIGMOID_EXTREME:
			return -1
		elif x >= SIGMOID_EXTREME:
			return 1
		else:
			return 2 / (1 + math.exp(-x)) - 1

	def dsigmoid(self, x):
		"Derivative of sigmoid activation function."
		if x <= -SIGMOID_EXTREME:
			return 0
		elif x >= SIGMOID_EXTREME:
			return 0
		else:
			return 2 * math.exp(-x) / ((1 + math.exp(-x)) ** 2)


	def linear(self, x):
		"Linear activation function."
		return x

	def dlinear(self, x):
		"Derivative of linear activation function."
		return 1.0



	
	def feed_forward(self, input):
		"Compute the result of the network given the input vector"

		# For each layer in the network.
		for i in range(self.num_layers()):
			if i > 0:
				# If this is not the input layer, then get the activation
				# function for this layer.
				f = self.activation[self.af_list[i-1]]

			# For each neuron in the layer.
			for j in range(self.neuron_count[i]):
				if i == 0:
					# For the input layer, just assign the output to
					# the jth input.
					self.outputs[i][j] = input[j]
				else:
					# For an actual neuron, compute sum(w_kj*o_k)+bias.
					output = 0.0
					for k in range(self.neuron_count[i-1]):
						output += self.outputs[i-1][k] * self.weights[i][j][k]
					output += self.weights[i][j]['bias']

					# Assign the result of the dot product directly to the nets value.
					self.nets[i][j] = output

					# Run the nets value through the activation function to get the output.
					self.outputs[i][j] = f(output)

		
		# Return the ordered list of output values for the output layer.
		output_index = self.num_layers() - 1
		output_list = [self.outputs[output_index][j] for j in range(self.neuron_count[output_index])]
		return output_list

	
	# Trains the network with the training set. The training set is a list of pairs (i.e. [(a,b), (c,d)]).
	# The first item in each pair is a list that corresponds to the input vector. The second item in each
	# pair is a list that corresponds to the output vector. N is the learning rate.
	def train(self, train_set, N):

		# Initialize the weight adjustments dictionary.
		# This holds the adjustments for each item in the training set.
		weight_adjusts = {}
		for i in range(1,self.num_layers()):
			weight_adjusts[i] = {}
			for j in range(self.neuron_count[i]):
				weight_adjusts[i][j] = {}
				for k in range(self.neuron_count[i-1]):
					weight_adjusts[i][j][k] = []
				weight_adjusts[i][j]['bias'] = []

		error_list = []

		for (input, output) in train_set:
			cur_output = self.feed_forward(input)

			# Get a list of indices starting with the output layer
			# and down to the first hidden layer.
			neuron_layers = [i for i in range(1, self.num_layers())]
			neuron_layers.reverse()

			# Compute the delta value for each neuron.
			output_layer = True
			for i in neuron_layers:
				# Get the derivative of the activation function.
				df = self.dactivation[self.af_list[i-1]]

				for j in range(self.neuron_count[i]):
					# TODO: Find out exactly what the "error" variable is in the handout.
					if output_layer:
						# For an output node, the error is simply the difference
						# between the desired output and the current output.
						error = output[j] - cur_output[j]
					else:
						# For hidden layer nodes, the error is the sum of the deltas
						# from the neurons in the next layer times the weights that
						# connect the neurons to this neuron.
						error = 0.0
						for k in range(self.neuron_count[i+1]):
							error += self.deltas[i+1][k] * self.weights[i+1][k][j]

					# Compute the delta value for this neuron.
					# It is the derivative of the activation function evaluated at nets[i][j]
					# multiplied by the error.
					self.deltas[i][j] = df(self.nets[i][j]) * error

				# After the first iteration, we are no longer in the output layer.
				output_layer = False

			# Update the weights in each neuron.
			for i in neuron_layers:
				for j in range(self.neuron_count[i]):
					for k in range(self.neuron_count[i-1]):
						# Compute the weight change for the weight between neuron [i-1][k]
						# and neuron [i][j].
						change = N * self.deltas[i][j] * self.outputs[i-1][k]
						weight_adjusts[i][j][k].append(change)

					# Compute the weight change for this neuron's bias node.
					change = N * self.deltas[i][j]
					weight_adjusts[i][j]['bias'].append(change)

			# Compute the sum of the squared error.
			cur_error = 0.0
			for i in range(len(output)):
				try:
					cur_error += 0.5*(output[i] - cur_output[i])**2
				except OverflowError, e:
					print 'output[i]', output[i]
					print 'cur_output[i]', cur_output[i]
					print 'cur_error', cur_error
					raise e
			error_list.append(cur_error)


		# Adjust the weights by adding all of the adjustments for the training set at once.
		for i in range(1,self.num_layers()):
			for j in range(self.neuron_count[i]):
				for k in range(self.neuron_count[i-1]):
					self.weights[i][j][k] += sum(weight_adjusts[i][j][k])
				self.weights[i][j]['bias'] += sum(weight_adjusts[i][j]['bias'])

	
		# Return the mean error for the training set.
		mean_error = 0.0
		for i in error_list:
			mean_error += i
		mean_error /= len(error_list)
		return mean_error


