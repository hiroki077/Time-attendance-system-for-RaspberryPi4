import pymysql
from flask import Flask, render_template_string, request, redirect, session

# --- DB関数 ---
def fetch_device_info(host="raspi4"):
    conn = pymysql.connect(
        host='localhost',
        user='ruki',
        password='ruki03',
        database='attendance',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM device_info WHERE host=%s"
            cursor.execute(sql, (host,))
            return cursor.fetchone()
    finally:
        conn.close()

def update_device_info(host, device_name, location_name, primary_ip):
    conn = pymysql.connect(
        host='localhost',
        user='ruki',
        password='ruki03',
        database='attendance',
        charset='utf8mb4'
    )
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE device_info SET device_name=%s, location_name=%s, primary_ip=%s WHERE host=%s"
            cursor.execute(sql, (device_name, location_name, primary_ip, host))
            conn.commit()
    finally:
        conn.close()

# --- Flask ---
ADMIN_USER = "ruki"
ADMIN_PASS = "ruki03"

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html><body>
  <a href="http://__HOST_IP__:8080/index.html" id="main-link">
    メイン画面へ
  </a>
  <h2>管理者ログイン</h2>
  {% if error %}<p style="color:red">{{ error }}</p>{% endif %}
  <form method="post">
    ユーザー名: <input name="username"><br>
    パスワード: <input name="password" type="password"><br>
    <input type="submit" value="ログイン">
  </form>
</body></html>
"""

DEVICE_TEMPLATE = """
<!DOCTYPE html>
<html><body>
  <a href="http://__HOST_IP__:8080/index.html" id="main-link">
    メイン画面へ
  </a>
  <h2>デバイス情報編集</h2>
  <p><a href="/admin/logout">ログアウト</a></p>
  {% if msg %}<p style="color:green">{{ msg }}</p>{% endif %}
  <form method="post">
    ホスト名: <input name="host" value="{{ info.host or 'raspi4' }}" readonly><br>
    デバイス名: <input name="device_name" value="{{ info.device_name or '' }}"><br>
    ロケーション: <input name="location_name" value="{{ info.location_name or '' }}"><br>
    Primary IP: <input name="primary_ip" value="{{ info.primary_ip or '' }}"><br>
    <input type="submit" value="更新">
  </form>
</body></html>
"""

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
    host_ip = request.host.split(":")[0]
    msg = ""
    info = fetch_device_info("raspi4")
    if request.method == "POST":
        # hostは変更不可
        device_name = request.form.get("device_name", "")
        location_name = request.form.get("location_name", "")
        primary_ip = request.form.get("primary_ip", "")
        update_device_info("raspi4", device_name, location_name, primary_ip)
        msg = "更新しました！"
        info = fetch_device_info("raspi4")
    return render_template_string(DEVICE_TEMPLATE.replace("__HOST_IP__", host_ip), info=info or {}, msg=msg)

@app.route("/admin/logout")
def logout():
    session.pop("admin", None)
    return redirect("/admin/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090, debug=True)