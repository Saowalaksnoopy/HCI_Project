import cv2
import numpy as np
import sounddevice as sd
import threading
import time

# 🎵 Play sound asynchronously
def play_note_async(frequency, duration):
    def play():
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        sound = 0.5 * np.sin(2 * np.pi * frequency * t)
        sd.play(sound, samplerate=sample_rate)
        sd.wait()

    threading.Thread(target=play).start()

# 🌟 Color Detection Function
def detect_colors_in_frame(frame, last_color, last_color_time, hold_duration=0.5):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define colors and their HSV ranges + sound frequencies
    color_ranges = {
        "red": ([0, 120, 100], [10, 255, 255], 293.66),  # Red (0-10 degrees)
        "green": ([35, 50, 50], [85, 255, 255], 349.23),  # Green (35-85 degrees)
        "blue": ([90, 50, 50], [130, 255, 255], 392.00),  # Blue (90-130 degrees)
        "yellow": ([20, 100, 100], [40, 255, 255], 329.63),  # Yellow (20-40 degrees)
        "purple": ([140, 50, 50], [160, 255, 255], 440.00),  # Purple (140-160 degrees)
        "brown": ([10, 40, 50], [30, 255, 200], 493.88),  # Brown (10-30 degrees)
        "black": ([0, 0, 0], [180, 255, 50], 261.63)  # Black (Low saturation and low value)
    }

    current_time = time.time()
    detected_color = None
    highlighted_frame = frame.copy()

    # Reduce Noise and improve detection accuracy
    blurred_frame = cv2.GaussianBlur(hsv, (5, 5), 0)

    for color, (lower, upper, frequency) in color_ranges.items():
        mask = cv2.inRange(blurred_frame, np.array(lower), np.array(upper))

        # Reduce Noise in Mask
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

        # Find contours and detect large enough regions
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            for contour in contours:
                if cv2.contourArea(contour) > 1000:  # Ignore small areas
                    detected_color = color

                    # Highlight detected region
                    cv2.drawContours(highlighted_frame, [contour], -1, (0, 255, 0), 2)

                    if color != last_color:
                        # Detect a new color: Check if the previous color has been held long enough
                        if current_time - last_color_time >= hold_duration:
                            play_note_async(frequency, 0.5)  # Play sound
                            return color, current_time, highlighted_frame
                    else:
                        # Same color continues being detected
                        return last_color, last_color_time, highlighted_frame

    # If no new color detected, retain the previous color
    return last_color, last_color_time, highlighted_frame

# 👁 Main Function to Process Live Video
def main():
    cap = cv2.VideoCapture(0)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    print("Press 'q' to exit...")
    last_color = None
    last_color_time = time.time()

    while True:
        ret, frame = cap.read()

        # Check if the frame was successfully captured
        if not ret:
            print("Error: Failed to capture frame.")
            break

        # Detect colors in the current frame
        last_color, last_color_time, highlighted_frame = detect_colors_in_frame(frame, last_color, last_color_time)

        # Add text showing the detected color
        if last_color:
            cv2.putText(
                highlighted_frame,
                f"Detected Color: {last_color}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        # Show the processed frame
        cv2.imshow("Color Detection", highlighted_frame)

        # Press 'q' to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
