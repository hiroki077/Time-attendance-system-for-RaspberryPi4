from flask import Flask, send_from_directory, request, jsonify
import os
from time_sync import get_jst_time
from device_config import fetch_device_info
from ip_config import API_BASE

print(API_BASE)

app = Flask(
    __name__,
    static_folder="www/static",
    template_folder="www"
)

state = {
    "uid_display": "---",
    "name_display": "---",
    "scan_time_display": "---",
    "status": "Waiting...",
    "history": {},
    "break_time_left": None,
    "customer_state": "Idle",
}

@app.route("/data")
def data():
    info = fetch_device_info("raspi4")  # ←毎回DB最新値を取得
    now = get_jst_time()
    now_str = now.strftime("%Y/%m/%d %H:%M:%S")
    now_unixtime = int(now.timestamp())
    d = {
        "uid": state.get("uid_display", "---"),
        "name": state.get("name_display", "---"),
        "scan_time": state.get("scan_time_display", "---"),
        "status": state.get("status", "---"),
        "now": now_str,
        "now_unixtime": now_unixtime,
        "history": state.get("history", {}),
        "break_time_left": state.get("break_time_left", None),
        "primary_ip": info['primary_ip'],
        "device_name": info['device_name'],
        "location_name": info['location_name']
    }
    return jsonify(d)




@app.route("/")
@app.route("/index.html")
def index():
    info = fetch_device_info("raspi4")
    is_primary = (request.remote_addr == info["primary_ip"])
    with open(os.path.join("www", "index.html"), encoding="utf-8") as f:
        html = f.read()
    host_ip = request.host.split(":")[0]           # IPだけを抽出
    polling_tag = '<script src="/static/js/index_polling.js"></script>' if is_primary else ""
    html = html.replace("__POLLING_SCRIPT__", polling_tag)
    html = html.replace("__HOST_IP__", host_ip)
    html = html.replace("__API_BASE__", API_BASE)
    print("★ API_BASE:", API_BASE)
    print("★ html出力サンプル：", html[:400])  
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}






@app.route("/attendance")
def attendance():
    info = fetch_device_info("raspi4")
    is_primary = (request.remote_addr == info["primary_ip"])
    with open(os.path.join("www", "attendance.html"), encoding="utf-8") as f:
        html = f.read()
    host_ip = request.host.split(":")[0]
    html = html.replace("__HOST_IP__", host_ip)
    polling_tag = '<script src="/static/js/attendance_polling.js"></script>' if is_primary else ""
    html = html.replace("__POLLING_SCRIPT__", polling_tag)
    html = html.replace("__API_BASE__", API_BASE)
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("www/static", filename)

@app.route("/state")
def state_api():
    info = fetch_device_info("raspi4")
    cust_state = state.get("customer_state", "Idle")
    return jsonify({
        "customer_state": cust_state,
        "primary_ip": info["primary_ip"],
        "device_name": info["device_name"],
        "location_name": info["location_name"]
    })

@app.route("/admin/login", methods=["GET", "POST"])
def login():
    host_ip = request.host.split(":")[0]
    if request.method == "POST":
        user = request.form.get("username")
        pw = request.form.get("password")
        if user == ADMIN_USER and pw == ADMIN_PASS:
            session["admin"] = True
            return redirect("/admin/device_info")
        else:
            return render_template_string(LOGIN_TEMPLATE.replace("__HOST_IP__", host_ip), error="ログイン失敗！")
    return render_template_string(LOGIN_TEMPLATE.replace("__HOST_IP__", host_ip))




@app.route("/admin/device_info", methods=["GET", "POST"])
def device_info():
    if not session.get("admin"):
        return redirect("/admin/login")
    device_name = "raspi4"
    msg = ""
    if request.method == "POST":
        location_name = request.form.get("location_name")
        primary_ip = request.form.get("primary_ip")
        update_device_info(device_name, location_name, primary_ip)
        msg = "更新しました！"
    info = fetch_device_info(device_name)
    host_ip = request.host.split(":")[0]
    return render_template_string(DEVICE_TEMPLATE.replace("__HOST_IP__", host_ip), info=info, msg=msg)





def start_webserver(run_async=True, port=8080):
    if run_async:
        import threading
        threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)).start()
    else:
        app.run(host="0.0.0.0", port=port)


