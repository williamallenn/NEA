TileSize = 64

RoundDurationSeconds = 5
UpgradeCardsPerRound = 3
EnemyCountPerRoundGrowth = 2
StartingEnemyCount = 5

StartingMoney = 0
EnemyKillReward = 15

PlayerBaseDamage = 1
PlayerBaseHealth = 10
DefaultHitInvulnerabilityMs = 500

TwinShotAngleOffsetDegrees = 15
PierceRoundsExtraPierce = 1
ExplosiveRoundsRadius = 90
ExplosiveRoundsDamage = 1
VampiricHealAmount = 1
AdrenalineSpeedBoost = 60
SecondWindShieldCharges = 1
OverclockCooldownMultiplier = 0.5
OverclockDamageMultiplier = 0.7
GlassCannonDamageMultiplier = 1.8
GlassCannonHealthReduction = 3
IronSkinInvulnerabilityBonusMs = 300

UpgradeCardWidth = 280
UpgradeCardHeight = 340
UpgradeCardSpacing = 40
UpgradeCardCornerRadius = 12
UpgradeOverlayAlpha = 180
UpgradeTitleFontSize = 36
UpgradeBodyFontSize = 24
UpgradeCardAccentColours = ["#63A375", "#4C7093", "#A3673E"]
HudPadding = 20

GameOverTitleFontSize = 72
GameOverBodyFontSize = 30
GameOverLineSpacing = 40
GameOverTopMargin = 160

WeaponSwitchCooldownMs = 200
WeaponIconSize = 64
WeaponIconSpacing = 12
WeaponIconCornerRadius = 8
WeaponOrbitRadius = TileSize // 2
WeaponSpriteSheetPath = "images/weapon.png"

WeaponData = {
	"pistol": {"cooldown": 400, "damage_multiplier": 1.0, "bullet_count": 1, "bullet_speed": 300, "spread_degrees": 0, "colour": "#E8D44D"},
	"shotgun": {"cooldown": 700, "damage_multiplier": 0.6, "bullet_count": 4, "bullet_speed": 260, "spread_degrees": 12, "colour": "#E87A4D"},
	"smg": {"cooldown": 150, "damage_multiplier": 0.5, "bullet_count": 1, "bullet_speed": 340, "spread_degrees": 4, "colour": "#4DA6E8"},
}

WeaponIconSpriteCoords = {
	"pistol": (0, 0),
	"shotgun": (64, 0),
	"smg": (128, 0),
}

GroundSpriteCoords = {
	"ground": (0, 768),
	"dirt": (64, 64),
	"water": (640, 768),
	"water_top_left": (704, 384),
	"water_left": (704, 448),
	"water_top": (768, 384),
	"water_top_right": (832, 384),
	"water_right": (832, 448),
}
