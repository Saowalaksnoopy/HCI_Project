import cv2
import numpy as np
import sounddevice as sd

# ฟังก์ชันเล่นเสียงตามโน้ตแบบ Asynchronous
def play_note_async(frequency, duration=0.5):
    sample_rate = 44100  # ความถี่การสุ่มเสียง
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    sound = 0.3 * np.sin(2 * np.pi * frequency * t)  # คลื่นเสียง Sine Wave
    sd.play(sound, samplerate=sample_rate)

# ฟังก์ชันตรวจจับสีไม้ไอติมและเล่นเสียง
def detect_stick_and_play(frame, last_played_color):
    # แปลงจาก BGR เป็น HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # ค่าสี HSV สำหรับแท่งไม้ไอติมแต่ละสีและความถี่เสียงที่สัมพันธ์กับโน้ต
    color_ranges = {
        "red": ([0, 120, 70], [10, 255, 255], 261.63),       # C (โด)
        "orange": ([11, 100, 100], [25, 255, 255], 293.66),   # D (เร)
        "yellow": ([25, 100, 100], [35, 255, 255], 329.63),   # E (มี)
        "green": ([35, 100, 100], [85, 255, 255], 349.23),    # F (ฟา)
        "light_blue": ([86, 100, 100], [125, 255, 255], 392.00), # G (ซอล)
        "blue": ([126, 100, 100], [140, 255, 255], 440.00),   # A (ลา)
        "purple": ([136, 100, 100], [160, 255, 255], 493.88), # B (ที)
        "black": ([0, 0, 0], [180, 255, 50], 523.25),         # High C (โด) สำหรับสีดำ
    }

    # ตัวแปรเก็บค่าพื้นที่และสีที่ใหญ่ที่สุด
    largest_area = 0
    best_contour = None
    best_color = None
    best_frequency = None

    # ตรวจจับแต่ละสีในภาพ
    for color, (lower, upper, frequency) in color_ranges.items():
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

        # ลด Noise ด้วย Morphological Operations
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)

        # ค้นหา Contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000 and area > largest_area:  # กรองพื้นที่ใหญ่พอ
                largest_area = area
                best_contour = contour
                best_color = color
                best_frequency = frequency

    # ถ้าพบสีที่มีขนาดพื้นที่ใหญ่ที่สุด
    if best_contour is not None:
        x, y, w, h = cv2.boundingRect(best_contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)  # วาดกรอบสี่เหลี่ยม
        cv2.putText(frame, f"Detected: {best_color}", (x, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # เล่นเสียงถ้าสีไม่ซ้ำกับครั้งก่อนหน้า
        if best_color != last_played_color:
            play_note_async(best_frequency)
            return best_color

    return last_played_color

# ฟังก์ชันสำหรับเปิดกล้อง USB
def open_usb_camera():
    cap = cv2.VideoCapture(1)  # เปิดกล้องที่มี index = 1
    if not cap.isOpened():  # ตรวจสอบว่าเปิดกล้องได้หรือไม่
        print("ไม่สามารถเปิดกล้อง USB ที่ index 1")  # ถ้าไม่สามารถเปิดได้
        exit()  # หยุดโปรแกรม
    return cap  # คืนค่ากล้องที่เปิดใช้งานแล้ว

# เปิดกล้องเว็บแคม
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Cannot open camera.")
    exit()

# ตัวแปรเก็บค่าสีที่เล่นเสียงล่าสุด
last_played_color = None

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab frame.")
        break

    # ปรับแสงและคอนทราสต์ก่อนตรวจจับ
    frame = cv2.convertScaleAbs(frame, alpha=1.3, beta=40)

    # ตรวจจับสีและเล่นเสียง
    last_played_color = detect_stick_and_play(frame, last_played_color)

    # แสดงผลลัพธ์
    cv2.imshow("Stick Detection with Notes", frame)

    # กด 'q' เพื่อปิดโปรแกรม
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ปิดกล้องและหน้าต่าง
cap.release()
cv2.destroyAllWindows()
