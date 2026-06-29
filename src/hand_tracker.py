"""Hand tracking helper built on top of MediaPipe Hands."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import mediapipe as mp


@dataclass
class HandLandmark:
    point: Tuple[int, int]
    confidence: float


class HandTracker:
    """Detects the index fingertip position from a webcam frame."""

    def __init__(
        self,
        max_num_hands: int = 1,
        detection_confidence: float = 0.6,
        tracking_confidence: float = 0.6,
    ) -> None:
        self._hands = mp.solutions.hands.Hands(
            max_num_hands=max_num_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

    def locate_index_finger(self, frame) -> Optional[HandLandmark]:
        """Returns the fingertip pixel coordinate if a hand is present."""

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb_frame)
        if not results.multi_hand_landmarks:
            return None

        h, w = frame.shape[:2]
        land = results.multi_hand_landmarks[0].landmark[8]  # index tip
        cx, cy = int(land.x * w), int(land.y * h)
        return HandLandmark(point=(cx, cy), confidence=land.visibility)

    def close(self) -> None:
        self._hands.close()
