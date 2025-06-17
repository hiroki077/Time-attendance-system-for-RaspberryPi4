# NFC Attendance System with Raspberry Pi Pico W

This project provides a contactless attendance (check-in/out) solution using a Raspberry Pi Pico W and NFC cards, integrated with a Django backend via a REST API. The Pico W scans NFC tags, verifies registration, and logs check-ins/check-outs, while offering a real-time status web interface.

## Features

- **NFC-based attendance** (check-in and check-out)  
- **Django API integration** for user data and log submission  
- **Real-time web interface** hosted on the Pico W  
- **Visual and audio feedback** using LEDs and a buzzer  
- **Daily log reset** at 00:00 JST  
- **Break time management** (tracks 1-hour rest period)  
- **Automatic reboot** every day at 04:00 JST  

## Hardware Requirements

- Raspberry Pi Pico W  
- MFRC522 (or RC522) NFC Reader  
- Buzzer (PWM-capable)  
- LEDs (green, red, yellow)  
- NFC cards or tags  

## Software Structure

- `main.py`  
  - Main loop: Wi-Fi setup, NFC scanning, state management, scheduled reboot  
- `wifi_config.py`  
  - Stores your Wi-Fi SSID and password  
- `time_sync.py`  
  - Synchronizes time via NTP (sets to JST)  
- `nfc_reader.py`  
  - Reads UID from NFC tags  
- `api_client.py`  
  - Sends HTTP requests to the Django REST API  
- `webserver.py`  
  - Hosts a simple HTTP server for real-time status display  

## Django API Endpoints

1. **Get user info by UID**  
   ```
   GET /api/pico/user/<uid>/
   ```  
   **Response example**:
   ```json
   {
     "uid": "0x880401c04d",
     "name": "Alice Tanaka",
     "is_registered": true
   }
   ```

2. **Submit attendance log**  
   ```
   POST /api/pico/log/
   ```  
   **Request body example**:
   ```json
   {
     "uid": "0x880401c04d",
     "action": "checkin"
   }
   ```  
   - **Response**:  
     - HTTP 200 OK on success  
     - HTTP 400/404 on error  

### Example `curl` Test

```bash
curl -X POST http://192.168.24.42:8000/api/pico/log/      -H "Content-Type: application/json"      -d '{"uid": "0x880401c04d", "action": "checkin"}'
```

---

## Setup Instructions

### 1. Flash MicroPython firmware

1. Download the latest MicroPython UF2 for Pico W from [micropython.org](https://micropython.org/download/rp2-pico-w/).
2. Hold down the BOOTSEL button on the Pico W, then connect it via USB.
3. Drag and drop the downloaded UF2 file onto the Pico W drive.

### 2. Clone this repository

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 3. Edit Wi-Fi credentials

1. Open `wifi_config.py` in a text editor.
2. Update the values:
   ```python
   WIFI_SSID = "YOUR_SSID"
   WIFI_PASSWORD = "YOUR_PASSWORD"
   ```

### 4. Copy files to the Pico W

Use Thonny (or any other MicroPython upload tool) to transfer the following files into the root of the Pico’s filesystem:

- `main.py`
- `wifi_config.py`
- `time_sync.py`
- `nfc_reader.py`
- `api_client.py`
- `webserver.py`

### 5. Power on the Pico W

1. After uploading all files, unplug and re-plug the Pico W.
2. The Pico W will automatically:
   - Connect to Wi-Fi
   - Sync time to JST
   - Start the web server
   - Await NFC scans

---

## Web Interface

1. Open a browser and navigate to:  
   ```
   http://<Pico_IP>/
   ```
2. The page displays:
   - Current JST time  
   - Last scanned UID  
   - Associated user name  
   - Scan timestamp  
   - Status (e.g., “Check-in successful” or error messages)  

---

## LEDs & Buzzer Feedback

- **Green LED**: Successful check-in or check-out  
- **Red LED**: Error (unregistered card, API failure, etc.)  
- **Yellow LED**: Waiting for scan  
- **Buzzer**:
  - Short beep on success  
  - Series of beeps on error  

---

## Scheduled Tasks

- **Daily reboot at 04:00 JST**  
  - Implemented in `main.py` using the internal RTC.  
- **Daily log reset at 00:00 JST**  
  - Logs stored on the server are cleared automatically via a Django management command (configured on the backend).  
