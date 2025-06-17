import urequests
from ip_config import API_BASE

API_CHECK_URL = API_BASE + "/api/cards/register/"

def is_card_registered(uid):
    try:
        payload = {"uid": uid, "card_type": "nfc", "device": "pico-terminal"}
        headers = {"Content-Type": "application/json"}
        res = urequests.post(API_CHECK_URL, json=payload, headers=headers)
        data = res.json()
        print("REGISTER CHECK:", data)
        return data  
    except Exception as e:
        print("Card check error:", e)
        return {"registered": False, "error": str(e)}  
