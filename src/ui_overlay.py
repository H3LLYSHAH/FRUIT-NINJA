"""Utility functions for drawing HUD/UI on top of frames."""
from __future__ import annotations

from typing import Sequence, Tuple

import cv2
import numpy as np


Color = Tuple[int, int, int]
Point = Tuple[int, int]


def overlay_sprite(frame: np.ndarray, sprite: np.ndarray, center: Point, scale: float = 1.0) -> None:
    if sprite is None or sprite.size == 0:
        return

    h, w = sprite.shape[:2]
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    sprite_resized = cv2.resize(sprite, (new_w, new_h))

    x, y = center
    top_left_x = int(x - new_w / 2)
    top_left_y = int(y - new_h / 2)

    frame_h, frame_w = frame.shape[:2]
    x1 = max(0, top_left_x)
    y1 = max(0, top_left_y)
    x2 = min(frame_w, top_left_x + new_w)
    y2 = min(frame_h, top_left_y + new_h)

    sprite_h, sprite_w = sprite_resized.shape[:2]
    sprite_x1 = max(0, x1 - top_left_x)
    sprite_y1 = max(0, y1 - top_left_y)

    overlap_w = min(x2 - x1, sprite_w - sprite_x1)
    overlap_h = min(y2 - y1, sprite_h - sprite_y1)
    if overlap_w <= 0 or overlap_h <= 0:
        return

    x2 = x1 + overlap_w
    y2 = y1 + overlap_h
    sprite_x2 = sprite_x1 + overlap_w
    sprite_y2 = sprite_y1 + overlap_h

    roi = frame[y1:y2, x1:x2]
    sprite_roi = sprite_resized[sprite_y1:sprite_y2, sprite_x1:sprite_x2]
    if sprite_roi.shape[0] == 0 or sprite_roi.shape[1] == 0:
        return

    if sprite_roi.shape[2] == 4:
        alpha = sprite_roi[..., 3:] / 255.0
        roi[:] = (1 - alpha) * roi + alpha * sprite_roi[..., :3]
    else:
        roi[:] = sprite_roi


def draw_centered_banner(frame: np.ndarray, text: str, y_ratio: float, color: Color) -> None:
    h, w = frame.shape[:2]
    font = cv2.FONT_HERSHEY_PLAIN
    scale = 3
    thickness = 3
    text_size = cv2.getTextSize(text, font, scale, thickness)[0]
    x = (w - text_size[0]) // 2
    y = int(h * y_ratio)
    cv2.rectangle(
        frame,
        (x - 20, y - text_size[1] - 20),
        (x + text_size[0] + 20, y + 20),
        (0, 0, 0),
        -1,
    )
    cv2.putText(frame, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)


def draw_trail(frame: np.ndarray, points: Sequence[Point]) -> None:
    if len(points) < 2:
        return
    glow = np.zeros_like(frame)
    core = np.zeros_like(frame)
    total = len(points) - 1
    for i in range(1, len(points)):
        strength = i / total
        color = (
            int(80 + 175 * strength),
            int(180 + 60 * strength),
            20,
        )
        thickness = int(6 + 20 * strength)
        cv2.line(glow, points[i - 1], points[i], color, thickness, cv2.LINE_AA)
        cv2.line(core, points[i - 1], points[i], (255, 255, 255), max(2, thickness // 3), cv2.LINE_AA)
    glow = cv2.GaussianBlur(glow, (0, 0), 9)
    frame[:] = cv2.addWeighted(frame, 1.0, glow, 0.35, 0)
    frame[:] = cv2.addWeighted(frame, 1.0, core, 0.55, 0)


def draw_score_panel(frame: np.ndarray, score: int, best: int, level: int, combo: float) -> None:
    x, y = 20, 20
    w, h = 280, 130
    cv2.rectangle(frame, (x, y), (x + w, y + h), (25, 25, 25), -1)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (80, 50, 10), 2)
    cv2.putText(frame, f"Score {score:4d}", (x + 12, y + 40), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 215, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Best  {best:4d}", (x + 12, y + 70), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 215, 160), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Lvl {level:02d}", (x + 12, y + 104), cv2.FONT_HERSHEY_DUPLEX, 0.7, (120, 255, 120), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Combo {combo:.1f}x", (x + 120, y + 104), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 200, 90), 2, cv2.LINE_AA)


def draw_lives(frame: np.ndarray, lives: int, sprite: np.ndarray) -> None:
    if lives <= 0:
        return
    bar_w = lives * 64 + 40
    cv2.rectangle(frame, (frame.shape[1] - bar_w - 20, 20), (frame.shape[1] - 20, 100), (25, 25, 25), -1)
    cv2.rectangle(frame, (frame.shape[1] - bar_w - 20, 20), (frame.shape[1] - 20, 100), (80, 50, 10), 2)
    base_x = frame.shape[1] - bar_w + 10
    for i in range(lives):
        overlay_sprite(frame, sprite, (base_x + i * 64, 60), 0.55)

