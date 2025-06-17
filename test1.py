import network
import time
import urequests

ssid = "Buffalo-G-BA10"
password = "8rctsrsex55sy"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

print("🔍 スキャン中...")
nets = wlan.scan()
for net in nets:
    print("見つかったSSID:", net[0].decode(), "| RSSI:", net[3])

print(f"📡 '{ssid}' に接続を試みます...")
wlan.connect(ssid, password)

for i in range(15):
    status = wlan.status()
    print(f"⏳ 試行 {i+1} 回目 | 接続ステータス: {status}")
    if status == 2:  # ← ここを修正！
        break
    time.sleep(1)

if wlan.status() != 2:
    print("❌ Wi-Fi接続に失敗")
    print("📶 最終ステータスコード:", wlan.status())
else:
    print("✅ Wi-Fi接続成功:", wlan.ifconfig())

    try:
        print("🌐 HTTP接続テスト...")
        res = urequests.get("http://example.com")
        print("✅ HTTP ステータスコード:", res.status_code)
        print("レスポンス（先頭100文字）:", res.text[:100])
        res.close()
    except Exception as e:
        print("❌ HTTP接続失敗:", e)
