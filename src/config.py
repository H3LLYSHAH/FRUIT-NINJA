"""Shared configuration flags for the Fruit Ninja style webcam game."""
from pathlib import Path

# Camera and window config
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
WINDOW_NAME = "AI Fruit Ninja"
TARGET_FPS = 60

# Gameplay tuning
INITIAL_SPAWN_INTERVAL = 1.15  # seconds
MIN_SPAWN_INTERVAL = 0.28
SPAWN_ACCELERATION = 0.017  # faster spawns per point
GRAVITY = 1850.0  # pixels / s^2
FRUIT_MIN_RADIUS = 42
FRUIT_MAX_RADIUS = 86
MIN_THROW_SPEED = 1250
MAX_THROW_SPEED = 1650
SLICE_SPEED_THRESHOLD = 900  # pixels / s
STARTING_LIVES = 3
BOMB_INSTANT_FAIL = True
COMBO_WINDOW = 1.1
MAX_COMBO = 4.5
TRAIL_HISTORY = 18

# Asset handling
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = PROJECT_ROOT / "assets"

# Fruit catalog contains (sprite name, size scale, score value)
FRUIT_CATALOG = [
	("apple.png", 0.85, 11),
	("banana.png", 0.95, 10),
	("grapes.png", 0.85, 12),
	("watermelon.png", 1.25, 15),
	("strawberry.png", 0.8, 13),
	("pineapple.png", 1.35, 16),
	("orange.png", 0.9, 9),
	("peach.png", 0.95, 12),
	("cherries.png", 0.75, 11),
	("mango.png", 1.0, 14),
	("kiwi.png", 0.8, 11),
	("pear.png", 0.95, 10),
	("lemon.png", 0.85, 9),
	("melon.png", 1.15, 14),
	("blueberries.png", 0.75, 13),
]
BOMB_PROBABILITY_BASE = 0.03
BOMB_PROBABILITY_GAIN = 0.002
BOMB_PROBABILITY_CAP = 0.2
