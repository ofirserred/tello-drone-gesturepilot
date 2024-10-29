# Tello Drone Gesture Control

This project allows you to control a Tello drone using hand gestures detected through a webcam. It utilizes the `djitellopy`, `OpenCV`, and `MediaPipe` libraries to process video feed, recognize gestures, and execute corresponding drone commands.

## Features

- **Gesture Recognition**: 
  - Take Off: Open all fingers
  - Land: Thumbs down
  - Flip Back: Thumbs up
  - Flip Left: Index finger left
  - Flip Right: Index finger right
  - Take Picture: All fingers closed

- **Live Camera Feed**: Stream video from the Tello drone's camera.

## Requirements

To run this project, you need to install the following Python packages:

- `djitellopy`
- `opencv-python`
- `mediapipe`
- `numpy`

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/tello-drone-gesturepilot.git
2. Navigate to the project directory:
   ```bash
   cd tello-drone-gesturepilot
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
## Usage
1. Ensure that your Tello drone is charged and powered on.
2. Connect your computer to the drone's Wi-Fi network.
3. Run the main script:
   ```bash
   python Project_Drone.py
4. Use the designated hand gestures to control the drone.
## Contributing
Feel free to submit issues or pull requests for improvements or bug fixes.
