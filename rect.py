###############################################################################
#
# rect.py
#
###############################################################################

#------------------------------------------------------------------------------
#
# Rect class
#
# This class provides a light-weight spatial representation
# object.  Each object has a position and dimensions.
#
#------------------------------------------------------------------------------

class Rect:

#------------------------------------------------------------------------------
# __init__()
#------------------------------------------------------------------------------

	def __init__(self, top_left_position, (size_x, size_y)):

		# The position will be set to the upper left-hand corner of the rectange
		self.topleft = top_left_position

		# The dimensions
		self.size_x = size_x
		self.size_y = size_y

#------------------------------------------------------------------------------
# colliderect()
#------------------------------------------------------------------------------

	def colliderect(self, rect):
		"This function checks whether there is a collisions between two rects"

		# Check the distance between the two rects
		distance_x = abs(rect.topleft[0] - self.topleft[0])
		distance_y = abs(rect.topleft[1] - self.topleft[1])

		# If both distances are less than the size in that dimension (-4 to make collisions more apparent), then we have
		# a collision.  Otherwise we don't.
		if distance_x < self.size_x - 4 and distance_y <= self.size_y - 4:
			return True
		elif distance_x <= self.size_x - 4 and distance_y < self.size_y - 4:
			return True
		else:
			return False