import RPi.GPIO as GPIO
GPIO.setwarnings(False)
from mfrc522 import SimpleMFRC522

print("=== プログラム開始 ===")

try:
    # RSTピン指定：GPIO25（デフォルトでOK、もし変更必要ならSimpleMFRC522(pin_rst=25)）
    reader = SimpleMFRC522()
    print("リーダー初期化OK")
except Exception as e:
    print("リーダー初期化失敗:", e)
    exit(1)

try:
    print("ICカードをかざしてください...")
    id, text = reader.read()
    print("読み取り成功！")
    print(f"ID: {id}")
    print(f"Text: {text}")
except Exception as e:
    print("読み取りエラー:", e)
finally:
    print("プログラム終了")
