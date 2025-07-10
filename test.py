from mfrc522 import MFRC522
import RPi.GPIO as GPIO
import signal
import time

GPIO.setwarnings(False)
reader = MFRC522(pin_rst=26)

def end_read(signal, frame):
    print("終了します")
    GPIO.cleanup()
    exit()

signal.signal(signal.SIGINT, end_read)

print("カードをスキャンしてください... (Ctrl+Cで終了)")

while True:
    (status, TagType) = reader.MFRC522_Request(reader.PICC_REQIDL)
    if status == reader.MI_OK:
        print("カード検出")
        (status, uid) = reader.MFRC522_Anticoll()
        if status == reader.MI_OK:
            print("UID:", uid)
        else:
            print("⚠️ UIDの取得に失敗しました")
    time.sleep(0.5)
