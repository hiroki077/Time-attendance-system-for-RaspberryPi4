import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522
from api_client import is_card_registered, register_work_time, post_unregistered_scan
from webserver import start_webserver, state
from time_sync import get_jst_time
from device_config import fetch_device_info

GREEN_LED = 27
RED_LED = 22
YELLOW_LED = 17
BUZZER = 16

GPIO.setmode(GPIO.BCM)
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
        # 最新デバイス情報（DBから毎回取得）
        device_info = fetch_device_info("raspi4")
        DEVICE_NAME = device_info['device_name']
        LOCATION_NAME = device_info['location_name']
        PRIMARY_FIXED_IP = device_info['primary_ip']

        print("waiting...")
        id, text = reader.read()
        uid = hex(id)
        now_time = get_jst_time()
        now_str = now_time.strftime("%Y/%m/%d %H:%M:%S")
        now_ts = time.time()

        # 二重スキャン防止
        if uid in state["last_scan_times"] and now_ts - state["last_scan_times"][uid] < 10:
            state["status"] = "⚠️ 注意: 時間を置いてください "
            GPIO.output(RED_LED, True); GPIO.output(GREEN_LED, False); GPIO.output(YELLOW_LED, False)
            error_sound()
            continue

        state["last_scan_times"][uid] = now_ts
        beep()
        state.update({"uid_display": uid, "scan_time_display": now_str})

        result = is_card_registered(uid)
        print("[DEBUG] check_card_status:", result, result.get("usage_type"))

        if not result.get("registered"):
            if result.get("usage_type") == "visitor":
                if customer_state == 0:
                    print(">>> 顧客カードを検出。customer_state → Serving")
                    state["customer_state"] = "Serving"
                    GPIO.output(GREEN_LED, True)
                    time.sleep(0.2)
                    GPIO.output(GREEN_LED, False)
                    time.sleep(1.0)
                    customer_state += 1
                    continue
                elif customer_state == 1:
                    state["customer_state"] = "Idle"
                    print(" お客さんの対応を終えました。")
                    GPIO.output(GREEN_LED, True)
                    time.sleep(0.2)
                    GPIO.output(GREEN_LED, False)
                    time.sleep(1.0)
                    customer_state = 0
                    continue

        if result.get("registered"):
            if result.get("usage_type") == "staff":
                assignee_type = "collaborator"
                assignee_id = 1  # 必要に応じてDBから取っても良い
                scanned_name = result.get("assignee", "---")
                state["name_display"] = scanned_name
                state["scan_time_display"] = now_str

                log_res = register_work_time(uid, assignee_type, assignee_id, action="checkin", device=DEVICE_NAME, location=LOCATION_NAME)
                print("[DEBUG] register_work_time:", log_res)
                state["status"] = "打刻成功" if log_res.get("message") else "打刻失敗"
                GPIO.output(GREEN_LED, True); GPIO.output(RED_LED, False); GPIO.output(YELLOW_LED, False)
                beep()

                # 履歴管理：新→旧順で保存
                if scanned_name not in state["history"]:
                    state["history"][scanned_name] = []
                state["history"][scanned_name].insert(0, {"time": now_str, "timestamp": now_ts})
                state["history"][scanned_name] = state["history"][scanned_name][:10]

                logs = state["history"][scanned_name]
                scan_count = len(logs)

                # 2回スキャン時に休憩中
                if scan_count == 2:
                    elapsed = logs[0]["timestamp"] - logs[1]["timestamp"]
                    if elapsed < 3600:
                        state["break_time_left"] = int(3600 - elapsed)
                        state["status"] = "休憩中"
                    else:
                        state["break_time_left"] = None
                        state["status"] = "休憩終了"
                elif scan_count == 3:
                    state["break_time_left"] = None
                    state["status"] = "休憩終了"
                elif scan_count > 3:
                    state["break_time_left"] = None
                    state["status"] = "打刻しました"
                else:
                    state["break_time_left"] = None
                    state["status"] = "打刻しました"

        elif result.get("usage_type") is not None:
            state["status"] = "⚠️ ユーザー登録をしてください。"
            GPIO.output(YELLOW_LED, True); GPIO.output(GREEN_LED, False); GPIO.output(RED_LED, True)
            error_sound()
            state["break_time_left"] = None

        else:
            unreg_res = post_unregistered_scan(uid, device=DEVICE_NAME, location=LOCATION_NAME)
            print("[DEBUG] unregistered scan:", unreg_res)
            state["status"] = "未登録カード"
            GPIO.output(RED_LED, True); GPIO.output(GREEN_LED, False); GPIO.output(YELLOW_LED, False)
            error_sound()
            state["break_time_left"] = None

        time.sleep(0.1)

if __name__ == "__main__":
    start_webserver()
    main_loop()
