import pygame
import sys
import random
from sprites import *

class Game:
	def __init__(self):
		pygame.init()
		info = pygame.display.Info()
		self.screen = pygame.display.set_mode((info.current_w,(info.current_h - 60)), pygame.SCALED, pygame.RESIZABLE)
		self.clock = pygame.time.Clock()
		self.dt = 0
		#self.PlayerSpriteSheet = SpriteSheet(r"path for the spritesheet")
		#self.EnemySpriteSheet = SpriteSheet(r"path for the spritesheet")
		self.GroundSpriteSheet = SpriteSheet("images/Floor.png")
		self.map = "src/Maps/Map1.txt"
		self.EnemyCount = 5
		self.running = True
		pygame.mouse.set_cursor(*pygame.cursors.broken_x)
  
	def ChangeMap(self, newMap):
		self.map = newMap
		self.new()

	def loadLevel(self, path):
		try:
			with open(path, "r") as f:
				return [line.rstrip("\n") for line in f]
		except FileNotFoundError:
			print(f"Level file not found: ({path})")
			return []

	def createLevel(self):
		TileClasses = {"#": Block, "D": Dirt, "W": Water, "L": WaterTopLeft, "T": WaterTop, "R": WaterTopRight, "l": WaterLeft, "r": WaterRight}
		level = self.loadLevel(self.map)
		self.validTiles = []
		for i, row in enumerate(level):
			for j, tile in enumerate(row):
				Ground(self, j, i)
				if tile in TileClasses:
					TileClasses[tile](self, j, i)
				if tile == ".":
					self.validTiles.append((j, i))

		height = len(level)
		width = max((len(row) for row in level), default=0)
		self.player = Player(self, width // 2, height // 2)
		self.spawnEnemies(self.EnemyCount)

	def spawnEnemies(self, count):
		for i in range(count):
			x, y = random.choice(self.validTiles)
			Enemy(self, x, y)

	def new(self):
		self.playing = True
		self.allSprites = CameraGroup(self)
		self.groundSprites = pygame.sprite.Group()
		self.enemies = pygame.sprite.Group()
		self.blocks = pygame.sprite.Group()
		self.bullets = pygame.sprite.Group()
		self.createLevel()

	def update(self):
		self.allSprites.update(self.dt)

	def events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.playing = False
				self.running = False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					self.player.shoot()

	def draw(self):
		self.allSprites.customDraw(self.player)
		pygame.display.update()

	def main(self):
		while self.playing:
			self.dt = self.clock.tick(120) / 1000
			self.events()
			self.update()
			self.draw()
		self.running = False

g = Game()
g.new()
while g.running:
	g.main()

pygame.quit()
sys.exit()