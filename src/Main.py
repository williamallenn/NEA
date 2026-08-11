import pygame
import sys
import random
from sprites import *
from upgrades import *

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
		pygame.mouse.set_cursor(*pygame.cursors.broken_x)

		w, h = self.screen.get_size()
		self.playButton = Button("images/Play_button.png", w // 2, h // 2 + 20, scale=2.5)
		self.settingsButton = Button("images/Settings_button.png", w // 2, h // 2 + 160, scale=2.5)
		self.exitButton = Button("images/Exit_button.png", w // 2, h // 2 + 300, scale=2.5)
		self.upgradeTitleFont = pygame.font.SysFont(None, UpgradeTitleFontSize)
		self.upgradeBodyFont = pygame.font.SysFont(None, UpgradeBodyFontSize)
		self.gameOverTitleFont = pygame.font.SysFont(None, GameOverTitleFontSize)
		self.gameOverBodyFont = pygame.font.SysFont(None, GameOverBodyFontSize)
		self.upgradeMenuOpen = False
		self.weaponIcons = self.loadWeaponIcons()

	def loadWeaponIcons(self):
		icons = {}
		try:
			sheet = SpriteSheet(WeaponSpriteSheetPath, alpha=True)
		except (pygame.error, FileNotFoundError):
			return icons
		for key, (sprite_x, sprite_y) in WeaponIconSpriteCoords.items():
			icons[key] = sheet.getSprite(sprite_x, sprite_y, WeaponIconSize, WeaponIconSize)
		return icons

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
		self.weaponSprite = WeaponSprite(self, self.player)

		self.reachableTiles = getReachableTiles(self.validTiles, spawn)
		unreachable = set(self.validTiles) - self.reachableTiles
		if unreachable:
			print(f"Warning: {len(unreachable)} unreachable tile(s) in {self.map}: {sorted(unreachable)}")

		self.spawnEnemies(self.spawnCountForRound())

	def spawnCountForRound(self):
		return StartingEnemyCount + (self.roundNumber - 1) * EnemyCountPerRoundGrowth

	def spawnEnemies(self, count):
		spawnPool = list(self.reachableTiles) if self.reachableTiles else self.validTiles
		for i in range(count):
			x, y = random.choice(spawnPool)
			Enemy(self, x, y)

	def new(self):
		self.playing = True
		self.allSprites = CameraGroup(self)
		self.groundSprites = pygame.sprite.Group()
		self.enemies = pygame.sprite.Group()
		self.blocks = pygame.sprite.Group()
		self.bullets = pygame.sprite.Group()
		self.availableUpgradePool = createUpgradePool()
		self.roundNumber = 1
		self.roundTimeRemaining = RoundDurationSeconds
		self.upgradeMenuOpen = False
		self.upgradeCards = []
		self.createLevel()

	def update(self):
		self.allSprites.update(self.dt)
		if self.player.health <= 0:
			self.playing = False
			self.state = "gameover"

	def events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.playing = False
				self.running = False
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
				if not self.upgradeMenuOpen:
					self.player.switchWeapon()
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
				if self.upgradeMenuOpen:
					for card in self.upgradeCards:
						if card.clicked(event):
							self.chooseUpgrade(card)
							break
				else:
					self.player.shoot()

	def draw(self):
		self.allSprites.customDraw(self.player)
		self.drawHUD()
		self.drawWeaponHUD()
		if self.upgradeMenuOpen:
			self.drawUpgradeMenuOverlay()
		pygame.display.update()

	def drawHUD(self):
		money_surf = self.upgradeBodyFont.render(f"${self.player.money}", True, "white")
		self.screen.blit(money_surf, (HudPadding, HudPadding))
		health_surf = self.upgradeBodyFont.render(f"HP {self.player.health}/{self.player.max_health}", True, "white")
		self.screen.blit(health_surf, (HudPadding, HudPadding + money_surf.get_height() + 4))
		round_surf = self.upgradeBodyFont.render(f"Round {self.roundNumber} - {int(self.roundTimeRemaining)}s", True, "white")
		self.screen.blit(round_surf, (HudPadding, HudPadding + (money_surf.get_height() + 4) * 2))

	def drawWeaponHUD(self):
		weapon_keys = self.player.weapon_keys
		total_width = len(weapon_keys) * WeaponIconSize + (len(weapon_keys) - 1) * WeaponIconSpacing
		w, h = self.screen.get_size()
		start_x = w - total_width - HudPadding
		for i, key in enumerate(weapon_keys):
			weapon = WeaponData[key]
			rect = pygame.Rect(start_x + i * (WeaponIconSize + WeaponIconSpacing), HudPadding, WeaponIconSize, WeaponIconSize)
			icon = self.weaponIcons.get(key)
			if icon is not None:
				self.screen.blit(icon, rect)
			else:
				pygame.draw.rect(self.screen, weapon["colour"], rect, border_radius=WeaponIconCornerRadius)
				label_surf = self.upgradeBodyFont.render(key[:1].upper(), True, "black")
				self.screen.blit(label_surf, label_surf.get_rect(center=rect.center))
			border_colour = "white" if i == self.player.weapon_index else "#444444"
			pygame.draw.rect(self.screen, border_colour, rect, width=3, border_radius=WeaponIconCornerRadius)

	def drawUpgradeMenuOverlay(self):
		overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
		overlay.fill((0, 0, 0, UpgradeOverlayAlpha))
		self.screen.blit(overlay, (0, 0))
		mouse_pos = pygame.mouse.get_pos()
		for card in self.upgradeCards:
			card.update(mouse_pos)
			card.draw(self.screen, self.upgradeTitleFont, self.upgradeBodyFont)

	def drawUpgradeCards(self):
		if len(self.availableUpgradePool) < UpgradeCardsPerRound:
			self.availableUpgradePool = createUpgradePool()
		return random.sample(self.availableUpgradePool, UpgradeCardsPerRound)

	def layoutUpgradeCards(self, cards):
		w, h = self.screen.get_size()
		card_count = len(cards)
		total_width = card_count * UpgradeCardWidth + (card_count - 1) * UpgradeCardSpacing
		start_x = (w - total_width) // 2
		y = (h - UpgradeCardHeight) // 2
		self.upgradeCards = [
			UpgradeCard(upgrade, start_x + i * (UpgradeCardWidth + UpgradeCardSpacing), y, UpgradeCardAccentColours[i % len(UpgradeCardAccentColours)])
			for i, upgrade in enumerate(cards)
		]

	def startRoundEnd(self):
		for enemy in list(self.enemies):
			enemy.kill()
		self.upgradeMenuOpen = True
		self.layoutUpgradeCards(self.drawUpgradeCards())

	def chooseUpgrade(self, card):
		card.upgrade.apply_effect(self.player)
		self.player.chosen_upgrades.append(card.upgrade.name)
		if card.upgrade in self.availableUpgradePool:
			self.availableUpgradePool.remove(card.upgrade)
		self.upgradeMenuOpen = False
		self.roundNumber += 1
		self.roundTimeRemaining = RoundDurationSeconds
		self.spawnEnemies(self.spawnCountForRound())

	def main(self):
		while self.playing:
			self.dt = self.clock.tick(120) / 1000
			self.events()
			if not self.upgradeMenuOpen:
				self.update()
				self.roundTimeRemaining -= self.dt
				if self.roundTimeRemaining <= 0:
					self.startRoundEnd()
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

	def drawGameOverScreen(self):
		self.screen.fill("black")
		w, h = self.screen.get_size()

		title_surf = self.gameOverTitleFont.render("Game Over", True, "white")
		self.screen.blit(title_surf, title_surf.get_rect(midtop=(w // 2, GameOverTopMargin)))

		round_surf = self.gameOverBodyFont.render(f"You reached round {self.roundNumber}", True, "white")
		self.screen.blit(round_surf, round_surf.get_rect(midtop=(w // 2, GameOverTopMargin + title_surf.get_height() + GameOverLineSpacing)))

		list_top = GameOverTopMargin + title_surf.get_height() + GameOverLineSpacing * 2 + round_surf.get_height()
		if self.player.chosen_upgrades:
			heading_surf = self.gameOverBodyFont.render("Upgrades collected:", True, "white")
			self.screen.blit(heading_surf, heading_surf.get_rect(midtop=(w // 2, list_top)))
			for i, name in enumerate(self.player.chosen_upgrades):
				line_surf = self.gameOverBodyFont.render(name, True, "#63A375")
				line_y = list_top + heading_surf.get_height() + GameOverLineSpacing + i * GameOverLineSpacing
				self.screen.blit(line_surf, line_surf.get_rect(midtop=(w // 2, line_y)))
		else:
			none_surf = self.gameOverBodyFont.render("No upgrades collected", True, "white")
			self.screen.blit(none_surf, none_surf.get_rect(midtop=(w // 2, list_top)))

		prompt_surf = self.gameOverBodyFont.render("Press SPACE to return to menu", True, "white")
		self.screen.blit(prompt_surf, prompt_surf.get_rect(midbottom=(w // 2, h - GameOverTopMargin // 2)))

	def gameOver(self):
		while self.state == "gameover" and self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
					self.state = None
				if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
					self.state = "menu"

			self.drawGameOverScreen()
			pygame.display.update()
			self.clock.tick(60)

	def run(self):
		while self.running:
			if self.state == "menu":
				self.menu()
			elif self.state == "settings":
				self.settingsMenu()
			elif self.state == "gameover":
				self.gameOver()
			elif self.state == "playing":
				self.new()
				self.main()

g = Game()
g.run()

pygame.quit()
sys.exit()