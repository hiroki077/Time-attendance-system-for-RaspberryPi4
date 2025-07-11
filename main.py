#!/usr/bin/env python3
import sys, os, time, subprocess
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from api_client import is_card_registered, register_work_time, post_unregistered_scan
from webserver import start_webserver, state
from time_sync import get_jst_time
from device_config import fetch_device_info
from excel_logger import save_attendance_excel

# ───── GPIO ─────
GREEN_LED = 27
RED_LED   = 22
YELLOW_LED= 17
BUZZER    = 16
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup([GREEN_LED, RED_LED, YELLOW_LED, BUZZER], GPIO.OUT)

def beep(dur=0.1):
    GPIO.output(BUZZER, 1); time.sleep(dur); GPIO.output(BUZZER, 0)

def error_sound():
    for _ in range(3):
        beep(0.05); time.sleep(0.05)

def start_admin_web():
    python_exe = sys.executable
    admin_path = os.path.join(os.path.dirname(__file__), "admin_web.py")
    print(f"🚀 Launch admin_web with: {python_exe} {admin_path}")
    subprocess.Popen([python_exe, admin_path], cwd=os.path.dirname(__file__))

# ───── 初期 UI 状態 ─────
GPIO.output(GREEN_LED, 0); GPIO.output(RED_LED, 0); GPIO.output(YELLOW_LED, 1)
state.update({
    "uid_display":       "---",
    "name_display":      "---",
    "scan_time_display": "---",
    "status":            "Waiting...",
    "last_scan_times":   {}, 
    "history":           {}, 
    "break_time_left":   None,
    "customer_state":    "Idle",
})

customer_state = 0       

# ★ 休憩判定に使う定数（必要なら調整）
BREAK_WINDOW_SEC = 3600   # 2 回目から 1 時間以内は休憩扱い
MAX_HISTORY_LEN  = 10     # 各人の履歴保持数

# ───── メインループ ─────
def main_loop():
    global customer_state
    reader = SimpleMFRC522()

    while True:
        # ---------- カード読み取り ----------
        id, _ = reader.read()
        uid = hex(id)

        try:
            now_time = get_jst_time()
        except Exception as e:
            print("[WARN] get_jst_time failed, fallback to local:", e)
            from datetime import datetime
            now_time = datetime.now()
        now_str = now_time.strftime("%Y/%m/%d %H:%M:%S")
        now_ts  = time.time()

        # ---------- 連続タップ防止 ----------
        last = state["last_scan_times"].get(uid, 0)
        if now_ts - last < 10:
            state["status"] = "⚠️ 注意: 時間を置いてください"
            GPIO.output([GREEN_LED, YELLOW_LED], 0); GPIO.output(RED_LED, 1)
            error_sound()
            continue
        state["last_scan_times"][uid] = now_ts

        # UI 更新
        beep()
        state.update({"uid_display": uid, "scan_time_display": now_str})

        try:
            # ---------- API チェック ----------
            dev = fetch_device_info("raspi4")
            DEVICE_NAME   = dev["device_name"]
            LOCATION_NAME = dev["location_name"]

            result = is_card_registered(uid)
            print("[DEBUG] check_card_status:", result)

            # ---------- Visitor 簡易モード ----------
            if not result.get("registered") and result.get("usage_type") == "visitor":
                if customer_state == 0:
                    customer_state         = 1
                    state["customer_state"] = "Serving"
                else:
                    customer_state         = 0
                    state["customer_state"] = "Idle"
                GPIO.output(GREEN_LED, 1); time.sleep(0.2); GPIO.output(GREEN_LED, 0)
                time.sleep(1.0)
                continue   # visitor 処理はこれで終わり

            # ---------- Staff 打刻 ----------
            if result.get("registered") and result.get("usage_type") == "staff":
                name = result.get("assignee", "")
                scanned_name = name or uid          # 名前がなければ UID で区別
                state["name_display"] = scanned_name

                log_res = register_work_time(
                    uid, "collaborator", 1,
                    action="checkin",
                    device=DEVICE_NAME,
                    location=LOCATION_NAME
                )
                save_attendance_excel(scanned_name, uid, dt=now_time)
                state["status"] = "打刻成功" if log_res.get("message") else "打刻失敗"
                GPIO.output(GREEN_LED, 1); GPIO.output([RED_LED, YELLOW_LED], 0)
                beep()

                # ── 履歴管理
                hist = state["history"].setdefault(scanned_name, [])
                hist.insert(0, {"time": now_str, "timestamp": now_ts})
                del hist[MAX_HISTORY_LEN:]           # 最大保存数

                scan_count = len(hist)
                if scan_count == 2:                  # 2 回目 → 休憩開始
                    elapsed = hist[0]["timestamp"] - hist[1]["timestamp"]
                    if elapsed < BREAK_WINDOW_SEC:
                        state["break_time_left"] = int(BREAK_WINDOW_SEC - elapsed)
                        state["status"]          = "休憩中"
                    else:
                        state["break_time_left"] = None
                        state["status"]          = "休憩中 (時間外)"
                elif scan_count == 3:                # 3 回目 → 休憩終了
                    state["break_time_left"] = None
                    state["status"]          = "休憩終了"
                else:
                    state["break_time_left"] = None
                    state["status"]          = "打刻しました"
                # ★★★── 履歴管理 ここまで ──★★★

                continue    # 次のループへ

            # ---------- それ以外（usage_type 不明 or 未登録） ----------
            if result.get("usage_type") is not None:
                # usage_type はあるが staff / visitor 以外
                state["status"] = "⚠️ ユーザー登録をしてください。"
                GPIO.output([GREEN_LED], 0); GPIO.output([RED_LED, YELLOW_LED], 1)
                error_sound()
                save_attendance_excel("", uid, dt=now_time)
            else:
                # 完全未登録
                post_unregistered_scan(uid, device=DEVICE_NAME, location=LOCATION_NAME)
                state["status"] = "未登録カード"
                GPIO.output([GREEN_LED, YELLOW_LED], 0); GPIO.output(RED_LED, 1)
                error_sound()
                save_attendance_excel("", uid, dt=now_time)

        except Exception as e:
            print("[ERROR] ネット接続障害 or API エラー:", e)
            state["status"] = "ネット接続なし：UIDを保存"
            GPIO.output([GREEN_LED, RED_LED], 0); GPIO.output(YELLOW_LED, 1)
            error_sound()
            save_attendance_excel(None, uid, dt=now_time)

        time.sleep(0.1)

# ───── エントリーポイント ─────
if __name__ == "__main__":
    start_webserver()
    start_admin_web()
    main_loop()
