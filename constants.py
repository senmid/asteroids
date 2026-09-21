SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
PLAYER_RADIUS = 20
LINE_WIDTH = 2
PLAYER_TURN_SPEED = 300
ASTEROID_MIN_RADIUS = 20
ASTEROID_KINDS = 3
ASTEROID_SPAWN_RATE_SECONDS = 0.8
ASTEROID_MAX_RADIUS = ASTEROID_MIN_RADIUS * ASTEROID_KINDS
SHOT_RADIUS = 5
SCORE_LARGE = 20
SCORE_MEDIUM = 50
SCORE_SMALL = 100
PLAYER_THRUST = 300
PLAYER_FRICTION = 0.99
PLAYER_MAX_SPEED = 500
PLAYER_BRAKE_FRICTION = 0.90
PLAYER_LIVES = 3
PLAYER_INVULN_SECONDS = 3.0
PLAYER_RESPAWN_CLEAR_RADIUS = 150
ASTEROID_SPIN_MIN = 20.0
ASTEROID_SPIN_MAX = 80.0
POWERUP_RADIUS = 12
POWERUP_LIFETIME_SECONDS = 8.0
POWERUP_DRIFT_SPEED = 40.0
POWERUP_DROP_CHANCE = 0.10
SPEED_BOOST_SECONDS = 6.0
SPEED_MULTIPLIER = 1.6
SHOT_WRAP_SECONDS = 8.0
SHOT_WRAP_LIFE_SECONDS = 2.0
FRICTION_DEFECT_SECONDS = 5.0
FRICTION_DEFECT_VALUE = 0.94
SHIELD_REGEN_PER_SECOND = 0.4
SHIELD_MAX_SECONDS = 5.0
SHIELD_PICKUP_SECONDS = 5.0
BOMB_DRAW_RADIUS = 10
BOMB_RADIUS = 250.0
BOMB_FUSE_SECONDS = 5.0
BOMB_COOLDOWN = 0.8
BOMBS_PER_LIFE = 3
BOMB_MAX_AMMO = 5
BOMB_INHERIT_VELOCITY = 0.35
BOMB_RING_LIFE = 0.28
BOMB_PICKUP_AMOUNT = 1
TITLE_TIMER = 5.3
VOICE_CHANNEL = 0
PICKUP_CHANNEL = 1
MUSIC_VOLUME = 0.3
MUSIC_DUCKED = 0.10
VOICE_VOLUME = 0.9
SFX_VOLUMES = {
    "shoot": 0.22,
    "explode_large": 0.20,
    "death": 0.40,
    "pickup": 0.35,
    "bomb_drop": 0.30,
    "bomb_boom": 0.40,
    "shield": 0.30,
}
POWERUP_KINDS = ("shield", "speed", "shot_wrap", "friction", "weapon", "bomb")
POWERUP_WEIGHTS = (22, 22, 12, 12, 16, 16)
WEAPON_NORMAL = "normal"
WEAPON_SPREAD = "spread"
WEAPON_HEAVY = "heavy"
WEAPON_BUFF_SECONDS = 6.0

WEAPONS = {
    WEAPON_NORMAL: {
        "cooldown": 0.22,
        "speed": 520,
        "radius": SHOT_RADIUS,
        "color": "white",
        "angles": (0,),
        "pierce": 1,
        "blast_radius": 0.0,
    },
    WEAPON_SPREAD: {
        "cooldown": 0.40,
        "speed": 450,
        "radius": 4,
        "color": "orange",
        "angles": (-15, 0, 15),
        "pierce": 1,
        "blast_radius": 0.0,
    },
    WEAPON_HEAVY: {
        "cooldown": 0.85,
        "speed": 380,
        "radius": 10,
        "color": "gold",
        "angles": (0,),
        "pierce": 2,
        "blast_radius": 55.0,
    },
}

WEAPON_BUFFS = {
    WEAPON_NORMAL: {
        "cooldown": 0.10,
        "radius": 7,
        "color": "cyan",
    },
    WEAPON_SPREAD: {
        "cooldown": 0.32,
        "angles": (-30, -15, 0, 15, 30),
        "color": "orange",
    },
    WEAPON_HEAVY: {
        "pierce": 4,
        "blast_radius": 95.0,
        "color": "red",
    },
}
