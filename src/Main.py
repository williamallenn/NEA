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
		self.ZombieSpriteSheet = SpriteSheet("images/zombie-sheet.png",alpha=True)
		self.GroundSpriteSheet = SpriteSheet("images/Floor.png")
		self.map = "src/Maps/Map1.txt"
		self.EnemyCount = 5
		self.running = True
		self.state = "menu"
		pygame.mouse.set_cursor(*pygame.cursors.broken_x)

		w, h = self.screen.get_size()
		self.playButton = Button("images/Play_button.png", w // 2, h // 2 + 20, scale=2.5)
		self.settingsButton = Button("images/Settings_button.png", w // 2, h // 2 + 160, scale=2.5)
		self.exitButton = Button("images/Exit_button.png", w // 2, h // 2 + 300, scale=2.5)

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

	def menu(self):
		while self.state == "menu" and self.running:
			mouse_pos = pygame.mouse.get_pos()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
					self.state = None

				if self.playButton.clicked(event):
					self.state = "playing"
				elif self.settingsButton.clicked(event):
					self.state = "settings"
				elif self.exitButton.clicked(event):
					self.running = False
					self.state = None

			self.playButton.update(mouse_pos)
			self.settingsButton.update(mouse_pos)
			self.exitButton.update(mouse_pos)

			self.screen.fill("#73D8E7")
			self.playButton.draw(self.screen)
			self.settingsButton.draw(self.screen)
			self.exitButton.draw(self.screen)

			pygame.display.update()
			self.clock.tick(60)

	def settingsMenu(self):
		font = pygame.font.SysFont(None, 48)
		while self.state == "settings" and self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
					self.state = None
				if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
					self.state = "menu"

			self.screen.fill("black")
			text = font.render("Settings (placeholder) - press ESC to go back", True, "white")
			self.screen.blit(text, text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2)))
			pygame.display.update()
			self.clock.tick(60)

	def run(self):
		while self.running:
			if self.state == "menu":
				self.menu()
			elif self.state == "settings":
				self.settingsMenu()
			elif self.state == "playing":
				self.new()
				self.main()
				self.state = "menu"

g = Game()
g.run()

pygame.quit()
sys.exit()