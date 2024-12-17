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

# 🌟 Color Detection Function (Improved Purple Detection)
def detect_colors_in_frame(frame, last_color, last_color_time, hold_duration=0.5):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define colors and their HSV ranges + sound frequencies
    color_ranges = {
        "red": ([[[0, 120, 100], [10, 255, 255]], [[170, 120, 100], [180, 255, 255]]], 293.66),  # Red (two ranges)
        "green": ([[[35, 50, 50], [85, 255, 255]]], 349.23),  # Green (35-85 degrees)
        "blue": ([[[90, 50, 50], [130, 255, 255]]], 392.00),  # Blue (90-130 degrees)
        "yellow": ([[[20, 100, 100], [40, 255, 255]]], 329.63),  # Yellow (20-40 degrees)
        "purple": ([[[125, 50, 50], [155, 255, 255]],  # Purple (extended Hue range)
                    [[155, 50, 50], [165, 255, 255]]], 415.30),  # Second range for deeper purple
        "orange": ([[[10, 100, 100], [25, 255, 255]]], 493.88),  # Orange (10-25 degrees)
        "black": ([[[0, 0, 0], [180, 255, 50]]], 261.63)  # Black (Low saturation and low value)
    }

    current_time = time.time()
    detected_color = None
    highlighted_frame = frame.copy()

    # Reduce Noise and improve detection accuracy
    blurred_frame = cv2.GaussianBlur(hsv, (5, 5), 0)

    for color, (ranges, frequency) in color_ranges.items():
        mask = None
        for lower, upper in ranges:  # Iterate through multiple HSV ranges for each color
            temp_mask = cv2.inRange(blurred_frame, np.array(lower), np.array(upper))
            mask = temp_mask if mask is None else cv2.bitwise_or(mask, temp_mask)

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

# ฟังก์ชันตรวจจับวัตถุไม้ไอติม
def detect_popsicle(frame):
    # แปลงภาพเป็นสีเทา
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # ใช้ GaussianBlur เพื่อลดสัญญาณรบกวน
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # ใช้ Canny edge detection เพื่อหาขอบ
    edges = cv2.Canny(blurred, 50, 150)

    # หาขอบในภาพ
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # กรองคอนทัวร์ที่ไม่ต้องการและตรวจสอบขนาด
    for contour in contours:
        # หาขอบเขตของคอนทัวร์
        x, y, w, h = cv2.boundingRect(contour)

        # ตรวจสอบขนาดของวัตถุ (ไม้ไอติม)
        min_size = 50  # ขนาดขั้นต่ำ (ในพิกเซล) ค่าที่ปรับได้
        max_size = 100  # ขนาดสูงสุด (ในพิกเซล) ค่าที่ปรับได้

        # กรองตามขนาดที่ต้องการ
        if min_size < w < max_size and min_size < h < max_size:
            # วาดกรอบสี่เหลี่ยมเพื่อแสดงผล
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return frame

# ฟังก์ชันหลักสำหรับการประมวลผลภาพ
def main():
    cap = cv2.VideoCapture(1)  # ใช้กล้อง USB

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    print("Press 'q' to exit...")
    last_color = None
    last_color_time = time.time()

    while True:
        ret, frame = cap.read()

        # ตรวจสอบว่าอ่านภาพได้หรือไม่
        if not ret:
            print("Error: Failed to capture frame.")
            break

        # ตรวจจับสีในกรอบภาพ
        last_color, last_color_time, highlighted_frame = detect_colors_in_frame(frame, last_color, last_color_time)

        # ตรวจจับไม้ไอติมในกรอบภาพ
        highlighted_frame = detect_popsicle(highlighted_frame)

        # แสดงผลข้อความสีที่ตรวจจับ
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

        # แสดงผลภาพที่ประมวลผลแล้ว
        cv2.imshow("Detected Popsicle and Colors", highlighted_frame)

        # กด 'q' เพื่อออกจากลูป
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # ปล่อยทรัพยากร
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
