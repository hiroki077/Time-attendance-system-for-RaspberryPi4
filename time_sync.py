from datetime import datetime, timedelta
import ntplib

def get_jst_time():
    try:
        client = ntplib.NTPClient()
        response = client.request('ntp.nict.jp', version=3)
        utc_time = datetime.utcfromtimestamp(response.tx_time)
        return utc_time + timedelta(hours=9)
    except Exception as e:
        print(f"[WARN] NTP取得失敗（ローカル時刻使用）: {e}")
        return datetime.now()

