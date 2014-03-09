import sys
import os
import procgame.dmd
import time
import re
import string
import Image
import pygame

import logging
logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def dmd_to_image(src_filename, dst_filename, dots_w=128, dots_h=32):
	pygame.init()
	pygame.display.set_mode((dots_w, dots_h))
	anim = procgame.dmd.Animation().load(src_filename)
	frame = anim.frames[0]
	pygame.image.save(frame.pySurface,dst_filename)

def tool_populate_options(parser):
    pass

def tool_get_usage():
    return """[options] <input.dmd> <outputimage> [width height]"""

def tool_run(options, args):
	if len(args) < 2:
		return False
	if len(args) == 4:
		w = args[2]
		h = args[3]
		dmd_to_image(src_filename=args[0], dst_filename=args[1], dots_w = w, dots_h =h)
	else:
		dmd_to_image(src_filename=args[0], dst_filename=args[1])
	return True
