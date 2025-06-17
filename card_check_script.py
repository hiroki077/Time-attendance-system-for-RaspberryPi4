from machine import Pin, PWM
from wifi_config import WIFI_SSID, WIFI_PASSWORD
from time_sync import connect_wifi, sync_time, get_jst_time
from nfc_reader import read_uid
from webserver import start_webserver
from api_client import post_log_with_response
from card_check import is_card_registered 
import time

# --- ピン初期化 ---
green_led = Pin(14, Pin.OUT)
red_led = Pin(15, Pin.OUT)
yellow_led = Pin(0, Pin.OUT)
buzzer_pwm = PWM(Pin(16))

# 成功音（ピッ）
def success_sound():
    buzzer_pwm.freq(1200)
    buzzer_pwm.duty_u16(30000)
    time.sleep(0.1)
    buzzer_pwm.duty_u16(0)

# エラー音（ビビビ）
def error_sound():
    for _ in range(3):
        buzzer_pwm.freq(600)
        buzzer_pwm.duty_u16(30000)
        time.sleep(0.05)
        buzzer_pwm.duty_u16(0)
        time.sleep(0.05)

# 読み取り確認音（ポッ）
def beep(frequency=1000, duration=0.1):
    buzzer_pwm.freq(frequency)
    buzzer_pwm.duty_u16(30000)
    time.sleep(duration)
    buzzer_pwm.duty_u16(0)

# 初期状態：黄色LED点灯
green_led.off()
red_led.off()
yellow_led.on()
buzzer_pwm.duty_u16(0)

# 表示用データ
state = {
    "uid": "---",
    "name": "---",
    "scan_time": "---",
    "status": "Waiting..."
}

# Wi-Fi接続 & 時刻同期
if connect_wifi(WIFI_SSID, WIFI_PASSWORD):
    sync_time()

# Webサーバー起動（状態表示用）
start_webserver(state)

# メインループ
while True:
    uid = read_uid()
    if uid:
        beep()  # 読み取り確認音

        result = is_card_registered(uid)  # ← dict を想定

        if result.get("registered") is True:
            # 正常登録カード → ログ送信
            t = get_jst_time()
            time_str = "{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(*t[:6])
            state["uid"] = uid
            state["scan_time"] = time_str

            response = post_log_with_response(uid, "checkin")

            if "error" in response:
                state["status"] = "Error - " + response["error"]
                state["name"] = "Unknown"
                red_led.on()
                green_led.off()
                yellow_led.off()
                error_sound()
            else:
                state["status"] = "Success - " + response.get("message", "Logged")
                state["name"] = response.get("assignee", "Unknown")
                green_led.on()
                red_led.off()
                yellow_led.off()
                success_sound()

        elif result.get("message") == "Card already registered in waiting list":
            # カードあり・ユーザー割り当てなし
            state["status"] = "User registration required"
            state["name"] = "Unknown"
            red_led.on()
            green_led.off()
            yellow_led.off()
            error_sound()

        else:
            # 完全に未登録 or 通信エラー
            state["status"] = "Error - Card not registered"
            state["name"] = "Unknown"
            red_led.on()
            green_led.off()
            yellow_led.off()
            error_sound()

        time.sleep(1)

        # 状態リセット
        green_led.off()
        red_led.off()
        yellow_led.on()
        state["status"] = "Waiting..."
        state["name"] = "---"
        state["uid"] = "---"
        state["scan_time"] = "---"

    # 毎朝4時に自動再起動
    if time.localtime()[3] == 4 and time.localtime()[4] == 0:
        import machine
        machine.reset()
