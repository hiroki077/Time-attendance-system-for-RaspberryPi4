
# NFC Attendance System with Raspberry Pi 4

## Overview
This project provides a **contactless attendance management system** using a Raspberry Pi 4, RC522 NFC reader, and Django backend via REST API.  
The system reads NFC cards, checks registration, logs attendance, and displays real-time status via a web server (Flask).  
It features visual/audio feedback with LEDs & a buzzer, break time management, and double-scan prevention.

---

## Features
- **NFC-based attendance:** Check-in/out with NFC cards or tags
- **Django REST API integration:** Register, verify, and log attendance
- **Real-time web interface** (Flask-based)
- **Visual and audio feedback:** LEDs and buzzer for status
- **Daily log reset** at 00:00 JST (server-side)
- **Automatic reboot** at 04:00 JST (cron or script)
- **Break time tracking:** 1-hour break support for staff
- **Double-scan prevention** (10 sec interval)

---

## Hardware Requirements
- Raspberry Pi 4 (Raspberry Pi OS)
- MFRC522 (or RC522) NFC Reader
- Buzzer (PWM-capable, e.g. GPIO 16)
- LEDs (Green: GPIO 27, Red: GPIO 22, Yellow: GPIO 17)
- NFC cards or tags
- Breadboard & jumper wires

---

## Pin Assignments
| Function   | GPIO Pin |
|------------|----------|
| Green LED  | 27       |
| Red LED    | 22       |
| Yellow LED | 17       |
| Buzzer     | 16       |

## RC522 <-> Raspberry Pi 4 Wiring

| RC522 Pin | Raspberry Pi Pin (BCM) | Physical Pin |
|:---------:|:----------------------:|:------------:|
| SDA       | GPIO8  (CE0)           | 24           |
| SCK       | GPIO11 (SCLK)          | 23           |
| MOSI      | GPIO10 (MOSI)          | 19           |
| MISO      | GPIO9  (MISO)          | 21           |
| IRQ       | Not Connected          | -            |
| GND       | GND                    | 6 (or 9,14,20,25,30,34,39) |
| RST       | GPIO26                 | 37           |
| 3.3V      | 3.3V                   | 1 (or 17)    |

- Be sure to use 3.3V for the RC522 (using 5V can damage the board).
- LEDs/Buzzer:  
  Green: GPIO27, Red: GPIO22, Yellow: GPIO17, Buzzer: GPIO16

---

## Software Structure
- `main.py` – Main loop (NFC scan, LED/Buzzer control, API, logic)
- `nfc_reader.py` – Reads UID from NFC tags
- `api_client.py` – Django REST API integration
- `webserver.py` – Flask-based real-time status page
- `device_config.py` – Fetches device/location info from backend
- `time_sync.py` – JST time sync

---

## Required Python Libraries
Install system & Python dependencies:
```sh
sudo apt update
sudo apt install python3-pip python3-dev git
pip3 install flask requests mfrc522 RPi.GPIO
```

If you use Django backend:
```sh
pip3 install django djangorestframework
```

---

## Setup Instructions
1. **Enable SPI**  
   `sudo raspi-config` → Interface Options → SPI → Enable

2. **(Optional) Set timezone to JST**  
   `sudo timedatectl set-timezone Asia/Tokyo`

3. **Clone repository & edit configs**  
   ```sh
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>
   # Edit device_config.py, webserver.py, etc. as needed
   ```

4. **Connect hardware as above**

5. **Start the system**
   ```sh
   python3 main.py
   ```

---

## Web Interface
- Open browser: `http://<Raspberry_Pi_IP>:<port>/`
- View real-time attendance logs and status.

---

## Notes
- Some scripts may need `sudo` to access GPIO/SPI.
- For startup at boot, use `systemd` or `cron`.
- Handle network/firewall settings to access web interface.

---

# NFC出勤管理システム (Raspberry Pi 4)

## 概要
このプロジェクトはRaspberry Pi 4・RC522 NFCリーダー・Djangoバックエンドを用いた**非接触型出勤管理システム**です。  
NFCカード読み取り、登録確認、出退勤打刻、Webリアルタイム表示（Flask）などを行います。  
LEDやブザーによるフィードバック、休憩管理、二重スキャン防止機能付き。

---

## 主な特徴
- **NFCカード打刻**（出勤・退勤）
- **Django REST API連携**（登録/確認/打刻記録）
- **リアルタイムWeb画面**（Flaskベース）
- **LED・ブザーによる状態通知**
- **毎日00:00に打刻履歴リセット**（サーバ側）
- **毎日04:00に自動再起動**（cron等）
- **1時間休憩管理**（スタッフ2回スキャンで判定）
- **二重スキャン防止**（10秒間隔）

---

## ハードウェア要件
- Raspberry Pi 4（Raspberry Pi OS）
- MFRC522（RC522）NFCリーダー
- ブザー（GPIO 16等）
- LED（緑: GPIO 27, 赤: GPIO 22, 黄: GPIO 17）
- NFCカード・タグ
- ブレッドボード・ジャンパ線

---

## ピンアサイン
| 機能      | GPIO番号 |
|-----------|----------|
| 緑LED     | 27       |
| 赤LED     | 22       |
| 黄LED     | 17       |
| ブザー     | 16       |

## RC522とRaspberry Pi 4の配線

| RC522端子 | Raspberry Piピン (BCM) | 物理ピン番号 |
|:---------:|:----------------------:|:------------:|
| SDA       | GPIO8  (CE0)           | 24           |
| SCK       | GPIO11 (SCLK)          | 23           |
| MOSI      | GPIO10 (MOSI)          | 19           |
| MISO      | GPIO9  (MISO)          | 21           |
| IRQ       | 接続不要               | -            |
| GND       | GND                    | 6 (or 9,14,20,25,30,34,39) |
| RST       | GPIO26                 | 37           |
| 3.3V      | 3.3V                   | 1 (or 17)    |

- RC522には必ず3.3Vを使用してください（5Vは故障原因となります）。
- LED・ブザー配線も上記のGPIO番号を参照

---

## ソフトウェア構成
- `main.py` – メイン制御（NFC, LED/ブザー, API, ロジック）
- `nfc_reader.py` – NFC UID読取
- `api_client.py` – Django REST API連携
- `webserver.py` – Flaskリアルタイム画面
- `device_config.py` – デバイス・場所情報取得
- `time_sync.py` – JST時刻同期

---

## 必要なPythonライブラリ
システム＆Python依存ライブラリ：
```sh
sudo apt update
sudo apt install python3-pip python3-dev git
pip3 install flask requests mfrc522 RPi.GPIO
```

Djangoバックエンド利用時：
```sh
pip3 install django djangorestframework
```

---

## セットアップ手順
1. **SPI有効化**  
   `sudo raspi-config` → インターフェース → SPI → 有効

2. **（任意）タイムゾーンをJSTに**  
   `sudo timedatectl set-timezone Asia/Tokyo`

3. **リポジトリをクローンし設定編集**  
   ```sh
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>
   # device_config.py等を編集
   ```

4. **ハード配線**

5. **システム起動**
   ```sh
   python3 main.py
   ```

---

## Webインターフェース
- ブラウザで `http://<ラズパイIP>:<ポート>/` を開くと打刻状況を確認できます。

---

## 補足
- GPIO/SPIアクセスにはsudoが必要な場合あり。
- 自動起動にはsystemdやcronを推奨。
- Web画面へはネットワーク・ファイアウォールの設定に注意。

---


