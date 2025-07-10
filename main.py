#!/usr/bin/env python3
import sys
import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522
from api_client import is_card_registered, register_work_time, post_unregistered_scan
from webserver import start_webserver, state
from time_sync import get_jst_time
from device_config import fetch_device_info
import subprocess
import os
from excel_logger import save_attendance_excel

GREEN_LED = 27
RED_LED = 22
YELLOW_LED = 17
BUZZER = 16

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(YELLOW_LED, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

def beep(dur=0.1):
    GPIO.output(BUZZER, True)
    time.sleep(dur)
    GPIO.output(BUZZER, False)

def error_sound():
    for _ in range(3):
        beep(0.05)
        time.sleep(0.05)

def start_admin_web():
    """venv の Python で admin_web.py を起動する"""
    python_exe = sys.executable  # venv/bin/python を指す
    admin_path = os.path.join(os.path.dirname(__file__), "admin_web.py")
    print(f"🚀 Launch admin_web with: {python_exe} {admin_path}")
    subprocess.Popen([python_exe, admin_path], cwd=os.path.dirname(__file__))

# 初期表示設定
GPIO.output(GREEN_LED, False)
GPIO.output(RED_LED, False)
GPIO.output(YELLOW_LED, True)
GPIO.output(BUZZER, False)
state.update({
    "uid_display": "---",
    "name_display": "---",
    "scan_time_display": "---",
    "status": "Waiting...",
    "last_scan_times": {},
    "history": {},
    "break_time_left": None,
    "customer_state": "Idle",
})

customer_state = 0

def main_loop():
    global customer_state
    reader = SimpleMFRC522()

    while True:
        # --- カード読み取り & 時刻取得 ---
        id, _ = reader.read()
        uid = hex(id)
        try:
            now_time = get_jst_time()
        except Exception as e:
            print("[WARN] get_jst_time failed, fallback to local:", e)
            from datetime import datetime
            now_time = datetime.now()
        now_str = now_time.strftime("%Y/%m/%d %H:%M:%S")
        now_ts = time.time()

        # --- 連続タップ防止 ---
        last = state["last_scan_times"].get(uid, 0)
        if now_ts - last < 10:
            state["status"] = "⚠️ 注意: 時間を置いてください"
            GPIO.output(RED_LED, True); GPIO.output(GREEN_LED, False); GPIO.output(YELLOW_LED, False)
            error_sound()
            continue
        state["last_scan_times"][uid] = now_ts

        beep()
        state.update({"uid_display": uid, "scan_time_display": now_str})

        # --- ネットワーク＆打刻処理 ---
        try:
            dev = fetch_device_info("raspi4")
            DEVICE_NAME = dev["device_name"]
            LOCATION_NAME = dev["location_name"]

            result = is_card_registered(uid)
            print("[DEBUG] check_card_status:", result)

            if not result.get("registered") and result.get("usage_type") == "visitor":
                # visitor 用簡易モード
                if customer_state == 0:
                    state["customer_state"] = "Serving"
                    GPIO.output(GREEN_LED, True); time.sleep(0.2); GPIO.output(GREEN_LED, False)
                    time.sleep(1.0)
                    customer_state = 1
                else:
                    state["customer_state"] = "Idle"
                    GPIO.output(GREEN_LED, True); time.sleep(0.2); GPIO.output(GREEN_LED, False)
                    time.sleep(1.0)
                    customer_state = 0

            elif result.get("registered") and result.get("usage_type") == "staff":
                # staff の打刻
                name = result.get("assignee", "")
                state["name_display"] = name
                log_res = register_work_time(
                    uid, "collaborator", 1,
                    action="checkin", device=DEVICE_NAME, location=LOCATION_NAME
                )
                save_attendance_excel(name, uid, dt=now_time)
                state["status"] = "打刻成功" if log_res.get("message") else "打刻失敗"
                GPIO.output(GREEN_LED, True); GPIO.output(RED_LED, False); GPIO.output(YELLOW_LED, False)
                beep()

            elif result.get("usage_type") is not None:
                # 登録はあるが staff/visitor ではない
                state["status"] = "⚠️ ユーザー登録をしてください。"
                GPIO.output(YELLOW_LED, True); GPIO.output(GREEN_LED, False); GPIO.output(RED_LED, True)
                error_sound()
                save_attendance_excel("", uid, dt=now_time)

            else:
                # 完全未登録
                post_unregistered_scan(uid, device=DEVICE_NAME, location=LOCATION_NAME)
                state["status"] = "未登録カード"
                GPIO.output(RED_LED, True); GPIO.output(GREEN_LED, False); GPIO.output(YELLOW_LED, False)
                error_sound()
                save_attendance_excel("", uid, dt=now_time)

        except Exception as e:
            print("[ERROR] ネット接続障害 or API エラー:", e)
            state["status"] = "ネット接続なし：UIDを保存"
            GPIO.output(YELLOW_LED, True); GPIO.output(GREEN_LED, False); GPIO.output(RED_LED, False)
            error_sound()
            save_attendance_excel(None, uid, dt=now_time)

        time.sleep(0.1)

if __name__ == "__main__":
    start_webserver()
    start_admin_web()
    main_loop()
