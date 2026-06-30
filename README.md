# FRUIT-NINJA
# Webcam Fruit Ninja

A touchless take on the classic Fruit Ninja experience that turns any webcam into a slicing arena. MediaPipe tracks your index finger in real time, OpenCV renders transparent PNG sprites over the camera feed, and a lightweight physics loop powers the fruit throws, gravity, bombs, and combo system.

## Features
- **Hand tracking:** MediaPipe Hands follows your index finger tip with sub-pixel smoothing.
- **Arcade physics:** Fruit fire out of the bottom of the frame, peak near the top, then crash back down with gravity and dynamic spawn speeds.
- **High-fidelity sprites:** Procedurally shaded watermelons, bananas, apples, oranges, pineapples, hearts, splashes, and bombs regenerated automatically whenever art updates ship.
- **Stylized HUD + trail:** Wood-tone HUD blocks, glowing combo popups, and a golden blade trail mimic the original Fruit Ninja presentation.
- **Combos + bombs:** Chaining slices inside the combo window ramps multipliers while nicking a bomb ends the round immediately.
- **Quick controls:** `Q` quits, `R` restarts after a game over.

## Getting Started
1. **Create a virtual environment (recommended).**
   ```powershell
   py -3 -m venv .venv
   .venv\Scripts\activate
   ```
2. **Install dependencies.**
   ```powershell
   pip install -r requirements.txt
   ```
3. **Run the game.** Use module mode so the relative imports resolve:
   ```powershell
   python -m src.main
   ```

## Fork & Import Instructions
Want to customize the slicer? Fork the project under your own account and sync it locally:
1. **Fork on GitHub.** Visit the original repo, click **Fork**, and keep the default options. This clones the code under your GitHub username.
2. **Clone your fork.**
   ```powershell
   git clone https://github.com/<your-username>/ninja-fruit.git
   cd ninja-fruit
   ```
3. **Add the upstream remote** so you can pull future updates from the source.
   ```powershell
   git remote add upstream https://github.com/tubakhxn/ninja-fruit.git
   ```
4. **Install deps & run** using the commands from the Getting Started section.
5. **Open in VS Code.** `code .` launches the workspace; use the Run/Debug panel if you prefer.

To contribute back, push a branch to your fork and open a pull request targeting `tubakhxn/ninja-fruit`.

## Gameplay Tips
- Keep the camera steady with good frontal lighting so MediaPipe sees your hand.
- Slice with fast, decisive motions. Slow drags will not cross the speed threshold.
- Bombs end the run when cut, so weave around their trajectories.
- Missed fruit chips away at the three-life pool. Staying in combo territory (≈1 second between slices) keeps the multiplier high.

## Project Structure
```
.
├── assets/              # Auto-generated PNG sprites (created on first run)
├── requirements.txt
├── README.md
└── src/
    ├── asset_utils.py   # Ensures sprites exist and loads them with alpha
    ├── config.py        # Tunable gameplay constants
    ├── game_objects.py  # Dataclasses + spawn helpers
    ├── hand_tracker.py  # MediaPipe wrapper for index-finger detection
    ├── ui_overlay.py    # HUD drawing helpers
    └── main.py          # Game loop, physics, UI, gesture detection
```

## Troubleshooting
- **Webcam not found:** adjust `CAMERA_INDEX` inside `src/config.py`.
- **Sluggish frame rate:** drop `CAMERA_WIDTH/HEIGHT` or lower `TARGET_FPS`.
- **Hand not detected:** make sure the full hand stays inside the frame; reduce detection thresholds in `HandTracker` if needed.
- **Old sprites showing:** delete the `assets/` folder or bump `ASSET_VERSION` in `src/asset_utils.py`; the generator will redraw every PNG on the next launch.
ls.
