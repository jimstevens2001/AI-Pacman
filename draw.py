###############################################################################
# 
# draw.py
#
###############################################################################

import pygame, os
from common import *

#------------------------------------------------------------------------------
#
# Drawer class
#
# This class is used to take care of all of the graphics when graphics are
# enabled.
#
#------------------------------------------------------------------------------

class Drawer:

#------------------------------------------------------------------------------
# __init__
#------------------------------------------------------------------------------

	def __init__(self, surface, state):

		# This will be our drawing canvas
		self.canvas = surface

		# Create a background surface
		self.background = pygame.Surface(self.canvas.get_size())

		# This is a reference to the games state
		self.state = state

		# This will contain all of the static images for a level
		self.tile_images = {}

		# Pacman image list
		self.pacman_images = []

		# ---------------------------------------------
		# Ghost attributes
		
		# Ghost image dictionaries
		self.all_ghost_images = {}
		self.current_ghost_image_set = {}
		self.current_ghost_image = {}
		
		# Ghost colors
		self.ghostcolor = {}
		self.ghostcolor[BLINKY] = (255, 0, 0, 255)		# Red, Blinky ghost
		self.ghostcolor[PINKY] = (255, 128, 255, 255)	# Pink, Pinky ghost
		self.ghostcolor[INKY] = (128, 255, 255, 255)	# Cyan, Inky ghost
		self.ghostcolor[CLYDE] = (255, 128, 0, 255)		# Orange, Clyde ghost
		self.ghostcolor[BLUE] = (50, 50, 255, 255)		# Blue, Vulnerable ghost
		self.ghostcolor[WHITE] = (255, 255, 255, 255)	# White, flashing ghost
		# ---------------------------------------------

#------------------------------------------------------------------------------
# change_tile_color()
#------------------------------------------------------------------------------

	def change_tile_color(self, tile, old_color, new_color):
		"Changes any pixel in the given tile from old_color to new_color"

		# Look at each pixel in the tile and if its color is the old one, change it to the new one
		for y in range(self.config_options['tile_size']):
			for x in range(self.config_options['tile_size']):
				if tile.get_at((x, y)) == old_color:
					tile.set_at((x, y), new_color)

#------------------------------------------------------------------------------
# build_image_path()
#------------------------------------------------------------------------------

	def build_image_path(self, image_name):
		"Makes an OS specific path to the given image name"

		return os.path.join(self.config_options['image_path'], image_name)

#------------------------------------------------------------------------------
# set_drawing_parameters()
#------------------------------------------------------------------------------

	def set_drawing_parameters(self, context_dictionary):
		"Sets up the drawing context"

		self.config_options = context_dictionary

		# Load tile images
		for tile in self.config_options['context_dictionary']:
			image_path = self.build_image_path(self.config_options['context_dictionary'][tile])
			self.tile_images[tile] = pygame.image.load(image_path).convert()

		# Load Pac-Man's animation images
		for image_name in self.config_options['active_pacman_images']:
			image_path = self.build_image_path(image_name)
			self.pacman_images.append(pygame.image.load(image_path).convert())

		# We need to know how many images there are
		self.pacman_image_count = len(self.config_options['active_pacman_images'])

		# Load Pac-Man's still image
		self.pacman_still_image = pygame.image.load(self.build_image_path(self.config_options['still_pacman_image'])).convert()

		# Load ghost images
		for i in range(6):
			self.all_ghost_images[i] = []
			for image_name in self.config_options['ghost_images']:
				# Construct the path to the image file
				image_path = self.build_image_path(image_name)

				# Load the image and add it to the list
				self.all_ghost_images[i].append(pygame.image.load(image_path).convert())

				# Change the tile color for each ghost
				if i != BLINKY:
					self.change_tile_color(self.all_ghost_images[i][self.config_options['ghost_images'].index(image_name)], (255, 0, 0, 255), self.ghostcolor[i])

		# We need to know how many images there are
		self.ghost_image_count = len(self.config_options['ghost_images'])

		# Set up three font objects for the score, level number,  and number of lives
		self.score_font = pygame.font.Font(None, 20)
		self.level_font = pygame.font.Font(None, 20)
		self.lives_font = pygame.font.Font(None, 20)

#------------------------------------------------------------------------------
# load_level()
#------------------------------------------------------------------------------

	def load_level(self):
		"Sets up level-specific drawing parameters"

		# Set frame delay
		self.delay = self.config_options['frame_delay']

		# Set power pellet blinking attributes
		self.blink_time = self.config_options['blink_time']
		self.on_off = 1

		# Set tile  colors
		for tile in self.tile_images:
			# Wall edge color
			self.change_tile_color(self.tile_images[tile], (255, 206, 255, 255), self.state.level.color_edge)
			# Wall fill color
			self.change_tile_color(self.tile_images[tile], (132, 0, 132, 255), self.state.level.color_fill)
			# Wall edge shadow color
			self.change_tile_color(self.tile_images[tile], (255, 0, 255, 255), self.state.level.color_shadow)
			# Pellet color
			self.change_tile_color(self.tile_images[tile], (128, 0, 128, 255), self.state.level.color_pellet)

		# Set default Pac-Man image
		self.pacman_image_index = 0
		self.current_pacman_image = self.pacman_still_image

		# Set default ghost images
		self.ghost_image_index = 0
		for i in range(GHOSTS):
			self.current_ghost_image_set[i] = self.all_ghost_images[i]
			self.current_ghost_image[i] = self.current_ghost_image_set[i][self.ghost_image_index]

		# Resize the window
		pygame.display.set_mode((self.state.level.level_dim[0] * self.config_options['tile_size'], self.state.level.level_dim[1] * self.config_options['tile_size'] + 30))
		
		# Create a background surface and make it black
		self.background = pygame.Surface(self.canvas.get_size())
		self.background = self.background.convert()
		self.background.fill((0,0,0))

#------------------------------------------------------------------------------
# extract_leve_eyt_rect()
#------------------------------------------------------------------------------

	def extract_left_eye_rect(self):
		"Extracts the left eye rect using the range given in the config file"

		eye_range = self.config_options['ghost_eye_range']
		return pygame.Rect(eye_range[0][0], eye_range[1][0], eye_range[0][1] - eye_range[0][0] + 1, eye_range[1][1] - eye_range[1][0] + 1)

#------------------------------------------------------------------------------
# extract_right_eye_rect()
#------------------------------------------------------------------------------

	def extract_right_eye_rect(self):
		"Extracts the right eye rect using the range given in the config file and the eye offset"

		eye_range = self.config_options['ghost_eye_range']
		return pygame.Rect(eye_range[0][0] + self.config_options['ghost_eye_offset'], \
							eye_range[1][0], eye_range[0][1] - eye_range[0][0] + 1, eye_range[1][1] - eye_range[1][0] + 1)

#------------------------------------------------------------------------------
# print_pessage()
#------------------------------------------------------------------------------

	def print_message(self, message, time):
		"Prints a large message in the middle of the screen"

		# Create a font object for the message
		message_font = pygame.font.Font(None, 30)

		# Render the message text
		message_text = message_font.render(message, 1, (255, 0, 0, 255))

		# Extract the rect
		message_rect = message_text.get_rect()

		# Create a small background window and paint it black
		message_window = pygame.Surface(message_rect.size)
		message_window = message_window.convert()
		message_window.fill((0,0,0))

		# Get the window's rect
		message_window_rect = message_window.get_rect()

		# Center the message in the window
		message_rect.center = message_window_rect.center

		# Center the window on the screen
		message_window_rect.center = self.canvas.get_rect().center

		# Paint the message on the window
		message_window.blit(message_text, message_rect)

		# Paint the window on the screen
		self.canvas.blit(message_window, message_window_rect)

		# Display the result
		pygame.display.flip()

		# Pause for the give amount of time
		pygame.time.wait(time)

#------------------------------------------------------------------------------
# draw()
#------------------------------------------------------------------------------

	def draw(self):
		"Draws level, pacman, ghosts, and pellets"

		# First, draw the background
		self.canvas.blit(self.background, (0,0))

		# Second, draw level.  Do it tile by tile
		row = 0
		col = 0
		while row < self.state.level.level_dim[1]:
			while col < self.state.level.level_dim[0]:
				# Get the tile identification string from the level layout
				tile_id = self.state.level.level_layout[row][col]
				if int(tile_id) in self.config_options['context_dictionary']:
					# Get the corresponding tile image
					tile = self.tile_images[int(tile_id)]

					# Calculate the real coordinates for the tile
					x_coord = col * self.config_options['tile_size']
					y_coord = row * self.config_options['tile_size']

					# Make the power pellets blink
					if self.blink_time == 0:
						self.on_off = (self.on_off + 1) % 2
						self.blink_time = self.config_options['blink_time']
					if not int(tile_id) == 3 or self.on_off:
						self.canvas.blit(tile, (x_coord, y_coord))
				col += 1
				
			row+= 1
			col = 0
		self.blink_time -= 1

		# Manipulate the Pac-Man image set to match the current direction
		if self.state.current_pacman_direction == UP:
			current_pacman_image_set = map(lambda x: pygame.transform.rotate(x, 90), self.pacman_images)
		elif self.state.current_pacman_direction == DOWN:
			current_pacman_image_set = map(lambda x: pygame.transform.rotate(x, -90), self.pacman_images)
		elif self.state.current_pacman_direction == LEFT:
			current_pacman_image_set = map(lambda x: pygame.transform.flip(x, 1, 0), self.pacman_images)
		elif self.state.current_pacman_direction == RIGHT:
			current_pacman_image_set = self.pacman_images

		# Only update the current Pac-Man image every few frames to avoid blurring
		if self.delay == 0:
			if not self.state.pacman_immobile:
				self.pacman_image_index = (self.pacman_image_index + 1) % self.pacman_image_count
			self.ghost_image_index = (self.ghost_image_index + 1) % self.ghost_image_count
			self.delay = self.config_options['frame_delay']
		self.delay -= 1

		# Then draw the ghosts
		for i in range(GHOSTS):
			if self.state.ghost_mode[i] == VULNERABLE:
				if self.state.ghost_timer[i] <= self.config_options['flash_timer']:
					if not self.state.ghost_timer[i] % 10:
						self.current_ghost_image_set[i] = self.all_ghost_images[((self.state.ghost_timer[i] / 10) % 2) + BLUE]
				else:
					self.current_ghost_image_set[i] = self.all_ghost_images[BLUE]
			else:
				self.current_ghost_image_set[i] = self.all_ghost_images[i]

			# Get the current ghost image for this frame
			self.current_ghost_image[i] = self.current_ghost_image_set[i][self.ghost_image_index]

			# -------------------------------------------
			# ghost eyes
			
			# Extract the left eye pixels
			left_eye_rect = self.extract_left_eye_rect()
			left_eye_image = self.current_ghost_image[i].subsurface(left_eye_rect).convert_alpha()

			# Extract the right eye pixels
			right_eye_rect = self.extract_right_eye_rect()
			right_eye_image = self.current_ghost_image[i].subsurface(right_eye_rect).convert_alpha()

			h_flip = 0
			v_flip = 0
			# Pacman is above us, flip vertically
			if self.state.pacman_rect.topleft[1] < self.state.ghost_rect[i].topleft[1]:
				left_eye_image = pygame.transform.flip(left_eye_image, 0, 1)
				right_eye_image = pygame.transform.flip(right_eye_image, 0, 1)
				h_flip = 1

			# Pacman is to our right, flip horizontally
			if self.state.pacman_rect.topleft[0] > self.state.ghost_rect[i].topleft[0]:
				left_eye_image = pygame.transform.flip(left_eye_image, 1, 0)
				right_eye_image = pygame.transform.flip(right_eye_image, 1, 0)
				v_flip = 1

			# Now draw the ghost
			if self.state.ghost_mode[i] != EYES:
				self.canvas.blit(self.current_ghost_image[i], self.state.ghost_rect[i].topleft)
			coord = self.state.ghost_rect[i].topleft

			# And draw its eyes on top of it
			self.canvas.blit(left_eye_image, (coord[0] + left_eye_rect.left, coord[1] + left_eye_rect.top))
			self.canvas.blit(right_eye_image, (coord[0] + right_eye_rect.left, coord[1] + right_eye_rect.top))

			# Reset eye pixels to default
			if h_flip:
				left_eye_image = pygame.transform.flip(left_eye_image, 0, 1)
				right_eye_image = pygame.transform.flip(right_eye_image, 0, 1)
			if v_flip:
				left_eye_image = pygame.transform.flip(left_eye_image, 1, 0)
				right_eye_image = pygame.transform.flip(right_eye_image, 1, 0)
			#----------------------------------------------

		# Then draw pacman
		if not self.state.pacman_immobile:
			self.current_pacman_image = current_pacman_image_set[self.pacman_image_index]

		# Put Pac-Man on the canvas
		self.canvas.blit(self.current_pacman_image, self.state.pacman_rect.topleft)

		# Draw the score, level and lives left
		score_text = self.score_font.render("SCORE: " + str(self.state.score), 1, (255, 0, 0, 255))
		level_text = self.level_font.render("LEVEL: " + str(self.state.level_number), 1, (255, 255, 0, 255))
		lives_text = self.lives_font.render("LIVES: " + str(self.state.pacman_lives), 1, (0, 255, 0, 255))
		self.canvas.blit(score_text, (5, self.state.level.level_dim[1] * self.config_options['tile_size'] + 5))
		self.canvas.blit(level_text, (self.canvas.get_rect().centerx - 25, self.state.level.level_dim[1] * self.config_options['tile_size'] + 5))
		self.canvas.blit(lives_text, (self.state.level.level_dim[0] * self.config_options['tile_size'] - 60, \
									  self.state.level.level_dim[1] * self.config_options['tile_size'] + 5))

		# Display everything
		pygame.display.flip()