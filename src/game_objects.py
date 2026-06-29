"""Game entities and physics helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np

from . import config


@dataclass
class Fruit:
    kind: str
    position: np.ndarray
    velocity: np.ndarray
    radius: float
    sprite_name: str
    born_at: float
    value: int
    sliced_at: float | None = None
    removed: bool = False

    def is_bomb(self) -> bool:
        return self.kind == "bomb"

    def time_alive(self, now: float) -> float:
        return now - self.born_at

    def mark_sliced(self, timestamp: float) -> None:
        self.sliced_at = timestamp


@dataclass
class Splash:
    position: Tuple[int, int]
    color: Tuple[int, int, int]
    born_at: float
    duration: float = 0.4

    def alpha(self, now: float) -> float:
        progress = (now - self.born_at) / self.duration
        return max(0.0, 1.0 - progress)


def spawn_fruit(width: int, height: int, score: int, rng: np.random.Generator, now: float) -> Fruit:
    bomb_chance = min(
        config.BOMB_PROBABILITY_CAP,
        config.BOMB_PROBABILITY_BASE + score * config.BOMB_PROBABILITY_GAIN,
    )
    is_bomb = rng.random() < bomb_chance

    if is_bomb:
        sprite_name = "bomb.png"
        size_scale = 1.1
        value = 0
        kind = "bomb"
    else:
        sprite_name, size_scale, value = config.FRUIT_CATALOG[
            rng.integers(len(config.FRUIT_CATALOG))
        ]
        kind = "fruit"

    radius = rng.uniform(config.FRUIT_MIN_RADIUS, config.FRUIT_MAX_RADIUS) * size_scale

    x = rng.uniform(radius, width - radius)
    # keep the spawn just beneath the frame so it always becomes visible
    y = height + radius + rng.uniform(5, 30)
    apex = rng.uniform(height * 0.15, height * 0.4)
    vertical_distance = max(90.0, y - apex)
    vy = -np.sqrt(2 * config.GRAVITY * vertical_distance) * rng.uniform(0.92, 1.05)
    vx = rng.uniform(-320, 320) * (1 + score * 0.003)

    return Fruit(
        kind=kind,
        position=np.array([x, y], dtype=np.float32),
        velocity=np.array([vx, vy], dtype=np.float32),
        radius=radius,
        sprite_name=sprite_name,
        born_at=now,
        value=int(value),
    )
