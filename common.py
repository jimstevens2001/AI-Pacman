###############################################################################
#
# common.py
#
# This file contains a set of constants that are used throughout the system
#
###############################################################################

# These are used for directions and edge identification
UP				= -1
DOWN			= 1
LEFT			= -2
RIGHT			= 2

# This mapping is used for debugging purposes
MOVE_LOOKUP = { UP: 'UP', DOWN: 'DOWN', LEFT: 'LEFT', RIGHT: 'RIGHT' }

# The number of ghosts
GHOSTS			= 4

# The ghosts names and IDs
BLINKY			= 0
PINKY			= 1
INKY			= 2
CLYDE			= 3
BLUE			= 4
WHITE			= 5

# The number of ghost modes
GHOST_MODES		= 3

# The various ghost modes
NORMAL			= 0
VULNERABLE		= 1
EYES			= 2

# These are used by the state updater to know what to do after updating the state
CONTINUE		= 0
NEXT_LEVEL		= 1
RESET_AGENTS	= 2
RESET_GAME		= 3


# This is a custom exception class
class PacmanError(Exception):
	pass
