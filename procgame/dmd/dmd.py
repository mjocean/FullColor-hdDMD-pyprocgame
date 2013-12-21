import pinproc
import time
import os
import pygame
import pygame.locals
from procgame.dmd import VgaDMD

class Frame(object):
	"""DMD frame/bitmap.
	
	"""
	
	width = 0
	"""Width of the frame in dots."""
	height = 0
	"""Height of the frame in dots."""
	
	pySurface = None
	""" the pygame surface that backs the frame """

	def __init__(self, width, height):
		"""Initializes the frame to the given `width` and `height`."""
		# super(Frame, self).__init__(width, height)
		self.width = width
		self.height = height
		self.pySurface = pygame.surface.Surface((width, height))
		self.x_offset = 4 #bytes_per_pixel 
		self.y_offset = self.width*4 # every y_offset Bytes is the next line
		self.font_dots = []

	def copy_rect(dst, dst_x, dst_y, src, src_x, src_y, width, height, op="copy"):
		"""Static method which performs some type checking before calling :meth:`pinproc.DMDBuffer.copy_to_rect`."""

		src_rect = pygame.Rect(int(src_x),int(src_y),int(width),int(height))
		dst_rect = pygame.Rect(int(dst_x),int(dst_y),int(width),int(height))

		""" 1.8.0: BLEND_ADD, BLEND_SUB, BLEND_MULT, BLEND_MIN, BLEND_MAX 
		 in 1.8.1: BLEND_RGBA_ADD, BLEND_RGBA_SUB, BLEND_RGBA_MULT, BLEND_RGBA_MIN, 
					BLEND_RGBA_MAX BLEND_RGB_ADD, BLEND_RGB_SUB, BLEND_RGB_MULT, 
					BLEND_RGB_MIN, BLEND_RGB_MAX 
		"""
		if (op=="copy"):
			special_flags = 0
		elif(op=="add"):
			special_flags = pygame.BLEND_ADD
		elif(op == "sub"):
			special_flags = pygame.BLEND_SUB
		elif(op == "blacksrc"):
			special_flags = 0;
			src.pySurface.set_colorkey((0,0,0))
		elif(op == "alpha"):
			special_flags = 0
			# TODO: THIS...
		elif(op == "alphaboth"):
			special_flags = 0
			# TODO: THIS...
		else:
			raise ValueError, "Operation type not recognized."

		dst.pySurface.blit(src.pySurface, dst_rect, src_rect, special_flags = special_flags)
		#src.copy_to_rect(dst, int(dst_x), int(dst_y), int(src_x), int(src_y), int(width), int(height), op)
		src.pySurface.set_colorkey(None)

	copy_rect = staticmethod(copy_rect)
	
	def subframe(self, x, y, width, height):
		"""Generates a new frame based on a sub rectangle of this frame."""
		subframe = Frame(width, height)
		Frame.copy_rect(subframe, 0, 0, self, x, y, width, height, 'copy')
		return subframe
	
	def copy(self):
		"""Returns a copy of itself."""
		frame = Frame(self.width, self.height)
		frame.pySurface = self.pySurface.copy()
		#frame.set_data(self.get_data())
		return frame
	
	def ascii(self):
		"""Returns an ASCII representation of itself."""
		# output = ''
		# table = [' ', '.', '.', '.', ',', ',', ',', '-', '-', '=', '=', '=', '*', '*', '#', '#',]
		# for y in range(self.height):
		# 	for x in range(self.width):
		# 		dot = self.get_dot(x, y)
		# 		output += table[dot & 0xf]
		# 	output += "\n"
		# return output
		raise ValueError, "Unsupported method Ascii"
	
	def create_with_text(lines, palette = {' ':0, '*':15}):
		"""Create a frame based on text.
		
		This class method can be used to generate small sprites within the game's source code::
		
			frame = Frame.create_with_text(lines=[ \\
			    '*+++*', \\
			    ' *+* ', \\
			    '  *  '], palette={' ':0, '+':7, '*':15})
		"""
		height = len(lines)
		if height > 0:
			width = len(lines[0])
		else:
			width = 0
		frame = Frame(width, height)
		for y in range(height):
			for x in range(width):
				char = lines[y][x]
				frame.set_dot(x, y, palette[char])
		return frame
	create_with_text = staticmethod(create_with_text)

	def create_frames_from_grid( self, num_cols, num_rows ):
		frames = []
		width = self.width / num_cols
		height = self.height / num_rows
	
		# Use nested loops to step through each column of each row, creating a new frame at each iteration and copying in the appropriate data.
		for row_index in range(0,num_rows):
			for col_index in range(0,num_cols):
				new_frame = Frame(width, height)
				Frame.copy_rect(dst=new_frame, dst_x=0, dst_y=0, src=self, src_x=width*col_index, src_y=height*row_index, width=width, height=height, op='copy')
				frames += [new_frame]
		return frames

	def set_font_dot(self, x, y, color):
	 	self.font_dots[x+(y*self.width)]=color

	def get_font_dot(self, x, y):
	 	return ord(self.font_dots[x+(y*self.width)])

	def fill_rect(self, x,y,w,h,c):
		r = pygame.Rect(int(x),int(y),int(w),int(h))
		self.pySurface.fill(c,r)


	def clear(self):
		self.pySurface.fill((0,0,0))

	def set_surface(self, surf):
		try:
			self.pySurface = surf.convert()
		except Exception as e:
			self.pySurface = surf
		

	def build_surface_from_8bit_dmd_string(self, str_data):
		self.eight_to_RGB_map = VgaDMD.get_palette_ch()
		self.font_dots = str_data
		x = 0
		y = 0
		d = ""
		for dot in str_data:
			# get the Byte from the frame data
			dot = ord(dot) 
			# convert it to the correct RGB pallette color
			(r,g,b) = self.eight_to_RGB_map[dot]

			d +=r + g + b
			# # write out the color into the target buffer array
			# index = y*self.y_offset + x*self.x_offset

			# #self.pySurface[index:(index+bytes_per_pixel)] = (b,g,r,0)
			# buffer_interface[index:(index+4)] = (b,g,r,0)

			# #move to the next dot
			# x += 1
			# if x == self.width:
			# 	x = 0
			# 	y += 1 
		self.pySurface = pygame.image.fromstring(d,(self.width,self.height),'RGB').convert()
			

	def get_surface_string(self):
		# convert every pixel to 8 bit mapping
		return pygame.image.tostring(self.pySurface,'RGB')
	#	#self.pySurface.get_buffer()

	# def set_data(self, frame_string):
	# 	ar = pygame.PixelArray(self.pySurface)
	# 	ar = frame_string
	# 	del ar
		#self.pySurface = pygame.image.fromstring(frame_string,(self.width,self.height),'P')
		
		# x = 0
		# y = 0
		# for dot in frame_string:
		# 	# get the Byte from the frame data
		# 	dot = ord(dot) 
		# 	# convert it to the correct RGB pallette color
		# 	(r,g,b) = self.eight_to_RGB_map[dot]

		# 	# write out the color into the target buffer array
		# 	index = y*self.y_offset + x*self.x_offset

		# 	#self.pySurface[index:(index+bytes_per_pixel)] = (b,g,r,0)
		# 	self.pySurface[index:(index+4)] = (b,g,r,0)

		# 	#move to the next dot
		# 	x += 1
		# 	if x == self.width:
		# 		x = 0
		# 		y += 1 


class Layer(object):
	"""
	The ``Layer`` class is the basis for the pyprocgame display architecture.
	Subclasses override :meth:`next_frame` to provide a frame for the current moment in time.
	Handles compositing of provided frames and applying transitions within a :class:`DisplayController` context.
	"""
	
	opaque = False
	"""Determines whether layers below this one will be rendered.  
	If `True`, the :class:`DisplayController` will not render any layers after this one 
	(such as from modes with lower priorities -- see :class:`DisplayController` for more information).
	"""
	
	target_x = 0
	"""Base `x` component of the coordinates at which this layer will be composited upon a target buffer."""
	target_y = 0
	"""Base `y` component of the coordinates at which this layer will be composited upon a target buffer."""
	target_x_offset = 0
	"""Translation component used in addition to :attr:`target_x` as this layer's final compositing position."""
	target_y_offset = 0
	"""Translation component used in addition to :attr:`target_y` as this layer's final compositing position."""
	enabled = True
	"""If `False`, :class:`DisplayController` will ignore this layer."""
	composite_op = 'copy'
	"""Composite operation used by :meth:`composite_next` when calling :meth:`~pinproc.DMDBuffer.copy_rect`."""
	transition = None
	"""Transition which :meth:`composite_next` applies to the result of :meth:`next_frame` prior to compositing upon the output."""
	
	def __init__(self, opaque=False):
		"""Initialize a new Layer object."""
		super(Layer, self).__init__()
		self.opaque = opaque
		self.set_target_position(0, 0)

	def reset(self):
		# To be overridden
		pass

	def set_target_position(self, x, y):
		"""Setter for :attr:`target_x` and :attr:`target_y`."""
		self.target_x = x
		self.target_y = y
	def next_frame(self):
		"""Returns an instance of a Frame object to be shown, or None if there is no frame.
		The default implementation returns ``None``; subclasses should implement this method."""
		return None
	def composite_next(self, target):
		"""Composites the next frame of this layer onto the given target buffer.
		Called by :meth:`DisplayController.update`.
		Generally subclasses should not override this method; implementing :meth:`next_frame` is recommended instead.
		"""
		src = self.next_frame()
		if src != None:
			if self.transition != None:
				src = self.transition.next_frame(from_frame=target, to_frame=src)
			Frame.copy_rect(dst=target, dst_x=self.target_x+self.target_x_offset, dst_y=self.target_y+self.target_y_offset, src=src, src_x=0, src_y=0, width=src.width, height=src.height, op=self.composite_op)
		return src

