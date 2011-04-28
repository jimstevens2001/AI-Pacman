import nn

print ""

infile = open( 'boeing60to60.dat', 'r' )
boeing_lines = infile.readlines()
infile.close

infile = open( 'airbus60to60.dat', 'r' )
airbus_lines = infile.readlines()
infile.close

boeing = []
airbus = []

# create the input data
for i in range( 25 ):
	boeing.append( [] )
	airbus.append( [] )

	for j in range( 256 ):
		boeing[i].append( float( boeing_lines[0] ) )
		boeing_lines.pop(0)

		airbus[i].append( float( airbus_lines[0] ) )
		airbus_lines.pop(0)

# need to scale the data between -1 and 1
for i in range( 25 ):
	max_boeing = max( [abs(k) for k in boeing[i]] )
	max_airbus = max( [abs(k) for k in airbus[i]] )

	for j in range( 256 ):
		boeing[i][j] /= max_boeing
		airbus[i][j] /= max_airbus

# make the training data
training_data = []
output_data = []

for i in range( 13 ):
	training_data.append( boeing[i*2] )
	output_data.append( 1 )

for i in range( 13 ):
	training_data.append( airbus[i*2] )
	output_data.append( 0 )

# train the NN
INUM = 256
HNUM = 5
ONUM = 1
LEARNING_RATE = 0.1
MSE = 10 ** -4
#MSE = 0.33

# initialize the NN
net = nn.NN( INUM, HNUM, ONUM )

# train the NN
avg_error = 1
epochs = 0
ITERATIONS = 1000
PRINT_INTERVAL = 100

#while( avg_error > MSE or avg_error == 0):
while( avg_error >= MSE ):
	avg_error = 0
	for i in range( len(training_data) ):
		error = net.train( (training_data[i], [output_data[i]]), LEARNING_RATE )
		avg_error += error
	avg_error /= len(training_data)
	
	if( epochs % PRINT_INTERVAL == 0 ):
		e = "Epochs: " + str( epochs )
		m = "Goal MSE: " + str( MSE )
		c = "Current MSE: " + str( avg_error )

		print e + "    " + m + "    " + c

	epochs += 1

print "\nEpochs: " + str( epochs ) + " MSE: " + str( avg_error )

# sim the NN
test_data = []
desired_output = []

for i in range( 12 ):
	test_data.append( boeing[i*2+1] )
	desired_output.append(1)

for i in range( 12 ):
	test_data.append( airbus[i*2+1] )
	desired_output.append(0)

print "\nDesired Result [Actual Result]:"
output = []
for i in range( len(test_data) ):
	cur_output = net.feed_forward( test_data[i] )
	output.append( cur_output )
	print str( desired_output[i] ) + " " + str( cur_output )

