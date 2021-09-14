import sys
import pygame
import random
import os
import neat
from math import sqrt
from pygame.locals import *
pygame.font.init()
FPS = 30
WIN_WIDTH = 800
WIN_HEIGHT = 800

BOY_IMG = pygame.image.load("boy.png")
BLOOD_IMG = pygame.image.load("inkspillspot.png")
PIPE_IMG = pygame.transform.scale2x(pygame.image.load("pipe.png"))
BG_IMG = pygame.image.load("BG.jpg")
STAT_FONT = pygame.font.SysFont("comicsans", 50)
STAT2_FONT = pygame.font.SysFont("comicsans", 25)

GENERATION = 0

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
class Pipe:
    GAP = 250
    VEL = 10

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()


    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, boy):
        boy_mask = boy.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - boy.x, self.top - round(boy.y))
        bottom_offset = (self.x - boy.x, self.bottom - round(boy.y))

        b_point = boy_mask.overlap(bottom_mask, bottom_offset)
        t_point = boy_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        return False

class Pipe2:
    GAP = 250
    VEL = 10
    def __init__(self, y):
        self.y = y
        self.width = 0

        self.left = 0
        self.right = 0
        self.PIPE_RIGHT = pygame.transform.rotate(PIPE_IMG, 90)
        self.PIPE_LEFT = pygame.transform.rotate(PIPE_IMG, -90)

        self.passed = False
        self.set_width()

    def set_width(self):
        self.width = random.randrange(50, 450)
        self.right = self.width + self.GAP
        self.left = self.width - self.PIPE_LEFT.get_width()

    def move(self):
        self.y += self.VEL

    def draw(self, win):
        win.blit(self.PIPE_LEFT, (self.left, self.y))
        win.blit(self.PIPE_RIGHT, (self.right, self.y))

    def collide(self, boy):
        boy_mask = boy.get_mask()
        left_mask = pygame.mask.from_surface(self.PIPE_LEFT)
        right_mask = pygame.mask.from_surface(self.PIPE_RIGHT)

        left_offset = (self.left - round(boy.x), self.y - boy.y)
        right_offset = (self.right - round(boy.x), self.y - boy.y)

        l_point = boy_mask.overlap(left_mask, left_offset)
        r_point = boy_mask.overlap(right_mask, right_offset)

        if l_point or r_point:
            return True
        return False

class Boy:
	IMG = BOY_IMG
	BLOOD = BLOOD_IMG
	def __init__(self):
		self.x = int(WIN_WIDTH / 2)
		self.y = int(WIN_HEIGHT / 2)
		self.VEL = 20
		self.pipe1_index = 0
		self.pipe2_index = 0
		self.prev1 = 0
		self.prev2 = 0

	def move(self, direction):
		if direction == LEFT and self.x > 0:
			self.x -= self.VEL
		elif direction == RIGHT and self.x < WIN_WIDTH - 50:
			self.x += self.VEL
		elif direction == UP and self.y > 0:
			self.y -= self.VEL
		elif direction == DOWN and self.y < WIN_HEIGHT - 60:
			self.y += self.VEL

	def get_mask(self):
		return pygame.mask.from_surface(self.IMG)

class Background:
	VEL = 0.1
	WIDTH = BG_IMG.get_width()
	IMG = BG_IMG

	def __init__(self):
		self.y = 0
		self.x1 = 0
		self.x2 = self.WIDTH

	def move(self):
		self.x1 -= self.VEL
		self.x2 -= self.VEL

		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win):
		win.blit(self.IMG, (self.x1, self.y))
		win.blit(self.IMG, (self.x2, self.y))



def main(genomes, config):

	global FPSCLOCK, DISPLAYSURF, BASICFONT

	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	DISPLAYSURF = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
	pygame.display.set_caption('FINAL BOY')

	nets = []
	ge = []
	boys = []
	pipes1 = [Pipe(800)]
	pipes2 = [Pipe2(0)]
	background = Background()



	for _, g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		boys.append(Boy())
		g.fitness = 0
		ge.append(g)


	run = True
	global GENERATION
	GENERATION += 1
	while run:
		background.draw(DISPLAYSURF)
		background.move()

		for boy in boys:

			boy.pipe1_index = 0


			boy.pipe2_index = 0

		for boy in boys:
			DISPLAYSURF.blit(boy.IMG, (boy.x, boy.y))

		for event in pygame.event.get():
			if event.type == QUIT:
				terminate()
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					terminate()
				elif event.key == K_q:
					run = False


		for b, boy in enumerate(boys):
			outputMove = nets[b].activate([boy.x, boy.y, abs(boy.x - pipes2[boy.pipe2_index].right), abs(boy.y - pipes1[boy.pipe1_index].height)])
			ge[b].fitness += 0.1
			maxOutputMove = max(outputMove)
			if outputMove.index(maxOutputMove) == 0:
				boy.move(LEFT)
			if outputMove.index(maxOutputMove) == 1:
				boy.move(RIGHT)
			if outputMove.index(maxOutputMove) == 2:
				boy.move(UP)
			if outputMove.index(maxOutputMove) == 3:
				boy.move(DOWN)


		rem1 = []
		rem2 = []
		add_pipe1 = False
		add_pipe2 = False
		for pipe in pipes1:
			for x, boy in enumerate(boys):
				if pipe.collide(boy):
					ge[x].fitness -= 1
					boys.pop(x)
					nets.pop(x)
					ge.pop(x)

				if not pipe.passed and pipe.x < 0:
					pipe.passed = True
					add_pipe1 = True
			if pipe.x + pipe.PIPE_TOP.get_width() < 0:
				rem1.append(pipe)

			pipe.move()

		for pipe in pipes2:
			for x, boy in enumerate(boys):
				if pipe.collide(boy):

					ge[x].fitness -= 1
					boys.pop(x)
					nets.pop(x)
					ge.pop(x)

				if not pipe.passed and pipe.y > 800:
					pipe.passed = True
					add_pipe2 = True

			if pipe.y > 800:
				rem2.append(pipe)

			pipe.move()

		if add_pipe1:
			pipes1.append(Pipe(800))

		if add_pipe2:
			pipes2.append(Pipe2(0))





		for r in rem1:
			pipes1.remove(r)

		for r in rem2:
			pipes2.remove(r)


		for x, boy in enumerate(boys):
			if boy.x + boy.IMG.get_width() > 750 or boy.x <= 0 or boy.y + boy.IMG.get_height() >= 750 or boy.y < 0:
				boys.pop(x)
				nets.pop(x)
				ge.pop(x)



		if len(boys) <= 0:
			run = False
			break

		for pipe in pipes1:
			pipe.draw(DISPLAYSURF)
		for pipe in pipes2:
			pipe.draw(DISPLAYSURF)

		gen_text = STAT_FONT.render("GENERATION: " + str(GENERATION), 1, (255, 255, 255))
		DISPLAYSURF.blit(gen_text, (WIN_WIDTH - 10 - gen_text.get_width(), 10))

		if len(boys) > 1:
			boys_text = STAT_FONT.render("BOYS: " + str(len(boys)), 1, WHITE)
			DISPLAYSURF.blit(boys_text, (WIN_WIDTH - 10 - boys_text.get_width(), 50))
		else:
			final_boy_text = STAT_FONT.render("FINAL BOY", 1, RED)
			DISPLAYSURF.blit(final_boy_text, (WIN_WIDTH - 10 - final_boy_text.get_width(), 50))

		for x, boy in enumerate(boys):
			boy_text = STAT2_FONT.render(str(int(ge[x].fitness)), 1, WHITE)
			DISPLAYSURF.blit(boy_text, (boy.x, boy.y))

		if add_pipe1 or add_pipe2:
			for g in ge:
				g.fitness += 5

		pygame.display.update()
		FPSCLOCK.tick(FPS)


def terminate():
	pygame.quit()
	sys.exit()


def run(config_file):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

	p = neat.Population(config)

	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)

	winner = p.run(main, 100)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)

