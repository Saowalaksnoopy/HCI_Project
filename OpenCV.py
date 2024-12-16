import cv2
import numpy as np
import sounddevice as sd
import threading

# กำหนดความถี่ของเสียงโน๊ต
NOTES = {
    "red": 261.63,    # โด (C4)
    "orange": 293.66, # เร (D4)
    "green": 329.63,  # มี (E4)
    "yellow": 349.23, # ฟา (F4)
    "blue": 392.00,   # ซอล (G4)
    "Indigo": 440.00, # ลา (A4)
    "purple": 493.88  # ที (B4)
}

# ฟังก์ชันสำหรับเล่นเสียง
def play_sound(frequency, duration=0.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)  # สร้างช่วงเวลา
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)  # สร้างคลื่นเสียงโดยใช้ sine wave
    sd.play(wave, samplerate=sample_rate)  # เล่นคลื่นเสียง
    sd.wait()  # รอจนกว่าเสียงจะเล่นเสร็จ

# ฟังก์ชันสำหรับตรวจจับสีในภาพ
def detect_colors(frame):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # แปลงภาพจาก BGR เป็น HSV
    detected_colors = []  # ลิสต์สำหรับเก็บสีที่ตรวจจับได้

    # กำหนดช่วงสีใน HSV สำหรับแต่ละสี
    color_ranges = {
        "red": [(0, 120, 70), (10, 255, 255)],  # ช่วงสีแดง
        "orange": [(11, 100, 100), (25, 255, 255)],  # ช่วงสีส้ม
        "yellow": [(26, 100, 100), (35, 255, 255)],  # ช่วงสีเหลือง
        "green": [(36, 100, 100), (85, 255, 255)],  # ช่วงสีเขียว
        "blue": [(86, 100, 100), (125, 255, 255)],  # ช่วงสีน้ำเงิน
        "Indigo": [(126, 100, 100), (140, 255, 255)],  # ช่วงสีคราม
        "purple": [(141, 100, 100), (160, 255, 255)]  # ช่วงสีม่วง
    }

    # ตรวจจับสีที่อยู่ในช่วงที่กำหนด
    for color, (lower, upper) in color_ranges.items():
        mask = cv2.inRange(hsv_frame, np.array(lower), np.array(upper))  # สร้างหน้ากากสี
        if cv2.countNonZero(mask) > 0:  # ถ้ามีพิกเซลที่ตรงกับสี
            detected_colors.append(color)  # เพิ่มสีที่ตรวจพบลงในลิสต์

    # จำกัดให้ตรวจจับสีได้สูงสุดแค่ 3 สี
    return detected_colors[:3]  # ส่งคืนลิสต์สีที่ตรวจจับได้สูงสุด 3 สี

# ฟังก์ชันสำหรับเปิดกล้อง USB
def open_usb_camera():
    cap = cv2.VideoCapture(1)  # เปิดกล้องที่มี index = 1
    if not cap.isOpened():  # ตรวจสอบว่าเปิดกล้องได้หรือไม่
        print("ไม่สามารถเปิดกล้อง USB ที่ index 1")  # ถ้าไม่สามารถเปิดได้
        exit()  # หยุดโปรแกรม
    return cap  # คืนค่ากล้องที่เปิดใช้งานแล้ว

# ฟังก์ชันสำหรับเล่นเสียงหลายๆ ตัวพร้อมกัน
def play_sounds_concurrently(colors):
    threads = []  # ลิสต์สำหรับเก็บ thread
    for color in colors:
        if color in NOTES:  # ตรวจสอบว่าในลิสต์สีที่พบ มีสีที่กำหนดไว้ใน NOTES หรือไม่
            thread = threading.Thread(target=play_sound, args=(NOTES[color], 0.5))  # สร้าง thread เพื่อเล่นเสียง
            threads.append(thread)  # เพิ่ม thread ลงในลิสต์
            thread.start()  # เริ่มต้น thread
    for thread in threads:  # รอให้ทุก thread เสร็จสิ้น
        thread.join()

# เริ่มการตรวจจับด้วยกล้อง
cap = open_usb_camera()

# ปรับตั้งค่าของกล้องเพื่อลด delay
cap.set(cv2.CAP_PROP_FPS, 30)  # ตั้งค่าความเร็วในการจับภาพเป็น 30 เฟรมต่อวินาที
cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)  # จำกัดจำนวนเฟรมใน buffer เป็น 3 เพื่อลดการหน่วง

while True:
    ret, frame = cap.read()  # อ่านภาพจากกล้อง
    if not ret:  # ถ้าไม่สามารถอ่านภาพได้
        print("ไม่สามารถอ่านภาพจากกล้องได้")  # แสดงข้อความผิดพลาด
        continue  # ไปทำงานในลูปถัดไป

    # ย่อขนาดเฟรมเพื่อลดการใช้ทรัพยากร
    frame = cv2.resize(frame, (640, 480))  # เปลี่ยนขนาดภาพให้มีความกว้าง 640px และสูง 480px

    # ตรวจจับสีในเฟรม
    colors = detect_colors(frame)

    # หากพบสีที่ตรวจจับได้ ให้เล่นเสียงโน๊ตตามสี
    if colors:
        print(f"สี: {', '.join(colors)}")  # แสดงสีที่ตรวจพบ
        play_sounds_concurrently(colors)  # เล่นเสียงพร้อมกัน

    # แสดงภาพจากกล้อง
    cv2.imshow("Frame", frame)
    cv2.waitKey(1)  # รอ 1 มิลลิวินาที

# ปิดกล้องและหน้าต่าง
cap.release()  # ปิดการเชื่อมต่อกับกล้อง
cv2.destroyAllWindows()  # ปิดหน้าต่างที่แสดงภาพ
