import numpy as np
import sounddevice as sd

# ฟังก์ชันสำหรับสร้างเสียงโน้ต
def play_note(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    sound = 0.5 * np.sin(2 * np.pi * frequency * t)  # คลื่นเสียงไซน์
    return sound

# ฟังก์ชันสำหรับสร้างเสียงเงียบ (ช่องว่าง)
def silence(duration, sample_rate=44100):
    return np.zeros(int(sample_rate * duration))  # สร้างเสียงเงียบ

# กำหนดโน้ตและความถี่
notes = {
    'C4': 261.63,  # โด (C4)
    'D4': 293.66,  # เร (D4)
    'E4': 329.63,  # มี (E4)
    'F4': 349.23,  # ฟา (F4)
    'G4': 392.00,  # ซอล (G4)
    'A4': 440.00,  # ลา (A4)
    'B4': 493.88,  # ซี (B4)
    'C5': 523.25   # โด (C5)
}

# เพลง: Twinkle Twinkle Little Star
song = [
    ('C4', 0.5), ('C4', 0.5), ('G4', 0.5), ('G4', 0.5),
    ('A4', 0.5), ('A4', 0.5), ('G4', 1), ('F4', 0.5),
    ('F4', 0.5), ('E4', 0.5), ('E4', 0.5), ('D4', 0.5),
    ('D4', 0.5), ('C4', 1)
]

# สร้างเสียงทั้งหมดที่มีความต่อเนื่อง
full_sound = np.array([])

# รวมคลื่นเสียงของแต่ละโน้ตในเพลง พร้อมกับช่องว่างระหว่างโน้ต
for note, duration in song:
    full_sound = np.concatenate((full_sound, play_note(notes[note], duration)))  # เล่นโน้ต
    full_sound = np.concatenate((full_sound, silence(0.1)))  # เพิ่มช่องว่างระหว่างโน้ต (สามารถปรับค่าช่องว่างนี้ได้)

# เล่นเสียงทั้งหมดพร้อมกัน
sd.play(full_sound, samplerate=44100)
sd.wait()
