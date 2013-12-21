import sys
import procgame
import pinproc
from threading import Thread
import random
import string
import time
import locale
import math
import copy
import ctypes
from .. import config

from procgame.events import EventManager

try:
	import pygame
	import pygame.locals
except ImportError:
	print "Error importing pygame; ignoring."
	pygame = None


class Desktop():
	"""The :class:`Desktop` class helps manage interaction with the desktop, providing both a windowed
	representation of the DMD, as well as translating keyboard input into pyprocgame events."""
	
	exit_event_type = 99
	"""Event type sent when Ctrl-C is received."""
	
	key_map = {}

	dots_w = 128
	dots_h = 32

	def __init__(self):
		print 'Desktop init begun.'
		self.ctrl = 0
		self.i = 0
		self.key_events = []
		if 'pygame' in globals():
			self.dots_w = config.value_for_key_path(keypath='dmd_dots_w', default=128)
			self.dots_h = config.value_for_key_path(keypath='dmd_dots_h', default=32)
			self.setup_window()
		else:
			print 'Desktop init skipping setup_window(); pygame does not appear to be loaded.'

		dmd_grid_path = config.value_for_key_path(keypath='dmd_grid_path', default='.')
		
		self.grid_image = pygame.surface.Surface((self.dots_w*10,self.dots_h*10),pygame.SRCALPHA)
		r = pygame.Rect(0,0,self.dots_w*10,self.dots_h*10)
		self.grid_image.fill((0,0,0,0),r)
		grid_32x32segment = pygame.image.load(dmd_grid_path + 'dmdgrid32x32.png')
		print("building a grid of " + str(self.dots_w) + "x" + str(self.dots_h))
		for step_w in range(0,self.dots_w/32):
			for step_h in range(0,self.dots_h/32):
				print("--stamping at " + str(step_w) + "x" + str(step_h))
				self.grid_image.blit(grid_32x32segment,(step_w*320,step_h*320))
		#self.grid_image = pygame.image.load('./dmdgrid.png')
		#self.grid_image = pygame.image.load('./dmdgrid256x128.png')
		self.grid_image = pygame.transform.scale(self.grid_image, self.screen.get_size()).convert_alpha()

		self.add_key_map(pygame.locals.K_LSHIFT, 3)
		self.add_key_map(pygame.locals.K_RSHIFT, 1)
	
	def add_key_map(self, key, switch_number):
		"""Maps the given *key* to *switch_number*, where *key* is one of the key constants in :mod:`pygame.locals`."""
		self.key_map[key] = switch_number
	
	def clear_key_map(self):
		"""Empties the key map."""
		self.key_map = {}

	def get_keyboard_events(self):
		"""Asks :mod:`pygame` for recent keyboard events and translates them into an array
		of events similar to what would be returned by :meth:`pinproc.PinPROC.get_events`."""
		#self.key_events = []
		for event in pygame.event.get():
			EventManager.default().post(name=self.event_name_for_pygame_event_type(event.type), object=self, info=event)
			key_event = {}
			if event.type == pygame.locals.KEYDOWN:
				if event.key == pygame.locals.K_RCTRL or event.key == pygame.locals.K_LCTRL:
					self.ctrl = 1
				if event.key == pygame.locals.K_c:
					if self.ctrl == 1:
						key_event['type'] = self.exit_event_type
						key_event['value'] = 'quit'
				elif (event.key == pygame.locals.K_ESCAPE):
					key_event['type'] = self.exit_event_type
					key_event['value'] = 'quit'
				elif event.key in self.key_map:
					key_event['type'] = pinproc.EventTypeSwitchClosedDebounced
					key_event['value'] = self.key_map[event.key]
			elif event.type == pygame.locals.KEYUP:
				if event.key == pygame.locals.K_RCTRL or event.key == pygame.locals.K_LCTRL:
					self.ctrl = 0
				elif event.key in self.key_map:
					key_event['type'] = pinproc.EventTypeSwitchOpenDebounced
					key_event['value'] = self.key_map[event.key]
			if len(key_event):
				self.key_events.append(key_event)
		e = self.key_events
		self.key_events = []
		return e
	
	
	event_listeners = {}
	
	def event_name_for_pygame_event_type(self, event_type):
		return 'pygame(%s)' % (event_type)
	
	screen = None
	""":class:`pygame.Surface` object representing the screen's surface."""

	screen_scale =7 # this is the factor to pygame scale the display.  192x96 (x6) = 1152x576

	# you'll need to change your displayController to width=192, height=96 and the same for all layers created

	def setup_window(self):
		pygame.init()
		#self.screen = pygame.display.set_mode((128*self.screen_multiplier, 32*self.screen_multiplier))
		# self.screen = pygame.display.set_mode((self.dots_w*self.screen_scale, self.dots_h*self.screen_scale),pygame.OPENGL|pygame.FULLSCREEN|pygame.DOUBLEBUF)
		# self.screen = pygame.display.set_mode((self.dots_w*self.screen_scale, self.dots_h*self.screen_scale),pygame.HWPALETTE|pygame.FULLSCREEN|pygame.DOUBLEBUF)
		self.screen = pygame.display.set_mode((self.dots_w*self.screen_scale, self.dots_h*self.screen_scale))

		print("****************")
		print(pygame.display.Info())
		print("****************")

		pygame.display.set_caption('Press CTRL-C to exit')
		self.scratch_surface = pygame.surface.Surface((self.dots_w, self.dots_h)).convert()
		print("****************")
		print(self.scratch_surface.get_flags())
		print("****************")

	def draw(self, frame):
		"""Draw the given :class:`~procgame.dmd.Frame` in the window."""

		self.scratch_surface.blit(frame.pySurface,(0,0))

		# scale the created image using pygame's (hardware scaler)
		# swap the uncommented line with the commented one for "rounded" 
		# effect, overall darker dots, and some performance penalty
		pygame.transform.scale(self.scratch_surface, self.screen.get_size(), self.screen)
		#pygame.transform.smoothscale(self.scratch_surface, self.screen.get_size(), self.screen)

		# Blit the grid on top to give it a more authentic DMD look.		
		self.screen.blit(self.grid_image,(0,0))

		##pygame.display.update()
		pygame.display.flip()
	

	def __str__(self):
		return '<Desktop pygame>'

