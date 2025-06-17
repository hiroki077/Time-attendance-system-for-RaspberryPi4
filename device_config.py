import pymysql

def fetch_device_info(device_name="raspi4"):
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
            sql = "SELECT * FROM device_info WHERE device_name=%s"
            cursor.execute(sql, (device_name,))
            return cursor.fetchone()
    finally:
        conn.close()

def update_device_info(device_name, location_name, primary_ip):
    conn = pymysql.connect(
        host='localhost',
        user='ruki',
        password='ruki03',
        database='attendance',
        charset='utf8mb4'
    )
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE device_info SET location_name=%s, primary_ip=%s WHERE device_name=%s"
            cursor.execute(sql, (location_name, primary_ip, device_name))
            conn.commit()
    finally:
        conn.close()
