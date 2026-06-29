"""Run the webcam powered Fruit Ninja experience on the Web via Streamlit."""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Tuple

import cv2
import numpy as np
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# Relative imports changed to direct imports for Streamlit root execution
import config
from asset_utils import AssetManager
from game_objects import Fruit, Splash, spawn_fruit
from hand_tracker import HandLandmark, HandTracker
from ui_overlay import draw_centered_banner, draw_lives, draw_score_panel, draw_trail, overlay_sprite


@dataclass
class FloatingText:
    text: str
    position: np.ndarray
    color: Tuple[int, int, int]
    born_at: float
    duration: float = 1.0

    def alpha(self, now: float) -> float:
        progress = (now - self.born_at) / self.duration
        return max(0.0, 1.0 - progress)


class StreamlitFruitNinjaProcessor(VideoTransformerBase):
    def __init__(self) -> None:
        # Initialize assets and trackers inside the state container
        self.hand_tracker = HandTracker()
        self.assets = AssetManager()
        self.rng = np.random.default_rng()

        self.fruits: List[Fruit] = []
        self.splashes: List[Splash] = []
        self.finger_history: Deque[Tuple[int, int, float]] = deque(maxlen=config.TRAIL_HISTORY)

        self.last_frame_time = time.perf_counter()
        self.last_spawn_time = self.last_frame_time

        self.score = 0
        self.best_score = 0
        self.combo = 1.0
        self.combo_chain = 0
        self.last_slice_time = 0.0
        self.lives = config.STARTING_LIVES
        self.game_over = False
        self.popups: List[FloatingText] = []

    def transform(self, frame):
        """Processes each frame sent from the user's browser webcam."""
        # Convert incoming WebRTC frame to NumPy array for OpenCV processing
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        
        now = time.perf_counter()
        dt = min(now - self.last_frame_time, 1 / 30)
        self.last_frame_time = now

        # Track hand landmarks from frame
        landmark = self.hand_tracker.locate_index_finger(img)
        self._update_finger_path(landmark, now)

        # Process Game State Mechanics
        if not self.game_over:
            self._spawn_if_needed(now, img.shape[1], img.shape[0])
            self._update_fruits(dt, now, img.shape[1], img.shape[0])
            self._detect_slices(now)

        # Render background and interactive UI directly onto the image matrix
        self._render_scene(img, landmark)

        # Check for reset trigger via a Streamlit session button check workaround or automation
        if self.game_over and st.session_state.get("reset_game", False):
            self._reset_state()
            st.session_state["reset_game"] = False

        return img

    def _reset_state(self) -> None:
        self.fruits.clear()
        self.splashes.clear()
        self.finger_history.clear()
        self.score = 0
        self.combo = 1.0
        self.combo_chain = 0
        self.last_slice_time = 0.0
        self.lives = config.STARTING_LIVES
        self.game_over = False
        self.last_spawn_time = time.perf_counter()
        self.popups.clear()

    def _spawn_if_needed(self, now: float, width: int, height: int) -> None:
        interval = max(
            config.MIN_SPAWN_INTERVAL,
            config.INITIAL_SPAWN_INTERVAL - self.score * config.SPAWN_ACCELERATION,
        )
        while now - self.last_spawn_time >= interval:
            self.fruits.append(spawn_fruit(width, height, self.score, self.rng, now))
            self.last_spawn_time += interval

    def _update_fruits(self, dt: float, now: float, width: int, height: int) -> None:
        for fruit in self.fruits:
            fruit.velocity[1] += config.GRAVITY * dt
            fruit.position += fruit.velocity * dt
            if fruit.sliced_at and now - fruit.sliced_at > 0.6:
                fruit.removed = True
            if fruit.position[1] - fruit.radius > height + fruit.radius:
                fruit.removed = True
                if not fruit.is_bomb() and fruit.sliced_at is None:
                    self._register_miss()
        self.fruits = [f for f in self.fruits if not f.removed]
        self._prune_splashes(now)
        self._prune_popups(now)

    def _register_miss(self) -> None:
        self.lives -= 1
        self.combo = 1.0
        if self.lives <= 0:
            self.game_over = True

    def _detect_slices(self, now: float) -> None:
        if len(self.finger_history) < 2:
            return
        history = list(self.finger_history)
        for fruit in self.fruits:
            if fruit.sliced_at is not None:
                continue
            for i in range(len(history) - 1):
                (x1, y1, t1) = history[i]
                (x2, y2, t2) = history[i + 1]
                dt = t2 - t1
                if dt <= 0:
                    continue
                speed = np.linalg.norm([x2 - x1, y2 - y1]) / dt
                if speed < config.SLICE_SPEED_THRESHOLD:
                    continue
                distance = _distance_point_to_segment(
                    fruit.position,
                    np.array([x1, y1], dtype=np.float32),
                    np.array([x2, y2], dtype=np.float32),
                )
                if distance <= fruit.radius * 0.85:
                    self._slice_fruit(fruit, now)
                    break

    def _slice_fruit(self, fruit: Fruit, timestamp: float) -> None:
        fruit.mark_sliced(timestamp)
        color = (0, 255, 0) if not fruit.is_bomb() else (0, 0, 255)
        self.splashes.append(
            Splash(position=tuple(fruit.position.astype(int)), color=color, born_at=timestamp)
        )
        if fruit.is_bomb():
            self.popups.append(
                FloatingText("BOMB!", fruit.position.copy(), (0, 0, 255), timestamp, duration=1.2)
            )
            self.combo = 1.0
            self.combo_chain = 0
            if config.BOMB_INSTANT_FAIL:
                self.lives = 0
                self.game_over = True
            else:
                self.lives = max(0, self.lives - 2)
            return

        if timestamp - self.last_slice_time < config.COMBO_WINDOW:
            self.combo = min(config.MAX_COMBO, self.combo + 0.35)
            self.combo_chain += 1
        else:
            self.combo = 1.0
            self.combo_chain = 1
        self.last_slice_time = timestamp
        points = int(fruit.value * self.combo)
        self.score += points
        self.best_score = max(self.best_score, self.score)
        self.popups.append(
            FloatingText(f"+{points}", fruit.position.copy(), (255, 215, 0), timestamp)
        )
        if self.combo_chain >= 3:
            self.popups.append(
                FloatingText(
                    f"{self.combo_chain} FRUIT COMBO!",
                    fruit.position.copy() - np.array([0, 60]),
                    (255, 180, 80),
                    timestamp,
                    duration=1.3,
                )
            )

    def _update_finger_path(self, landmark: HandLandmark | None, timestamp: float) -> None:
        if landmark is None:
            self.finger_history.clear()
            return
        x, y = landmark.point
        self.finger_history.append((x, y, timestamp))

    def _prune_splashes(self, now: float) -> None:
        self.splashes = [s for s in self.splashes if s.alpha(now) > 0.05]

    def _prune_popups(self, now: float) -> None:
        self.popups = [p for p in self.popups if p.alpha(now) > 0.05]

    def _render_scene(self, frame, landmark: HandLandmark | None) -> None:
        for fruit in self.fruits:
            sprite = self.assets.get(fruit.sprite_name)
            scale = (fruit.radius * 2) / sprite.shape[0]
            overlay_sprite(frame, sprite, tuple(fruit.position.astype(int)), scale)
            if fruit.is_bomb():
                cv2.circle(frame, tuple(fruit.position.astype(int)), int(fruit.radius * 1.1), (0, 0, 255), 2)

        points = [(x, y) for x, y, _ in self.finger_history]
        draw_trail(frame, points)

        now = time.perf_counter()
        for splash in self.splashes:
            alpha = splash.alpha(now)
            if alpha <= 0:
                continue
            radius = int(80 * alpha + 15)
            cv2.circle(frame, splash.position, radius, splash.color, thickness=6)

        self._render_popups(frame, now)

        level = 1 + self.score // 40
        draw_score_panel(frame, self.score, self.best_score, level, self.combo)
        draw_lives(frame, self.lives, self.assets.get("life.png"))

        if landmark:
            cv2.circle(frame, landmark.point, 12, (255, 255, 255), 2)

        if self.game_over:
            draw_centered_banner(frame, "Game Over!", 0.4, (0, 0, 255))


    def _render_popups(self, frame: np.ndarray, now: float) -> None:
        font = cv2.FONT_HERSHEY_DUPLEX
        for popup in self.popups:
            alpha = popup.alpha(now)
            if alpha <= 0:
                continue
            color = tuple(int(channel * alpha) for channel in popup.color)
            pos = (
                int(popup.position[0]),
                int(popup.position[1] - 60 * (1 - alpha)),
            )
            cv2.putText(frame, popup.text, pos, font, 1.1, color, 2, cv2.LINE_AA)


def _distance_point_to_segment(point: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
    ab = b - a
    if np.allclose(ab, 0):
        return float(np.linalg.norm(point - a))
    t = np.clip(np.dot(point - a, ab) / np.dot(ab, ab), 0.0, 1.0)
    projection = a + t * ab
    return float(np.linalg.norm(point - projection))


def main() -> None:
    st.set_page_config(page_title="Webcam Fruit Ninja", layout="centered")
    st.title("Webcam Fruit Ninja 🥷")
    st.markdown("Allow camera access and wave your index finger to slice!")

    # Instantiates layout button to restart the game state wrapper cleanly
    if st.button("Restart Game"):
        st.session_state["reset_game"] = True

    webrtc_streamer(
        key="fruit-ninja",
        video_transformer_factory=StreamlitFruitNinjaProcessor,
        async_processing=True
    )


if __name__ == "__main__":
    main()
