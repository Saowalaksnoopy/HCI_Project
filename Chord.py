import numpy as np
import sounddevice as sd

# ฟังก์ชันสำหรับสร้างเสียงโน้ต
def play_note(frequency, duration):
    sample_rate = 44100  # ความถี่การสุ่มเสียง
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    sound = 0.5 * np.sin(2 * np.pi * frequency * t)  # คลื่นเสียงไซน์
    return sound

# ฟังก์ชันสำหรับเล่นคอร์ด
def play_chord(frequencies, duration):
    chord_sound = np.zeros(int(44100 * duration))  # เตรียมคลื่นเสียงว่าง
    for freq in frequencies:
        chord_sound += play_note(freq, duration)  # เพิ่มเสียงโน้ตลงในคอร์ด
    sd.play(chord_sound, samplerate=44100)  # เล่นเสียงคอร์ด
    sd.wait()

# กำหนดโน้ตและความถี่
notes = {
    'C4': 261.63,  # โด (C4)
    'D4': 293.66,  # เร (D4)
    'E4': 329.63,  # มี (E4)
    'F4': 349.23,  # ฟา (F4)
    'G4': 392.00,  # ซอล (G4)
    'A4': 440.00,  # ลา (A4)
    'B4': 493.88,  # ซี (B4)
    'C5': 523.25,  # โด (C5)
    'D5': 587.33,  # เรสูงๆๆ (D5) เพิ่มเข้าไป
    'E5': 659.25,  # มี (E5)
    'F5': 698.46,  # ฟา (F5)
    'G5': 783.99   # ซอล (G5)
}

# เพลง: Twinkle Twinkle Little Star (เล่นเป็นคอร์ด)
song = [
    # คอร์ด C (C major)
    ([notes['C4'], notes['E4'], notes['G4']], 0.5), 
    ([notes['C4'], notes['E4'], notes['G4']], 0.5), 
    
    # คอร์ด G (G major)
    ([notes['G4'], notes['B4'], notes['D5']], 0.5),
    ([notes['G4'], notes['B4'], notes['D5']], 0.5),
    
    # คอร์ด C (C major)
    ([notes['C4'], notes['E4'], notes['G4']], 0.5),
    ([notes['C4'], notes['E4'], notes['G4']], 0.5),
    
    # คอร์ด F (F major)
    ([notes['F4'], notes['A4'], notes['C5']], 0.5),
    ([notes['F4'], notes['A4'], notes['C5']], 0.5),
    
    # คอร์ด C (C major)
    ([notes['C4'], notes['E4'], notes['G4']], 0.5),
    ([notes['C4'], notes['E4'], notes['G4']], 0.5),
    
    # คอร์ด G (G major)
    ([notes['G4'], notes['B4'], notes['D5']], 0.5),
    ([notes['G4'], notes['B4'], notes['D5']], 0.5),
    
    # คอร์ด C (C major)
    ([notes['C4'], notes['E4'], notes['G4']], 1)
]

# เล่นเพลงแบบคอร์ด
for chord, duration in song:
    play_chord(chord, duration)
