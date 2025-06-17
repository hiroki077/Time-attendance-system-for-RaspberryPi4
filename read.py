import time
from machine import SPI, Pin
from mfrc522 import MFRC522
import os


# SPI設定
sck = Pin(6, Pin.OUT)
mosi = Pin(7, Pin.OUT)
miso = Pin(4, Pin.OUT)
cs = Pin(5, Pin.OUT)
rst = Pin(18, Pin.OUT)
spi = SPI(0, baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)
rdr = MFRC522(spi, cs, rst)
led = Pin(0, Pin.OUT)

CSV_FILE = "AttendanceRecord.csv"
CSV_HEADER = "日付,名前,社員番号,打刻1,打刻2,打刻3,打刻4,打刻5,打刻6"

# ユーザー読み込み
def load_users():
    users = {}
    max_number = 1000
    try:
        with open("users.csv", "r", encoding="utf-8") as f:
            for line in f:
                name, number, card_id = line.strip().split(",")
                users[card_id.lower()] = (name, number)
                if number.isdigit():
                    max_number = max(max_number, int(number))
    except:
        print("users.csv が見つかりません（新規作成予定）")
    return users, max_number

# 新規ユーザー登録
def register_new_user(uid, next_number):
    number = str(next_number + 1)
    name =  input(" 名前を入力してください 　また、キャンセルの場合は0000 を入力してください。")
    if name == "0000":
        print(" キャンセルされました")
        return None, None
    elif name == "":
            print("名前を空白で登録はできません。")
            return register_new_user(uid, next_number)
    else:
        with open("users.csv", "a", encoding="utf-8") as f:
            f.write(f"{name},{number},{uid}\n")
        print(f"{name} さん（社員番号: {number}）を新規登録しました")
        return name, number

# ワイド形式ログ保存 + ヘッダー付き
def log_attendance_wide(name, number, uid):
    now = time.localtime()
    date_str = "{:04d}-{:02d}-{:02d}".format(now[0], now[1], now[2])
    time_str = "{:02d}:{:02d}:{:02d}".format(now[3], now[4], now[5])

    # 既存行の読み込み（1行目がヘッダーであることに注意）
    lines = []
    found = False
    header_written = False

    try:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]
            if lines and lines[0].startswith("日付"):
                header_written = True
            else:
                lines.insert(0, CSV_HEADER)
                header_written = True
    except:
        lines = [CSV_HEADER]
        header_written = True

    for i in range(1, len(lines)):
        parts = lines[i].split(",")
        if len(parts) >= 3 and parts[0] == date_str and parts[1] == name and parts[2] == number:
            parts.append(time_str)
            lines[i] = ",".join(parts)
            found = True
            break

    if not found:
        lines.append(f"{date_str},{name},{number},{time_str}")

    with open(CSV_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

# メイン処理
print("カードをかざしてください...")

while True:
    (stat, tag_type) = rdr.request(rdr.REQIDL)
    if stat == rdr.OK:
        (stat, raw_uid) = rdr.anticoll()
        if stat == rdr.OK:
            led.value(True)
            uid = "0x" + "".join("%02x" % b for b in raw_uid).lower()
            print("検出UID:", uid)

            users, max_number = load_users()
            if uid in users:
                now = time.localtime()
                date_str = "{:04d}-{:02d}-{:02d}".format(now[0], now[1], now[2])
                time_str = "{:02d}:{:02d}:{:02d}".format(now[3], now[4], now[5])
                name, number = users[uid]
                print(f"{name} さん（社員番号: {number}）{date_str}{time_str} に打刻されました。")
            else:
                name, number = register_new_user(uid, max_number)

            log_attendance_wide(name, number, uid)
            time.sleep(1)
            led.value(False)
