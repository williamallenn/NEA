import pygame
import sys
import random
from settings import *

class SpriteSheet:
	def __init__(self, file, alpha=False):
		self.alpha = alpha
		if alpha:
			self.sheet = pygame.image.load(file).convert_alpha()
		else:
			self.sheet = pygame.image.load(file).convert()

	def getSprite(self, x, y, width, height):
		if self.alpha:
			sprite = pygame.Surface([width, height], pygame.SRCALPHA)
		else:
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
			image_rect = sprite.image.get_rect(center=sprite.rect.center)
			offset_pos = image_rect.topleft - self.offset
			self.display_surface.blit(sprite.image, offset_pos)


class Player(pygame.sprite.Sprite):
	def __init__(self, game, x, y):

		self.game = game
		self.groups = game.allSprites
		pygame.sprite.Sprite.__init__(self, game.allSprites)
		self.x = x * TileSize
		self.y = y * TileSize
		self.direction = pygame.math.Vector2()
		self.width = TileSize
		self.height = TileSize
		self.looking = "down"
		sprite_scale = 2
		self.image = pygame.Surface([int(TileSize * sprite_scale)] * 2, pygame.SRCALPHA)
		playerImg = pygame.image.load("images/Player1.png").convert_alpha()
		playerImg = pygame.transform.scale(playerImg, self.image.get_size())
		self.image.blit(playerImg, (0, 0))
		self.rect = pygame.Rect(0, 0, self.width, self.height) 
		self.rect.x = self.x
		self.rect.y = self.y
		self.health = 10
		self.speed = 350 
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
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()

	def shoot(self):
		now = pygame.time.get_ticks()
		if now - self.last_attack_time >= self.attack_cooldown:
			mouse_screen_pos = pygame.mouse.get_pos()
			world_mouse_pos = pygame.math.Vector2(mouse_screen_pos) + self.game.allSprites.offset
			direction = world_mouse_pos - pygame.math.Vector2(self.rect.center)
			if direction.magnitude() != 0:
				direction = direction.normalize()
			Bullet(self.game, self, direction)
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

	def collideWEnemies(self):
		Hit = [s for s in pygame.sprite.spritecollide(self, self.game.enemies, False) if s is not self]
		if Hit:
			self.takeDamage()

	def collideWBullets(self):
			Hit = pygame.sprite.spritecollide(self, self.game.bullets, True)
			if Hit:
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
		self.rect.y += self.direction.y * self.speed * dt
		self.collideWBlocks('y')
		self.collideWEnemies()

class Enemy(Player):
	def __init__(self, game, x, y):
		super().__init__(game, x, y)
		self.groups = game.allSprites, game.enemies
		game.enemies.add(self)
		self.speed = 90
		self.health = 3
		self.rect = pygame.Rect(0, 0, self.width, self.height)
		self.rect.x = self.x
		self.rect.y = self.y
		sheet = game.ZombieSpriteSheet.sheet
		frame_count = 4
		frame_width = sheet.get_width() // frame_count
		frame_height = sheet.get_height()
		sprite_scale = 1.5
		img_size = int(TileSize * sprite_scale)

		self.frames = []
		for i in range(frame_count):
			frame = game.ZombieSpriteSheet.getSprite(i * frame_width, 0, frame_width, frame_height)
			frame = pygame.transform.scale(frame, (img_size, img_size))
			self.frames.append(frame)

		self.frame_index = 0
		self.animation_speed = 8 
		self.image = self.frames[0]

	def animate(self, dt):
		self.frame_index += self.animation_speed * dt
		if self.frame_index >= len(self.frames):
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]
  
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

	def collideWEnemies(self):
		pass

	def softCollideWEnemies(self, overlap_tolerance=8):
		Hit = [s for s in pygame.sprite.spritecollide(self, self.game.enemies, False) if s is not self]
		if not Hit:
			return
		push_x_total = 0
		push_y_total = 0

		for other in Hit:
			dx = self.rect.centerx - other.rect.centerx
			dy = self.rect.centery - other.rect.centery
			dist = (dx ** 2 + dy ** 2) ** 0.5
			min_dist = (self.rect.width / 2 + other.rect.width / 2) - overlap_tolerance
			if dist < min_dist and dist > 0:
				overlap = min_dist - dist
				push_x_total += (dx / dist) * overlap * 0.5
				push_y_total += (dy / dist) * overlap * 0.5
			elif dist == 0:
				push_x_total += random.uniform(-1, 1)
				push_y_total += random.uniform(-1, 1)

		self.rect.x += push_x_total
		self.rect.y += push_y_total

	def collideWBlocks(self, direction):
		return super().collideWBlocks(direction)
	def collideWBullets(self):
		return super().collideWBullets()
	def update(self, dt):
		super().update(dt)
		self.softCollideWEnemies()
		if self.direction.magnitude() != 0:
			self.animate(dt)

class Block(pygame.sprite.Sprite):
	def __init__(self, game, x, y):
		self.game = game
		self.groups = game.groundSprites, game.blocks
		pygame.sprite.Sprite.__init__(self, self.groups)
		self.x = x * TileSize
		self.y = y * TileSize
		self.width = TileSize
		self.height = TileSize
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
		self.x = x * TileSize
		self.y = y * TileSize
		self.width = TileSize
		self.height = TileSize
		self.image = self.game.GroundSpriteSheet.getSprite(0,768, self.width, self.height)
		self.rect = self.image.get_rect()
		self.rect.x = self.x
		self.rect.y = self.y

class Dirt(Ground):
	def __init__(self, game, x, y):
		super().__init__(game, x, y)
		self.image = self.game.GroundSpriteSheet.getSprite(64, 64, self.width, self.height)

class Water(Ground):
    def __init__(self,game,x,y):
        super().__init__(game,x,y)
        self.image = self.game.GroundSpriteSheet.getSprite(640,768,self.width,self.height)

class WaterTopLeft(Ground):
    def __init__(self,game,x,y):
        super().__init__(game,x,y)
        self.image = self.game.GroundSpriteSheet.getSprite(704,384,self.width,self.height)

class WaterLeft(Ground):
    def __init__(self,game,x,y):
        super().__init__(game,x,y)
        self.image = self.game.GroundSpriteSheet.getSprite(704,448,self.width,self.height)
        
class WaterTop(Ground):
    def __init__(self,game,x,y):
        super().__init__(game,x,y)
        self.image = self.game.GroundSpriteSheet.getSprite(768,384,self.width,self.height)
        
class WaterTopRight(Ground):
    def __init__(self,game,x,y):
        super().__init__(game,x,y)
        self.image = self.game.GroundSpriteSheet.getSprite(832,384,self.width,self.height)

class WaterRight(Ground):
    def __init__(self,game,x,y):
        super().__init__(game,x,y)
        self.image = self.game.GroundSpriteSheet.getSprite(832,448,self.width,self.height)

class Bullet(pygame.sprite.Sprite):
	def __init__(self, game, player, direction):
		self.game = game
		self.groups = game.allSprites, game.bullets
		pygame.sprite.Sprite.__init__(self, self.groups)
		self.image = pygame.Surface((16, 16))
		self.image.fill("yellow")
		self.direction = direction
		spawn = pygame.math.Vector2(player.rect.center) + self.direction * 20
		self.rect = self.image.get_rect(center=spawn)
		self.speed = 300 
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
   
	def update(self, dt):
		self.rect.x += self.direction.x * self.speed * dt
		self.rect.y += self.direction.y * self.speed * dt
		self.checkHit()
		if pygame.time.get_ticks() - self.spawnTime > self.lifetime:
			self.kill()

class Button:
	def __init__(self, image_path, x, y, scale=1.0):
		image = pygame.image.load(image_path).convert_alpha()
		width = int(image.get_width() * scale)
		height = int(image.get_height() * scale)
		self.image = pygame.transform.scale(image, (width, height))
		self.hover_image = pygame.transform.scale(self.image, (int(width * 1.08), int(height * 1.08)))
		self.rect = self.image.get_rect(center=(x, y))
		self.hovered = False

	def update(self, mouse_pos):
		self.hovered = self.rect.collidepoint(mouse_pos)

	def draw(self, surface):
		if self.hovered:
			img = self.hover_image
			rect = img.get_rect(center=self.rect.center)
		else:
			img = self.image
			rect = self.rect
		surface.blit(img, rect)

	def clicked(self, event):
		return (
			event.type == pygame.MOUSEBUTTONDOWN
			and event.button == 1
			and self.rect.collidepoint(event.pos)
		)