import pygame
import sys

class SpriteSheet:
	def __init__(self, file):
		self.sheet = pygame.image.load(file).convert()

	def getSprite(self, x, y, width, height):
		sprite = pygame.Surface([width, height])
		sprite.blit(self.sheet, (0, 0), (x, y, width, height))
		return sprite


class CameraGroup(pygame.sprite.Group):
	def __init__(self, game):
		super().__init__()
		self.game = game
		self.display_surface = game.screen
		self.offset = pygame.math.Vector2()
		self.half_w = self.display_surface.get_size()[0] // 2
		self.half_h = self.display_surface.get_size()[1] // 2

	def center_target_camera(self, target):
		self.offset.x = target.rect.centerx - self.half_w
		self.offset.y = target.rect.centery - self.half_h

	def customDraw(self, player):
		self.center_target_camera(player)
		self.display_surface.fill("#73D8E7")
  
		for sprite in self.game.groundSprites:
			offset_pos = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image, offset_pos)

		for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
			offset_pos = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image, offset_pos)


class Player(pygame.sprite.Sprite):
	def __init__(self, game, x, y):

		self.game = game
		self.groups = game.allSprites
		pygame.sprite.Sprite.__init__(self, game.allSprites)
		self.x = x * 32
		self.y = y * 32
		self.direction = pygame.math.Vector2()
		self.width = 32
		self.height = 32
		self.looking = "down"
		self.image = pygame.Surface([self.width, self.height])
		self.image.blit(pygame.image.load(r"C:\Users\flapb\OneDrive - Spencer Academies Trust\comp sci\NEA\coding\images\Player1.png"), (0, 0))
		self.rect = self.image.get_rect()
		self.rect.x = self.x
		self.rect.y = self.y
		self.health = 10
		self.speed = 200  
		self.attack_cooldown = 400
		self.last_attack_time = 0

	def move(self):
		Key = pygame.key.get_pressed()
		self.direction.x = 0
		self.direction.y = 0
		if Key[pygame.K_w]:
			self.direction.y = -1
			self.looking = "up"
		if Key[pygame.K_s]:
			self.direction.y = 1
			self.looking = "down"
		if Key[pygame.K_a]:
			self.direction.x = -1
			self.looking = "left"
		if Key[pygame.K_d]:
			self.direction.x = 1
			self.looking = "right"
		if Key[pygame.K_ESCAPE]:
			self.game.playing = False
			self.game.running = False
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()

	def shoot(self):
		now = pygame.time.get_ticks()
		if now - self.last_attack_time >= self.attack_cooldown:
			Bullet(self.game, self)
			self.last_attack_time = now

	def collideWBlocks(self, direction):
		if direction == 'x':
			Hit = pygame.sprite.spritecollide(self, self.game.blocks, False)
			if Hit:
				if self.direction.x > 0:
					self.rect.x = Hit[0].rect.left - self.rect.width
				if self.direction.x < 0:
					self.rect.x = Hit[0].rect.right
		if direction == 'y':
			Hit = pygame.sprite.spritecollide(self, self.game.blocks, False)
			if Hit:
				if self.direction.y > 0:
					self.rect.y = Hit[0].rect.top - self.rect.height
				if self.direction.y < 0:
					self.rect.y = Hit[0].rect.bottom

	def collideWEnemies(self, direction):
		if direction == 'x':
			Hit = pygame.sprite.spritecollide(self, self.game.enemies, False)
			if Hit:
				if self.direction.x > 0:
					self.rect.x = Hit[0].rect.left - self.rect.width
				if self.direction.x < 0:
					self.rect.x = Hit[0].rect.right
				self.takeDamage()
		if direction == 'y':
			Hit = pygame.sprite.spritecollide(self, self.game.enemies, False)
			if Hit:
				if self.direction.y > 0:
					self.rect.y = Hit[0].rect.top - self.rect.height
				if self.direction.y < 0:
					self.rect.y = Hit[0].rect.bottom
				self.takeDamage()

	def takeDamage(self):
		now = pygame.time.get_ticks()
		if not hasattr(self, "last_hit_time"):
			self.last_hit_time = 0
		if now - self.last_hit_time >= 500:
			self.health -= 1
			self.last_hit_time = now

	def update(self, dt):
		self.move()
		self.rect.x += self.direction.x * self.speed * dt
		self.collideWBlocks('x')
		self.collideWEnemies('x')
		self.rect.y += self.direction.y * self.speed * dt
		self.collideWBlocks('y')
		self.collideWEnemies('y')

class Enemy(Player):
	def __init__(self, game, x, y):
		self.groups = game.allSprites, game.enemies
		super().__init__(game, x, y)
		pygame.sprite.Sprite.__init__(self, self.groups)
		self.image.fill("red")
		self.speed = 90
		self.health = 3
		self.rect.x = self.x
		self.rect.y = self.y

	def move(self):
		self.direction.x = 0
		self.direction.y = 0

		if self.rect.x < self.game.player.rect.x:
			self.direction.x = 1
			self.looking = "right"
		elif self.rect.x > self.game.player.rect.x:
			self.direction.x = -1
			self.looking = "left"

		if self.rect.y < self.game.player.rect.y:
			self.direction.y = 1
			self.looking = "down"
		elif self.rect.y > self.game.player.rect.y:
			self.direction.y = -1
			self.looking = "up"

		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()

	def collideWEnemies(self, direction):
		return super().collideWEnemies(direction)
	def collideWBlocks(self, direction):
		return super().collideWBlocks(direction)
	def update(self, dt):
		return super().update(dt)

class Block(pygame.sprite.Sprite):
	def __init__(self, game, x, y):

		self.game = game
		self.groups = game.groundSprites, game.blocks
		pygame.sprite.Sprite.__init__(self, self.groups)
		self.x = x * 32
		self.y = y * 32
		self.width = 32
		self.height = 32
		self.image = pygame.Surface([self.width, self.height])
		self.image.fill("black")
		self.rect = self.image.get_rect()
		self.rect.x = self.x
		self.rect.y = self.y

class Ground(pygame.sprite.Sprite):
	def __init__(self, game, x, y):
		self.game = game
		self.groups = game.groundSprites
		pygame.sprite.Sprite.__init__(self, self.groups)
		self.x = x * 32
		self.y = y * 32
		self.width = 32
		self.height = 32
		self.image = self.game.GroundSpriteSheet.getSprite(160, 32, self.width, self.height)
		self.rect = self.image.get_rect()
		self.rect.x = self.x
		self.rect.y = self.y

class Grass(Ground):
	def __init__(self, game, x, y):
		super().__init__(game, x, y)
		self.image = self.game.GroundSpriteSheet.getSprite(160, 128, self.width, self.height)

class Bullet(pygame.sprite.Sprite):
	def __init__(self, game, player):
		self.game = game
		self.groups = game.allSprites, game.bullets
		pygame.sprite.Sprite.__init__(self, self.groups)

		self.image = pygame.Surface((8, 8))
		self.image.fill("yellow")
		player_screen_pos = pygame.math.Vector2(player.rect.center) - self.game.allSprites.offset
		mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
		direction_vector = mouse_pos - player_screen_pos

		if direction_vector.length() > 0:
			self.direction = direction_vector.normalize()
		else:
			self.direction = pygame.math.Vector2(0, -1)
		spawn = pygame.math.Vector2(player.rect.center) + self.direction * 20
		self.rect = self.image.get_rect(center=spawn)

		self.speed = 400  
		self.spawnTime = pygame.time.get_ticks()
		self.lifetime = 1000  

	def checkHit(self):
		hitEnemies = pygame.sprite.spritecollide(self, self.game.enemies, False)
		for enemy in hitEnemies:
			enemy.health -= 1
			self.kill()
			if enemy.health <= 0:
				enemy.kill()
			break

	def update(self, dt):
		self.rect.x += self.direction.x * self.speed * dt
		self.rect.y += self.direction.y * self.speed * dt
		self.checkHit()
		if pygame.time.get_ticks() - self.spawnTime > self.lifetime:
			self.kill()
        