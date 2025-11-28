# Augmented-Reality-for-Pothole-Detection-and-Route-Optimization-Using-Deep-Learning


# Pothole Detection Interface

Desktop application that uses a YOLO model to detect potholes in a live
camera feed and renders an adaptive driving corridor overlay. The app is
implemented in `workingcode.py` with Tkinter for UI controls and OpenCV /
PIL for video processing.

## Features
- Loads a trained YOLO model (`best.pt`) to detect potholes frame-by-frame.
- Highlights pothole bounding boxes and dims hazardous regions when the lane
  corridor intersects a detection.
- Provides fullscreen live video preview plus control panel for corridor width,
  perspective tilt, guideline reset, and camera cycling.

## Requirements
- Python 3.10+ (tested on Windows 10)
- GPU optional, CPU inference works at lower FPS
- Python packages:
  - `opencv-python`
  - `numpy`
  - `Pillow`
  - `ultralytics`
  - `tkinter` (bundled with standard Python on Windows)

Install dependencies with:
```bash
pip install opencv-python numpy Pillow ultralytics
```

## Usage
1. Place `best.pt` (trained YOLO weights) in the project root or update the
   path in `workingcode.py`.
2. Connect the desired camera(s). Edit `camera_index` if the default webcam is
   not at index 0.
3. Run the app:
   ```bash
   python workingcode.py
   ```
4. The window launches in fullscreen. Use `Alt+F4` or the in-app Quit button to
   exit.

## Controls
- `➡️ Widen Corridor` / `⬅️ Narrow Corridor`: adjust lane width.
- `⏫ Tilt Forward` / `⏬ Tilt Backward`: modify perspective height of the
  corridor.
- `🔄 Reset Guidelines`: reset tuning knobs to defaults.
- `🔄 Switch Camera`: cycle through camera indices 0-2.
- `❌ Quit`: release the camera and close the UI.

## Troubleshooting
- **Black screen / no video**: verify the camera index and ensure no other app
  is using the device.
- **Model load error**: confirm the absolute path to `best.pt` is correct and
  that the file is not blocked by Windows security.
- **Low FPS**: lower the capture resolution or use a GPU-enabled environment.

Feel free to adapt the UI layout, detection threshold, or camera selection
logic to suit your deployment scenario.
