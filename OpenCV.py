import cv2
import numpy as np
import sounddevice as sd

# ฟังก์ชันสำหรับสร้างเสียงโน้ต
def play_note(frequency, duration):
    sample_rate = 44100  # ความถี่การสุ่มเสียง
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    sound = 0.5 * np.sin(2 * np.pi * frequency * t)
    sd.play(sound, samplerate=sample_rate)
    sd.wait()

# ฟังก์ชันสำหรับตรวจจับสีและการเล่นเสียง
def detect_color_and_play(frame, last_played_color):
    # แปลงภาพจาก BGR เป็น HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # กำหนดขอบเขตสีที่ต้องการตรวจจับ (สีต่าง ๆ ตามที่กำหนด)
    color_ranges = {
        "red": ([0, 120, 70], [10, 255, 255], 261.63),  # โด
        "orange": ([10, 120, 70], [25, 255, 255], 293.66),  # เร
        "green": ([35, 100, 100], [85, 255, 255], 329.63),  # มี
        "yellow": ([20, 100, 100], [35, 255, 255], 349.23),  # ฟา
        "blue": ([90, 100, 100], [140, 255, 255], 392.00),  # ซอล
        "light_blue": ([80, 100, 100], [130, 255, 255], 440.00),  # ลา
        "purple": ([140, 100, 100], [170, 255, 255], 466.16),  # ที
    }

    # ตรวจสอบว่าไม่มีสีใดๆ ถูกตรวจพบ
    for color, (lower, upper, frequency) in color_ranges.items():
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

        if np.sum(mask) > 10000:  # ถ้าพบสีนี้ในภาพ
            if color != last_played_color:  # ถ้าไม่เคยเล่นสีนี้ล่าสุด
                play_note(frequency, 1)  # เล่นเสียงโน้ต
                return color  # ส่งคืนสีที่เล่นเสียงไปแล้ว
    
    # หากไม่พบสีที่กำหนดเลย ไม่ต้องเล่นเสียง
    return last_played_color  # หากไม่พบสีใหม่ ให้คงสีเดิม

# เปิดกล้องเว็บแคม
cap = cv2.VideoCapture(0)

# ตัวแปรเก็บสีที่เล่นเสียงล่าสุด
last_played_color = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ตรวจจับสีและเล่นเสียง
    last_played_color = detect_color_and_play(frame, last_played_color)

    # แสดงผลภาพจากกล้อง
    cv2.imshow("Frame", frame)

    # กด 'q' เพื่อออกจากโปรแกรม
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ปิดการเชื่อมต่อกล้องและหน้าต่าง
cap.release()
cv2.destroyAllWindows()
