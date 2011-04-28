###############################################################################
#                                                                             #
# ghost.py                                                                    #
#                                                                             #
###############################################################################

import random
from common import *

RANDOM = 0
MAN = 1
SMART_MAN = 2
PATH_FINDER = 3

DEPTH = 9

tile_size = 16
DOWN_DIR = (0,tile_size)
UP_DIR = (0,-tile_size)
LEFT_DIR = (-tile_size,0)
RIGHT_DIR = (tile_size,0)
dir = (UP_DIR, DOWN_DIR, LEFT_DIR, RIGHT_DIR)

MOVE_TYPE = PATH_FINDER
#MOVE_TYPE = SMART_MAN

###############################################################################
#
# class Ghost
#
###############################################################################

class Ghost:

	# constructor
	#	 self - have to have
	#	 state - reference to the game state
	#	 game_engine - reference to the game engine 
	def __init__( self, my_id, state, game_engine ):

		# initialize my ghost id
		self.my_id = my_id

		# initialize reference to the game state
		self.state = state

		# going to have a reference to the game engine
		# # can only call set_ghost_direction( ghost_id )
		self.game_engine = game_engine

		# get the position of the ghost pen
		self.ghost_pen = self.state.level.ghost_home[PINKY]

		# Set the threshold for a sub optimal move.
		# This will prevent all of the ghosts from all following Pac-Man in single
		# file.
		self.threshold = 0.25

		# TODO: this should probably be cleaned up
		# initialize the number of ghost moves for all ghosts
		#num_first_ghost_moves = [0,2,1,2]
		num_first_ghost_moves = [0,0,0,0]
		self.num_first_moves = num_first_ghost_moves[self.my_id]

		# TODO: this should probably be cleaned up
		# initialize the ghosts first moves
		first_ghost_moves = [[] for g in range(4)]
		first_ghost_moves[BLINKY] = []
		first_ghost_moves[PINKY]  = [RIGHT,UP]
		#first_ghost_moves[PINKY]  = [LEFT,UP]
		first_ghost_moves[INKY]   = [UP]
		first_ghost_moves[CLYDE]  = [LEFT,UP]
		#first_ghost_moves[CLYDE]  = [RIGHT,UP]
		self.first_moves = first_ghost_moves[self.my_id]

		# TODO: this should probably be cleaned up
		# initialize the number of moves that the ghost has made
		num_moves_all_ghosts = [0,0,0,0]
		self.num_moves = num_moves_all_ghosts[self.my_id]

		# Set the goal position for the path_finder
		self.goal = (0,0)


#------------------------------------------------------------------------------
#
# get_next_move()
#
#------------------------------------------------------------------------------

# The current ghost heuristic is to chase packman, reducing the Manhattan
# distance between himself and Pac-Man. However, sometimes, based on a random
# value compared to the threshold level, the ghost will choose to move in a
# suboptimal manner. This will prevent all of the ghosts from chasing Pac-Man
# in single file, allowing them to occasionaly surround him.

	def get_next_move( self ):
		"Returns the ghost's chosen next direction. This is based off of the \
		 current state as well as the ghost's rules for picking the next move."

		#print (self.my_id) + ": get_next_move"

		# Check to see if the ghost turned. If so, then the ghost has made a move
		# and the move counter needs to be incremented. 
		if( self.made_move() ):
			#print "Ghost " + str(ghost_id) + " made a valid move"
			self.num_moves += 1;
			#self.ghost_direction[ghost_id] = self.chosen_ghost_direction[ghost_id]


		# Check to see if the ghost has performed the desired first moves. If not
		# then the next move needs to be the next first move.
		#print "num_moves[" + str(ghost_id) + "] is " + str(self.num_moves[ghost_id])
		if( self.num_moves < self.num_first_moves ):
			#print "Ghost " + str(ghost_id) + " is making an initial move."
			dir = self.first_moves[self.num_moves]
			#print "Moving " + dir
			self.game_engine.set_ghost_direction( self.my_id, dir )
			return

		
		if( self.state.ghost_mode[ self.my_id ] == EYES ):
			dir = self.path_finder( self.ghost_pen )
		else:
			# get the direction to pac-man
			if( MOVE_TYPE == PATH_FINDER ):
				dir = self.path_finder( self.state.pacman_rect )
			elif( MOVE_TYPE == SMART_MAN ):
				dir = self.get_smart_man_dir()
			elif( MOVE_TYPE == MAN ):
				dir = self.get_dir_to_pacman()
			elif( MOVE_TYPE == RANDOM ):
				dir = self.get_random_dir()

		self.game_engine.set_ghost_direction( self.my_id, dir )

		return 



#------------------------------------------------------------------------------
#
# get_smart_man_dir()
#
#------------------------------------------------------------------------------

	def get_smart_man_dir( self ):
		"Returns the direction that the ghost should move. If the ghost is \
		 vulnerable, then it moves away from Pac-Man. Otherwise, it moves towards \
		 Pac-Man"
	
		dir = self.get_dir_to_pacman()
	
		if( self.state.ghost_mode[ self.my_id ] == VULNERABLE ):
			dir = -dir
	
		return dir



#------------------------------------------------------------------------------
#
# get_dir_to_pacman()
#
#------------------------------------------------------------------------------

	def get_dir_to_pacman( self ):
		"Finds the move that minimizes the manhatan distance between the ghost \
		 designate by ghost_id and pac-man"
	
		dir = ''
	
		pac_pos = self.state.pacman_rect.topleft
		my_pos = self.state.ghost_rect[self.my_id].topleft
	
		x_dif = my_pos[0] - pac_pos[0]
		y_dif = my_pos[1] - pac_pos[1]
	
	
		seed = random.randint(0,3)
	
		if( seed > self.threshold ):
			if( abs(x_dif) > abs(y_dif) ):
				if( x_dif < 0 ):
					dir = RIGHT
				else:
					dir = LEFT
			else:
				if( y_dif < 0 ):
					dir = DOWN
				else:
					dir = UP
		else:
			if( abs(x_dif) < abs(y_dif) ):
				if( x_dif < 0 ):
					dir = RIGHT
				else:
					dir = LEFT
			else:
				if( y_dif < 0 ):
					dir = DOWN
				else:
					dir = UP
	
		return dir



#------------------------------------------------------------------------------
#
# made_move()
#
#------------------------------------------------------------------------------

	def made_move( self ):
		"Checks to see if the current direction is different than the previous \
		 direction. This would be false if the ghost chose to move in a direction \
		 that was invalid, such as moving into a wall."

		curr_dir = self.state.current_ghost_direction[ self.my_id ]
		next_dir = self.state.next_ghost_direction[ self.my_id ]

		return ( curr_dir == next_dir )



#------------------------------------------------------------------------------
#
# get_random_dir()
#
#------------------------------------------------------------------------------

	def get_random_dir( self ):
		"This is the heuristic for a rancom move. The extra conditions in the if \
		 statements prevend the ghost from moving backwards. If they are allowed \
		 to move backwards, then they look like they are having a spasm."
	
		seed = random.randint(0,3)
	
		curr_dir = self.state.current_ghost_direction[ self.my_id ]
	
		if   (seed == 0) and (curr_dir != LEFT):
			dir = RIGHT
		elif (seed == 1) and (curr_dir != RIGHT):
			dir = LEFT
		elif (seed == 2) and (curr_dir != DOWN):
			dir = UP
		elif (seed == 3) and (curr_dir != UP):
			dir = DOWN
		else:
			#print "Ghost tried to move backwards"
			dir = curr_dir
	
		return dir



#------------------------------------------------------------------------------
#
# path_finder()
#
#------------------------------------------------------------------------------

	def path_finder( self, goal ):
		"This function is called when the ghost has been eaten by Pac-Man and needs \
		 to find its way back to the ghost pen to regenerate. It returns the next \
		 move the ghost needs to make to find its way back to the ghost pen. \
		"

		start = self.state.ghost_rect[self.my_id].topleft
	
		start = (start[0]/tile_size*tile_size, start[1]/tile_size*tile_size)
		goal  = (goal[0]/tile_size*tile_size, goal[1]/tile_size*tile_size)

		path = self.astar( start, goal )

		# TODO: This will cause out of range problems
		# Fix it!

		if( len(path) == 1 ):
			loc = path[0]
		elif( len(path) > 1 ):
			loc = path[1]
		else:
			PacmanError( "Length of path is 0" )

		move = (loc[0]-start[0], loc[1]-start[1])

		# TODO: gave "KeyError: (0,0)"
		dirname = {UP_DIR: UP, DOWN_DIR: DOWN, LEFT_DIR: LEFT, RIGHT_DIR: RIGHT}

		dir = dirname[move]

		return dir


	def astar( self, start, goal ):
		self.goal = goal

		closed = []
		deep = []
		q = [[start]]

		while q != []:
			p = q.pop(0)
			x = p[-1]

			# TODO: need to check depth
			if( x in closed ):
				continue
			if( x == goal ):
				return p
			if (len(p) == DEPTH):
				deep.append(p)
				continue

			closed.append(x)

			#print closed

			for y in self.successors(x):
				self.enqueue( q, p, y )

		min_f = -1
		min_i = -1
		for i in deep:
			if min_f == -1 or (self.f(i) < min_f):
				min_f = self.f(i)
				min_i = i
		return min_i


	def apply_move( self, pos, move ):
		return( pos[0] + move[0], pos[1] + move[1] )



	# TODO: need to take into account going through portal
	def successors( self, pos ):
		retval = []

		local_dir = list(dir)

		while local_dir != []:
			next = local_dir.pop(random.randint(0, len(local_dir)-1))
			newpos = self.apply_move( pos, next )

			# TODO: check for successors
			if self.isvalid(newpos):
				retval.append(newpos)

		return retval

	def isvalid(self, pos):
		if self.game_engine.checker.out_of_bounds(pos):
			return False
		elif self.game_engine.checker.is_wall(pos):
			return False
		else:
			return True


	def enqueue( self, q, p , y ):
		q.append( p + [y] )
		q.sort( self.path_cmp )

	def path_cmp( self, x, y ):
		if( self.f(x) > self.f(y) ):
			return 1
		elif( self.f(x) == self.f(y)):
			return 0
		else:
			return -1

	# TODO: made this greedy
	def f( self, p ):
		return len(p) + self.h( p[-1] )
		#return self.h( p[-1] )

	def h( self, s ):
		return( abs( self.goal[0] - s[0] ) + abs( self.goal[1] - s[1] ) )


