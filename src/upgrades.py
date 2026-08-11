import pygame
from settings import *

class Upgrade:
	def __init__(self, name, description, apply_effect):
		self.name = name
		self.description = description
		self.apply_effect = apply_effect


def applyTwinShot(player):
	player.extra_bullets += 1

def applyPiercingRounds(player):
	player.bullet_pierce += PierceRoundsExtraPierce

def applyExplosiveRounds(player):
	player.explosive_rounds = True

def applyVampiricRounds(player):
	player.lifesteal_amount += VampiricHealAmount

def applyAdrenalineRush(player):
	player.speed += AdrenalineSpeedBoost

def applySecondWind(player):
	player.shield_charges += SecondWindShieldCharges

def applyOverclock(player):
	player.attack_cooldown *= OverclockCooldownMultiplier
	player.damage *= OverclockDamageMultiplier

def applyGlassCannon(player):
	player.damage *= GlassCannonDamageMultiplier
	player.max_health = max(1, player.max_health - GlassCannonHealthReduction)
	player.health = min(player.health, player.max_health)

def applyIronSkin(player):
	player.hit_invulnerability_ms += IronSkinInvulnerabilityBonusMs


def createUpgradePool():
	return [
		Upgrade("Twin Shot", "Fire an additional bullet in a spread", applyTwinShot),
		Upgrade("Piercing Rounds", "Bullets pass through an extra enemy", applyPiercingRounds),
		Upgrade("Explosive Rounds", "Bullets detonate, damaging nearby enemies", applyExplosiveRounds),
		Upgrade("Vampiric Rounds", "Killing an enemy restores health", applyVampiricRounds),
		Upgrade("Adrenaline Rush", "Move faster", applyAdrenalineRush),
		Upgrade("Second Wind", "Gain a shield that blocks the next hit", applySecondWind),
		Upgrade("Overclock", "Fire much faster but each shot is weaker", applyOverclock),
		Upgrade("Glass Cannon", "Deal far more damage but lose health", applyGlassCannon),
		Upgrade("Iron Skin", "Take hits less often", applyIronSkin),
	]


class UpgradeCard:
	def __init__(self, upgrade, x, y, accent_colour):
		self.upgrade = upgrade
		self.rect = pygame.Rect(x, y, UpgradeCardWidth, UpgradeCardHeight)
		self.accent_colour = accent_colour
		self.hovered = False

	def update(self, mouse_pos):
		self.hovered = self.rect.collidepoint(mouse_pos)

	def clicked(self, event):
		return (
			event.type == pygame.MOUSEBUTTONDOWN
			and event.button == 1
			and self.rect.collidepoint(event.pos)
		)

	def wrapText(self, text, font, max_width):
		words = text.split(" ")
		lines = []
		current_line = ""
		for word in words:
			test_line = f"{current_line} {word}".strip()
			if font.size(test_line)[0] <= max_width:
				current_line = test_line
			else:
				lines.append(current_line)
				current_line = word
		if current_line:
			lines.append(current_line)
		return lines

	def draw(self, surface, title_font, body_font):
		background_colour = self.accent_colour if self.hovered else "#2B2B3A"
		pygame.draw.rect(surface, background_colour, self.rect, border_radius=UpgradeCardCornerRadius)
		pygame.draw.rect(surface, self.accent_colour, self.rect, width=3, border_radius=UpgradeCardCornerRadius)

		title_surf = title_font.render(self.upgrade.name, True, "white")
		surface.blit(title_surf, title_surf.get_rect(midtop=(self.rect.centerx, self.rect.top + 20)))

		line_y = self.rect.top + 80
		for line in self.wrapText(self.upgrade.description, body_font, self.rect.width - 40):
			line_surf = body_font.render(line, True, "white")
			surface.blit(line_surf, line_surf.get_rect(midtop=(self.rect.centerx, line_y)))
			line_y += body_font.get_height()