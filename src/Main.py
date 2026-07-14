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
		#self.PlayerSpriteSheet = SpriteSheet(r"path for the spritesheet")
		#self.EnemySpriteSheet = SpriteSheet(r"path for the spritesheet")
		self.GroundSpriteSheet = SpriteSheet(r"C:\Users\flapb\OneDrive - Spencer Academies Trust\comp sci\NEA\coding\images\TX Tileset Grass.png")
		self.map = "src/Maps/Map1.txt"
		self.running = True
  
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
		TileClasses = {"#": Block, "G": Grass, "E": Enemy}
		for i, row in enumerate(self.loadLevel(self.map)):
			for j, tile in enumerate(row):
				Ground(self, j, i)
				if tile == "P":
					self.player = Player(self, j, i)
				elif tile in TileClasses:
					TileClasses[tile](self, j, i)

	def new(self):
		self.playing = True
		self.allSprites = CameraGroup(self)
		self.groundSprites = pygame.sprite.Group()
		self.enemies = pygame.sprite.Group()
		self.blocks = pygame.sprite.Group()
		self.createLevel()

	def update(self):
		self.allSprites.update()

	def events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.playing = False
				self.running = False

	def draw(self):
		self.allSprites.customDraw(self.player)
		self.clock.tick(120)
		pygame.display.update()

	def main(self):
		while self.playing:
			self.clock.tick(120)
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