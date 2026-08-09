import pygame
import sys
import random
from sprites import *

TileLegend = {
	"#": {"blocking": True},
	"D": {"ground": "dirt"},
	"W": {"ground": "water"},
}

def isWaterTile(grid, x, y):
	if 0 <= y < len(grid) and 0 <= x < len(grid[y]):
		return grid[y][x] == "W"
	return False

def getWaterVariant(grid, x, y):
	up = isWaterTile(grid, x, y - 1)
	down = isWaterTile(grid, x, y + 1)
	left = isWaterTile(grid, x - 1, y)
	right = isWaterTile(grid, x + 1, y)

	if not up and not left:
		return "water_top_left"
	if not up and not right:
		return "water_top_right"
	if not up:
		return "water_top"
	if not left:
		return "water_left"
	if not right:
		return "water_right"
	return "water"

class Queue:
	def __init__(self):
		self.items = []

	def enqueue(self, item):
		self.items.append(item)

	def dequeue(self):
		return self.items.pop(0)

	def isEmpty(self):
		return len(self.items) == 0


def getReachableTiles(validTiles, start):
	validSet = set(validTiles)
	visited = {start}
	queue = Queue()
	queue.enqueue(start)
	while not queue.isEmpty():
		x, y = queue.dequeue()
		for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
			neighbour = (x + dx, y + dy)
			if neighbour in validSet and neighbour not in visited:
				visited.add(neighbour)
				queue.enqueue(neighbour)
	return visited

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
		self.running = True
		self.state = "menu"
		self.coins = 0
		self.wave = 1
		self.waveActive = False
		self.hudFont = pygame.font.SysFont(None, 36)
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
		level = self.loadLevel(self.map)
		self.validTiles = []
		for i, row in enumerate(level):
			for j, tile in enumerate(row):
				info = TileLegend.get(tile)
				if info and info.get("ground") == "water":
					ground_key = getWaterVariant(level, j, i)
				elif info and "ground" in info:
					ground_key = info["ground"]
				else:
					ground_key = "ground"
				Ground(self, j, i, ground_key)
				if info and info.get("blocking"):
					Block(self, j, i)
				if tile == ".":
					self.validTiles.append((j, i))

		height = len(level)
		width = max((len(row) for row in level), default=0)
		spawn = (width // 2, height // 2)
		self.player = Player(self, *spawn)

		self.reachableTiles = getReachableTiles(self.validTiles, spawn)
		unreachable = set(self.validTiles) - self.reachableTiles
		if unreachable:
			print(f"Warning: {len(unreachable)} unreachable tile(s) in {self.map}: {sorted(unreachable)}")

		self.startWave()

	def spawnEnemies(self, count):
		spawnPool = list(self.reachableTiles) if self.reachableTiles else self.validTiles
		for i in range(count):
			x, y = random.choice(spawnPool)
			Enemy(self, x, y)

	def startWave(self):
		self.waveActive = True
		enemyCount = EnemyCountBase + (self.wave - 1) * EnemyCountIncrement
		self.spawnEnemies(enemyCount)

	def killEnemy(self, enemy):
		self.coins += CoinsPerKill
		enemy.kill()

	def checkWaveStatus(self):
		if self.waveActive and len(self.enemies) == 0:
			self.waveActive = False
			self.coins += CoinsPerWave
			if self.wave >= MaxWaves:
				self.playing = False
				self.state = "upgrade"
			else:
				self.wave += 1
				self.startWave()

	def new(self):
		self.playing = True
		self.coins = 0
		self.wave = 1
		self.allSprites = CameraGroup(self)
		self.groundSprites = pygame.sprite.Group()
		self.enemies = pygame.sprite.Group()
		self.blocks = pygame.sprite.Group()
		self.bullets = pygame.sprite.Group()
		self.createLevel()

	def update(self):
		self.allSprites.update(self.dt)
		self.checkWaveStatus()

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
		self.drawHUD()
		pygame.display.update()

	def drawHUD(self):
		hudText = f"Wave {self.wave}/{MaxWaves}   Coins: {self.coins}"
		hudSurf = self.hudFont.render(hudText, True, "white")
		self.screen.blit(hudSurf, (10, 10))

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

	def upgradeMenu(self):
		font = pygame.font.SysFont(None, 48)
		while self.state == "upgrade" and self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
					self.state = None
				if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
					self.state = "menu"

			self.screen.fill("black")
			text = font.render(f"Upgrades (placeholder) - Coins: {self.coins} - press ESC to return to menu", True, "white")
			self.screen.blit(text, text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2)))
			pygame.display.update()
			self.clock.tick(60)

	def run(self):
		while self.running:
			if self.state == "menu":
				self.menu()
			elif self.state == "settings":
				self.settingsMenu()
			elif self.state == "upgrade":
				self.upgradeMenu()
			elif self.state == "playing":
				self.new()
				self.main()
			

g = Game()
g.run()

pygame.quit()
sys.exit()