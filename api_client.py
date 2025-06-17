import requests
from ip_config import API_BASE

def is_card_registered(uid):
    try:
        payload = {"uid": uid, "card_type": "nfc", "device": "raspi4"}
        headers = {"Content-Type": "application/json"}
        res = requests.post(f"{API_BASE}/rukicard_api/check/", json=payload, headers=headers)
        return res.json()
    except Exception as e:
        print("Card check error:", e)
        return {"registered": False}

def register_work_time(uid, assignee_type, assignee_id, action="checkin", device="raspi4", location=""):
    try:
        payload = {
            "card_uid": uid,
            "assignee_type": assignee_type,
            "assignee_id": assignee_id,
            "action": action,
            "device": device,
            "location": location
        }
        headers = {"Content-Type": "application/json"}
        res = requests.post(f"{API_BASE}/rukicard_api/insertwt/", json=payload, headers=headers)
        return res.json()
    except Exception as e:
        print("register_work_time error:", e)
        return {"message": "Error"}

def post_unregistered_scan(uid, device="raspi4", location=""):
    try:
        payload = {
            "uid": uid,
            "device": device,
            "card_type": "nfc",
            "location": location
        }
        headers = {"Content-Type": "application/json"}
        res = requests.post(f"{API_BASE}/rukicard_api/log/", json=payload, headers=headers)
        return res.json()
    except Exception as e:
        print("Unreg scan POST error:", e)
        return {"message": "Error"}
