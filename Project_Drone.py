from djitellopy import Tello
import cv2
import mediapipe as mp
import time

thumb_up_counter = thumb_down_counter = index_up_counter = index_down_counter = index_left_counter = index_right_counter = fingers_closed_counter = fingers_open_counter = 0
threshold = 30  # Number of frames needed to confirm a gesture
drone_is_down = True
image_folder = "Drone_images"

mp_hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=1,
                                    min_detection_confidence=0.5)  # Use mediapipe model to detect hands
mp_draw = mp.solutions.drawing_utils  # Draw dots on the joints detected
mp_connect = mp.solutions.hands.HAND_CONNECTIONS  # Draw lines between the detected joints


def hand_gestures(frame):
    global thumb_up_counter, thumb_down_counter, index_left_counter, index_right_counter, fingers_closed_counter, fingers_open_counter, drone_is_down, drone_is_down

    frame = cv2.flip(frame, 1)  # Flipping the camera for the model to recognize the hand gestures
    results = mp_hands.process(frame)  # Process the given frame by using media pipe

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_connect)  # Draw lines between joints
            landmarks = [(lm.x, lm.y) for lm in hand_landmarks.landmark]  # Extract Landmarks coordinates

            thumb_tip_y = landmarks[4][1]  # Get thumb tip Y coordinates
            index_tip_x = landmarks[8][0]  # Get index tip X coordinates

            other_landmarks_y_thumb = [landmark[1] for id, landmark in enumerate(landmarks) if
                                       id != 4]  # Differentiate between other joints and thumb tip joint
            other_landmarks_x_index = [landmark[0] for id, landmark in enumerate(landmarks) if
                                       id != 8]  # Differentiate between other joints and index tip joint

            thumb_up = all(
                thumb_tip_y < y for y in other_landmarks_y_thumb)  # Demonstrate Thumbs up value where tip is above all
            thumb_down = all(thumb_tip_y > y for y in
                             other_landmarks_y_thumb)  # Demonstrate Thumbs down value where tip is below all
            index_left = all(index_tip_x < x for x in
                             other_landmarks_x_index)  # Demonstrate index left value where tip is left from all
            index_right = all(index_tip_x > x for x in
                              other_landmarks_x_index)  # Demonstrate index right value where tip is right from all

            # Demonstrate all fingers open where all joints above each other
            fingers_open = (landmarks[8][1] < landmarks[6][1] and  # Index
                            landmarks[12][1] < landmarks[10][1] and  # Middle
                            landmarks[16][1] < landmarks[14][1] and  # Ring
                            landmarks[20][1] < landmarks[18][1])  # Pinky

            # Demonstrate all fingers closed where all joints below each other
            fingers_closed = (landmarks[8][1] > landmarks[6][1] and  # Index
                              landmarks[12][1] > landmarks[10][1] and  # Middle
                              landmarks[16][1] > landmarks[14][1] and  # Ring
                              landmarks[20][1] > landmarks[18][1])  # Pinky

            if fingers_open:  # TakeOff Command
                fingers_open_counter += 1
                if fingers_open_counter >= threshold and drone_is_down:
                    cv2.putText(frame, "All Fingers Open Command Executed!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 255, 0), 2)
                    tello.takeoff()
                    drone_is_down = False
                    fingers_open_counter = 0

            elif thumb_up:  # Flip Back
                thumb_up_counter += 1
                if thumb_up_counter >= threshold:
                    cv2.putText(frame, "Thumbs Up Command Executed!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 255, 0), 2)
                    tello.flip_back()
                    thumb_up_counter = 0

            elif thumb_down:  # Land Command
                thumb_down_counter += 1
                if thumb_down_counter >= threshold and not drone_is_down:
                    cv2.putText(frame, "Thumbs Down Command Executed!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 255, 0), 2)
                    tello.land()
                    thumb_down_counter = 0
                    drone_is_down = True

            elif index_right:  # Flip Right
                index_right_counter += 1
                if index_right_counter >= threshold:
                    cv2.putText(frame, "Index Right Command Executed!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 255, 0), 2)
                    tello.flip_left()  # Because the camera is flipped
                    index_right_counter = 0

            elif index_left:  # Flip Left
                index_left_counter += 1
                if index_left_counter >= threshold:
                    cv2.putText(frame, "Index Left Command Executed!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 255, 0), 2)
                    tello.flip_right()  # Because the camera is flipped
                    index_left_counter = 0

            elif fingers_closed:  # Take A Picture
                fingers_closed_counter += 1
                if fingers_closed_counter >= threshold:
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    image_path = os.path.join(image_folder, f"image_{timestamp}.jpg")
                    cv2.imwrite(image_path, frame)
                    cv2.putText(frame, f"Image saved: {image_path}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0),
                                2)
                    fingers_closed_counter = 0

            else:
                # Reset all counters if no valid gesture is detected
                thumb_up_counter = thumb_down_counter = index_left_counter = index_right_counter = fingers_closed_counter = fingers_open_counter = 0
    return frame


def camera_feed(tello):
    global drone_is_down
    tello.takeoff()  # Init take off command by default at start
    drone_is_down = False  # Indicating the drone is not down
    tello.move_up(50)  # Move up a little bit so the drone will be with our height
    try:
        while True:
            # Get frame from Tello camera
            frame = tello.get_frame_read().frame  # Get the frame of the video from the tello camera
            frame = cv2.cvtColor(frame,
                                 cv2.COLOR_BGR2RGB)  # Convert frame colors from BGR to RGB (Red Green Blue) colors
            frame = hand_gestures(
                frame)  # Send the frame given by the drone to the hand gestures command and save it after process
            cv2.imshow("Tello Camera Feed", frame)  # Show the frame and display it to the user
            # Exit loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        pass


def tello_connect():
    tello = Tello()  # Save the Tello drone as variable
    tello.connect()  # Connect to the drone
    print(f"Battery: {tello.get_battery()}")  # Check the battery left and display it to the user
    tello.streamon()  # Open stream for the camera
    cv2.namedWindow("Tello Camera Feed")  # Name of the window
    return tello


def tello_disconnect(tello):
    tello.land()  # Landing the drone safely
    tello.streamoff()  # Turn off stream
    tello.end()  # End communication
    cv2.destroyAllWindows()  # Close all windows


if __name__ == "__main__":
    tello = tello_connect()  # Connect to tello
    camera_feed(tello)  # Show camera feed
    tello_disconnect(tello)  # Disconnect from tello
