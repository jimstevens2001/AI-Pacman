###############################################################################
#
# level_parser.py
#
###############################################################################



#------------------------------------------------------------------------------
#
# Level class
#
# This class parses a level file and contains all of the information for the
# level.
#
#------------------------------------------------------------------------------

class Level:

#------------------------------------------------------------------------------
# __init__
#------------------------------------------------------------------------------

	def __init__(self, filename=None):

		if filename:
			self.parse_file(filename)

#------------------------------------------------------------------------------
# parse_file()
#------------------------------------------------------------------------------

	def parse_file(self, filename):
		"Parses the given level file"

		self.filename = filename

		# Open the file, read it line by line, and strip the lines
		inFile = open(filename, 'r')
		lines = inFile.readlines()
		inFile.close()
		lines = [i.strip() for i in lines]

		# Extract all the level information
		self.num_pellets = int(lines[0].split(' ', 1)[1])
		self.pacman_home = eval(lines[1].split(' ', 1)[1])
		self.ghost_home = eval(lines[2].split(' ', 1)[1])
		self.level_dim = eval(lines[3].split(' ', 1)[1])
		self.color_edge = eval(lines[4].split(' ', 1)[1])
		self.color_fill = eval(lines[5].split(' ', 1)[1])
		self.color_shadow = eval(lines[6].split(' ', 1)[1])
		self.color_pellet = eval(lines[7].split(' ', 1)[1])
		self.level_layout = [i.split() for i in lines[8:]]

