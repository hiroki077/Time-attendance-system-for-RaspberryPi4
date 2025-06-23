import ntplib
from datetime import datetime, timezone, timedelta

def get_jst_time():
    try:
        c = ntplib.NTPClient()
        res = c.request('ntp.nict.jp', version=3)
        utc_dt = datetime.utcfromtimestamp(res.tx_time)
        jst = utc_dt + timedelta(hours=9)
        return jst
    except Exception as e:
        print("NTP取得失敗:", e)
        # ローカル時刻
        return datetime.now(timezone(timedelta(hours=9)))
