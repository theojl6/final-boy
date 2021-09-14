import sys
import pygame
import random
import os
from pygame.locals import * # import top-level variables
pygame.font.init()
FPS = 30
WIN_WIDTH = 800
WIN_HEIGHT = 600
CELLSIZE = 20
assert WIN_WIDTH % CELLSIZE == 0, "Window width needs to be multiple of cell size"
assert WIN_HEIGHT % CELLSIZE == 0, "Window height needs to be multiple of cell size"
CELLWIDTH = int(WIN_WIDTH / CELLSIZE)
CELLHEIGHT = int(WIN_HEIGHT / CELLSIZE)
BOY_IMG = pygame.image.load("boy.png")
STAR_IMG = pygame.image.load("Star.png")
ZOMB_IMG = pygame.image.load("squirrel.png")
BLOOD_IMG = pygame.image.load("inkspillspot.png")
STAT_FONT = pygame.font.SysFont("comicsans", 50)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

class Star:
	IMG = STAR_IMG
	VEL = 20

	def __init__(self, x, y, dir):
		self.x = x
		self.y = y
		self.dir = dir

	def move(self):
		if self.dir == LEFT:
			self.x -= self.VEL
		elif self.dir == RIGHT:
			self.x += self.VEL
		elif self.dir == UP:
			self.y -= self.VEL
		elif self.dir == DOWN:
			self.y += self.VEL

	def draw(self, surface):
		surface.blit(self.IMG, (self.x, self.y))

	def get_mask(self):
		return pygame.mask.from_surface(self.IMG)

class Zomb:
	IMG = ZOMB_IMG
	DEATH_IMG = BLOOD_IMG
	VEL = 1

	def __init__(self, x, y):
		self.x = x
		self.y = y

	def move(self, boyx, boyy):
		if self.x > boyx:
			self.x -= self.VEL
		else:
			self.x += self.VEL
		if self.y > boyy:
			self.y -= self.VEL
		else:
			self.y += self.VEL

	def draw(self, surface):
		surface.blit(self.IMG, (self.x, self.y))

	def collide(self, star):
		star_mask = star.get_mask()
		zomb_mask = pygame.mask.from_surface(self.IMG)
		zomb_pos = (self.x - star.x, self.y - star.y)
		c_point = star_mask.overlap(zomb_mask, zomb_pos)
		if c_point:
			return True
		else:
			return False

	def get_mask(self):
		return pygame.mask.from_surface(self.IMG)

	def death(self, surface):
		x = self.x
		y = self.y
		surface.blit(self.DEATH_IMG, (x, y))


class Boy:
	IMG = BOY_IMG
	def __init__(self):
		self.x = int(WIN_WIDTH / 2)
		self.y = int(WIN_HEIGHT / 2)
		self.VEL = 5
		self.score = 0

	def move(self, direction):
		if direction == LEFT:
			self.x -= self.VEL
		elif direction == RIGHT:
			self.x += self.VEL
		elif direction == UP:
			self.y -= self.VEL
		elif direction == DOWN:
			self.y += self.VEL

	def collide(self, zomb):
		zomb_mask = zomb.get_mask()
		boy_mask = pygame.mask.from_surface(self.IMG)
		boy_pos = (self.x - zomb.x, self.y - zomb.y)
		c_point = zomb_mask.overlap(boy_mask, boy_pos)
		if c_point:
			return True
		else:
			return False

def generateZomb(x, y):
	zomb = Zomb(x, y)
	return zomb

def main():
	global FPSCLOCK, DISPLAYSURF, BASICFONT

	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	DISPLAYSURF = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
	pygame.display.set_caption('Zombie Defense')

	while True:
		runGame()

def runGame():

	stars = []
	zombs = []
	blood = []

	boy = Boy()

	while True:
		DISPLAYSURF.fill(BGCOLOR)
		DISPLAYSURF.blit(boy.IMG, (boy.x, boy.y))

		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()
			elif event.type == KEYDOWN:
				if event.key == K_a:
					star = Star(boy.x, boy.y, LEFT)
					stars.append(star)
				elif event.key == K_d:
					star = Star(boy.x, boy.y, RIGHT)
					stars.append(star)
				elif event.key == K_w:
					star = Star(boy.x, boy.y, UP)
					stars.append(star)
				elif event.key == K_s:
					star = Star(boy.x, boy.y, DOWN)
					stars.append(star)
				elif event.key == K_ESCAPE:
					terminate()

		keys = pygame.key.get_pressed()
		if keys[pygame.K_UP] and boy.y > 0:
			boy.move(UP)
		if keys[pygame.K_DOWN] and boy.y < WIN_HEIGHT - 60:
			boy.move(DOWN)
		if keys[pygame.K_LEFT] and boy.x > 0:
			boy.move(LEFT)
		if keys[pygame.K_RIGHT] and boy.x < WIN_WIDTH - 50:
			boy.move(RIGHT)

		for b in blood:
			b.death(DISPLAYSURF)

		for star in stars:
			star.draw(DISPLAYSURF)
			star.move()


		while len(zombs) < 5:
			randx, randy = getRandomBorderCoord()
			zombs.append(generateZomb(randx, randy))

		for zomb in zombs:
			zomb.draw(DISPLAYSURF)
			zomb.move(boy.x, boy.y)
			if boy.collide(zomb):
				zombs = []
				blood = []
				boy.score = 0
				boy = Boy()


		for z, zomb in enumerate(zombs):
			for s, star in enumerate(stars):
				if zomb.collide(star):
					blood.append(zomb)
					zombs.pop(z)
					stars.pop(s)
					boy.score += 1


		text = STAT_FONT.render("Score: " + str(boy.score), 1, (255, 255, 255))
		DISPLAYSURF.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

		pygame.display.update()
		FPSCLOCK.tick(FPS)

def getRandomBorderCoord():
	x, y = None, None
	border = random.randint(0, 3)
	if border == 0:
		x = 0
		y = random.randint(0, 600)
	elif border == 1:
		x = 800
		y = random.randint(0, 600)
	elif border == 2:
		x = random.randint(0, 800)
		y = 0
	elif border == 3:
		x = random.randint(0, 800)
		y = 600

	return x, y


def terminate():
	pygame.quit()
	sys.exit()

if __name__ == '__main__':
	main()

