# JARVIS V1.5

JARVIS is a Python voice assistant for Windows with AI, maths, laptop control, Android control and ESP32 control.

## Install

Open Command Prompt:

```bat
cd C:\Users\acer\Desktop\JARVIS
python -m pip install -r requirements.txt
python main.py
```

## AI

Ollama is preferred because it can run locally.

```bat
ollama pull llama3.2:3b
```

OpenAI is optional. Keep API keys out of the source code.

## Laptop control

PyAutoGUI is used for mouse/keyboard-style Windows automation.

Say:
- "laptop help"
- "laptop screenshot"
- "laptop lock"
- "laptop copy"
- "laptop paste"
- "laptop minimize"
- "laptop show desktop"
- "laptop volume up"
- "laptop volume down"
- "laptop mute"

## Android phone control

JARVIS uses Google's Android Debug Bridge (ADB). Install Android SDK Platform Tools and make sure `adb` works in Command Prompt.

Check:

```bat
adb devices
```

For USB debugging, enable Developer Options and USB debugging on the phone and approve the computer.

Android 11+ also supports wireless debugging. Your computer and phone need to be on the same Wi-Fi network.

Say:
- "phone help"
- "phone status"
- "phone home"
- "phone back"
- "phone lock"
- "phone volume up"
- "phone volume down"
- "phone mute"
- "phone open YouTube"
- "phone open Google"
- "phone search ESP32"

## ESP32 control

The ESP32 runs `esp32/JARVIS_ESP32.ino`.

1. Open the sketch in Arduino IDE.
2. Change Wi-Fi SSID/password.
3. Change `JARVIS_TOKEN`.
4. Upload it to the ESP32.
5. Open Serial Monitor at 115200.
6. Note the ESP32 IP address.
7. In the JARVIS Command Prompt set:

```bat
setx ESP32_IP "192.168.1.123"
setx ESP32_TOKEN "your-token"
```

Close and reopen Command Prompt after `setx`.

Then say:
- "ESP32 help"
- "ESP32 status"
- "ESP32 on"
- "ESP32 off"
- "ESP32 restart"

The ESP32 and laptop should normally be on the same LAN. Arduino-ESP32 supports Wi-Fi station mode and HTTP servers.

## Important security note

The ESP32 controller is intended for a trusted local network. Change the token and do not expose its HTTP control port directly to the public Internet.

ADB is powerful. Only enable debugging for a phone/computer you trust.

## Project structure

```text
jarvis/
├── main.py
├── ai.py
├── math_engine.py
├── laptop_control.py
├── phone_control.py
├── esp32_control.py
├── esp32/
│   └── JARVIS_ESP32.ino
├── requirements.txt
├── .env.example
├── .gitignore
└── LICENSE
```

Future V1.6 targets:
- phone as a JARVIS microphone
- ESP32/ESP32-S3 microphone/audio terminal
- offline speech recognition
- richer Windows automation
- ESP32 rover/device profiles
- wake-word detection
