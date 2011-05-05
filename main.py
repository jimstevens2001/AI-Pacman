###############################################################################
#
# main.py
#
###############################################################################

###############################################################################
#
# EECS 749 : Final Project - Learning Pac-Man
# Path     : /users/032/j/jstevens/Fall_07/749/pacman
# Date     : 11/26/2007
# Authors  : Fabrice Baijot, Adam Smith, Jim Stevens
# Version  : 3.1
# Language : Python, version 2.5 and PyGame, version 1.7
# System   : cycle3.eecs.ku.edu
# Site     : Dept. of Electrical Engineering and Computer Science
#            The University of Kansas, Lawrence, KS 66045
#
# Description:
#
# The project implements a game of Pac-Man where the player can be human or AI. 
# The AI uses reinforcement learning to acquire experience as it plays the game
# and gets better with time. There are two methods of reinforcement learning 
# used in this system: explicit state table representation and function
# approximation. The system is very modular and can easily be expanded to 
# include different types of ghosts, more learning algorithms for Pac-Man, and
# a variety of other parameters. For more information, please consult the 
# README file that accompanies this system.
# 
# Usage:
#
# This system uses PyGame for graphics.  It was implemented using PyGame v1.7.
# The system can also use Psyco for accelerated performance, but this is not a 
# requirement.
#
# The system expects the name of the configuration file to be passed in as a 
# command line parameter.  Without a config file, the game will not run.  The 
# convention for using the system is
#
#     > python main <config file name>
#
# Please see the README for more information.
#
###############################################################################



# Try to import psyco to improve execution time. The psyco version that is
# included with the code only works on Linux with Python v2.5. This is the
# version of Python that is currently installed on the EECS machines.
try:
	import psyco
	# Try to keep memory usage below 64 MB
	#psyco.profile( memorymax=65536 )
	psyco.full()
except:
	print 'Psyco not found. Continuing without Psyco...'


import game_engine, game_state, ai_pacman_approx, ai_pacman_qval, ai_pacman_nn, simple_ghost, sys
from common import *


if __name__ == "__main__":

	# Attempt to set the name of the config file. This will only fail if the
	# name of the config file was not passed in on the command line.
	try:
		config_file = 'config/'+sys.argv[1]+'.txt'
	except:
		print 'Usage: %s <config_file>'%(sys.argv[0])
		sys.exit(1)

	# Create a state object
	state = game_state.State()

	# Create the Game Engine object.  It takes a reference to the drawing 
	# object, the state, and the name of the config file
	game = game_engine.Game(None, state, config_file)


	# If graphics are enabled, then we need to import pygame and initialize all
	# of the necessary compontents to get graphics.
	if game.manager.config_options['graphics_on']:

		# Import the PyGame stuff
		import pygame, draw, human_pacman
		from pygame.locals import *
	
		# Create a clock object
		clock = pygame.time.Clock()

		# Initialize PyGame and the game window
		pygame.init()
		pygame.display.set_caption("Learning Pac-Man")
		window = pygame.display.set_mode((1, 1))

		# Extract the screen from the display
		screen = pygame.display.get_surface()

		# Create the drawing object, it takes a reference to the screen and the state
		drawer = draw.Drawer(screen, state)

		# Give the game engine a reference to the drawing object
		game.set_drawing_object(drawer)

		# Just for fun, display a window and tray icon
		pygame.display.set_icon(pygame.transform.scale(pygame.image.load("images/pacman-r3.gif").convert(), (32, 32)))

	elif not game.manager.config_options['ai_mode']:
		raise PacmanError("Cannot run game with graphics OFF if not in training mode")

	# Load the first level
	game.updater.reset_game()

	# Create a pacman object depending on the training mode
	if game.manager.config_options['ai_mode']:
		iterations = game.manager.config_options['training_iterations']
		if game.manager.config_options['learning_algorithm'] == 'approximation':
			pacman = ai_pacman_approx.Pacman(state, game)
		elif game.manager.config_options['learning_algorithm'] == 'explicit':
			pacman = ai_pacman_qval.Pacman(state, game)
		elif game.manager.config_options['learning_algorithm'] == 'neuralnet':
			pacman = ai_pacman_nn.Pacman(state, game)
	else:
		pacman = human_pacman.Pacman(game)

	# Create the ghosts
	ghost = {}
	for i in range(GHOSTS):
		ghost[i] = simple_ghost.Ghost(i, state, game)

	keep_going = True

	# The game loop
	while keep_going:

		# If we are using graphics, then allow a couple of helpful commands: pause and quit
		if game.manager.config_options['graphics_on']:
			pygame.event.pump()

			# Pause the game if the 'p' key is pressed
			if pygame.key.get_pressed()[pygame.K_p]:
				pygame.time.wait(400)
				unpause = False
				while not unpause:
					pygame.event.pump()
					# Unpause the game if 'p' is pressed again
					if pygame.key.get_pressed()[pygame.K_p]:
						pygame.time.wait(100)
						unpause = True
					# Exit if the 'Esc' key is pressed
					if pygame.key.get_pressed()[pygame.K_ESCAPE]:
						sys.exit(0)
					# Exit if we get a QUIT event (such as pressing the X button in the window)
					for event in pygame.event.get():
						if event.type == pygame.QUIT:
							sys.exit(0)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit(0)

		# Get the next move from Pac-Man
		pacman.get_next_move()

		# Get the next move from each ghost
		for i in range(GHOSTS):
			ghost[i].get_next_move()

		# Apply the chosen moves
		game.update_agents()

		# Do some management stuff
		if game.manager.config_options['ai_mode']:

			# Decrement the number of iterations
			iterations -= 1

			# Print a progress message for every 100000 iterations
			#if iterations % 100000 == 0:
			if iterations % 10000 == 0:
			#if iterations % 1000 == 0:
				print 'iterations left: ' + str(iterations/1000) + " K"

			# The training session has reached the desired number of iterations
			# and needs to exit.
			if iterations == 0:

				# Pacman should save his training data before we quit
				pacman.save_training_data()

				# If the graphics are enabled, print a simple message so the user knows why the window suddenly disappeared.
				# If graphics are not enabled, simply print a final message.
				if game.manager.config_options['graphics_on']:
					drawer.print_message('END OF SIMULATION', 3000)
				else:
					print "END OF SIMULATION"
				keep_going = False

		# Update the display
		if game.manager.config_options['graphics_on']:
			drawer.draw()
			# This will limit the number of frames per second to 60
			clock.tick(60)

