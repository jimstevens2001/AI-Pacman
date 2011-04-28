from common import *
import random

class PF:

#------------------------------------------------------------------------------
# __init__()
#------------------------------------------------------------------------------

	def __init__(self, game):
		self.game = game
		self.random = random.Random()

#------------------------------------------------------------------------------
# astar()
#------------------------------------------------------------------------------

	def astar(self, start, goal):
		"A* algorithm. Finds the optimal path from start to goal."

		unnormalized_goal = goal

		# The start position needs to be normalized to a tile. An agent may
		# be at any location in a tile, but we only care about which tile they
		# are currently in.
		tile_size = self.game.manager.config_options['tile_size'] 
		start_tile = self.game.checker.get_tile_coordinates(start)
		start = (start_tile[0] * tile_size, start_tile[1] * tile_size)
		goal_tile = self.game.checker.get_tile_coordinates(goal)
		goal = (goal_tile[0] * tile_size, goal_tile[1] * tile_size)

		self.goal = goal

		#start = ((start[0] / tile_size) * tile_size, (start[1] / tile_size) * tile_size)
		#goal  = (( goal[0] / tile_size) * tile_size, ( goal[1] / tile_size) * tile_size)

		# The list of explored states
		closed = []

		# The priority queue for states we still need to look at
		q = [[start]]

		# Look at each item in the priority queue and check to see if it is the
		# goal.
		while q != []:

			# Get the first item in our sorted queue
			p = q.pop(0)

			# This is the actual position
			x = p[-1] # the position that is closest to the goal

			if( x in closed ):
				# If x is in the closed list, then we have already checked it and
				# expanded it and we don't need to do it again.
				continue

			if( x == goal ):
				# If x is the goal, then we need to return the path from the
				# starting position to the goal
				return p

			# Since x was not the goal, we need to append it to the closed list
			# so that it doesn't get checked again.
			closed.append(x)

			# Enqueue all of the successors of x into the priority queue
			for y in self.successors(x):
				self.enqueue(q, p, y)

		# If the queue ever becomes empty and a path has not been returned,
		# then the algorithm could not find a valid path from the start
		# position to the goal.
		print "start: ", start
		print "goal:  ", goal
		print "unnormalized goal: ", unnormalized_goal
		raise PacmanError('A* failed to find a path')

#------------------------------------------------------------------------------
# apply_move()
#------------------------------------------------------------------------------

	def apply_move(self, pos, move):
		"Applies a move to a position, returning a new position."

		return (pos[0] + move[0], pos[1] + move[1])

#------------------------------------------------------------------------------
# successors()
#------------------------------------------------------------------------------

	def successors(self, pos):
		"Expands a position into all of its valid next positions."

		retval = []

		# Each step has to be a tile
		step = self.game.manager.config_options['tile_size']

		# Possible next positions are up, down, left and right of the current
		# position.
		local_dir = [(0,-step), (0,step), (-step,0), (step,0)]

		# Look at all of the possible next positions and add them to the return
		# list if they are valid moves.
		while local_dir != []:
			next = local_dir.pop(self.random.randint(0, len(local_dir)-1))
			newpos = self.apply_move( pos, next )

			# Only use the new position if it is a valid move.
			if self.isvalid(newpos):
				retval.append(newpos)

		return retval

#------------------------------------------------------------------------------
# isvalid()
#------------------------------------------------------------------------------

	def isvalid(self, pos):
		"Checks to see if the position is valid."

		# If a position is not a wall and it is not out of bounds, then it is
		# a valid next position.
		# TODO: This is a hack. We need to track down the A* error
		if self.game.checker.out_of_bounds(pos):
		#if self.game.checker.out_of_bounds2(pos):
			return False
		elif self.game.checker.is_wall(pos):
			return False
		else:
			return True

#------------------------------------------------------------------------------
# enqueue()
#------------------------------------------------------------------------------

	def enqueue(self, q, p , y):
		"Enqueues a path p with next position y into priority queue q."

		q.append(p + [y])
		q.sort(self.path_cmp)

#------------------------------------------------------------------------------
# path_cmp()
#------------------------------------------------------------------------------

	def path_cmp(self, x, y):
		"Compares the value of the f function of two paths. Used to sort a \
		 list of paths."

		if self.f(x) > self.f(y):
			return 1
		elif self.f(x) == self.f(y):
			return 0
		else:
			return -1

#------------------------------------------------------------------------------
# f()
#------------------------------------------------------------------------------

	def f(self, p):
		"Returns the value of the A* heuristic of the heuristic, h, plus the \
		 depth len(p)."

		return len(p) - 1 + self.h(p[-1])

#------------------------------------------------------------------------------
# h()
#------------------------------------------------------------------------------

	def h(self, s):
		"Returns the value of the heuristic function. This is the Manhattan \
		 distance."

		return abs(self.goal[0] - s[0]) + abs(self.goal[1] - s[1])
