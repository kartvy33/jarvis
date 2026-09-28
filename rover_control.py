"""Smart Rover control bridge for JARVIS.

JARVIS runs on the laptop and talks to the Smart Rover Flask server.
The rover server uses the same ROVER_API_KEY as the ESP32 telemetry link.
"""

import os
import json
import urllib.error
import urllib.request

ROVER_SERVER_URL = os.getenv("SMART_ROVER_URL", "http://127.0.0.1:5000").rstrip("/")
ROVER_KEY = os.getenv("SMART_ROVER_KEY", os.getenv("ROVER_API_KEY", ""))


def _request(command):
    payload = json.dumps({"command": command}).encode("utf-8")
    request = urllib.request.Request(
        f"{ROVER_SERVER_URL}/api/jarvis/command",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Rover-Key": ROVER_KEY,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=4) as response:
            data = json.loads(response.read().decode("utf-8"))
        if data.get("ok"):
            action = data.get("action")
            if action == "PATROL_START":
                return "Smart Rover autonomous patrol started."
            if action == "PATROL_STOP":
                return "Smart Rover patrol stopped."
            if action == "STOP":
                return "Smart Rover stopped."

            if action is None and isinstance(data.get("rover"), dict):
                status = data.get("rover", {}).get("status", {})
                parts = []
                if status.get("battery") is not None:
                    parts.append(f"battery {status['battery']} percent")
                if status.get("voltage") is not None:
                    parts.append(f"voltage {float(status['voltage']):.2f} volts")
                if status.get("temperature") is not None:
                    parts.append(f"temperature {float(status['temperature']):.1f} degrees Celsius")
                if status.get("humidity") is not None:
                    parts.append(f"humidity {float(status['humidity']):.1f} percent")
                if status.get("rain") is not None:
                    rain = status["rain"] is True or status["rain"] == 1 or str(status["rain"]).lower() in {"true", "1", "detected"}
                    parts.append("rain detected" if rain else "no rain detected")
                if status.get("latitude") is not None and status.get("longitude") is not None:
                    parts.append(f"GPS {status['latitude']:.6f}, {status['longitude']:.6f}")
                if parts:
                    return "Smart Rover status: " + ", ".join(parts) + "."
                return "Smart Rover status received."

            if action:
                return f"Smart Rover command sent: {action}."
            return "Smart Rover command completed."
        return data.get("error", "Smart Rover rejected the command.")
    except urllib.error.URLError as exc:
        return f"I cannot reach the Smart Rover server: {exc}"
    except Exception as exc:
        return f"Smart Rover error: {exc}"


def rover_command(command: str) -> str:
    text = command.lower().strip()
    for prefix in ("smart rover ", "smartrover ", "rover "):
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
            break

    aliases = {
        "forward": "forward",
        "move forward": "forward",
        "backward": "backward",
        "move backward": "backward",
        "reverse": "reverse",
        "left": "left",
        "turn left": "left",
        "right": "right",
        "turn right": "right",
        "stop": "stop",
        "emergency stop": "emergency stop",
        "patrol": "patrol start",
        "start patrol": "patrol start",
        "auto patrol": "patrol start",
        "start auto patrol": "patrol start",
        "stop patrol": "patrol stop",
        "manual mode": "patrol stop",
        "status": "status",
        "gps": "gps",
        "location": "location",
        "map": "map",
    }

    if text in {"help", "commands"}:
        return (
            "Rover commands: forward, backward, left, right, stop, "
            "start patrol, stop patrol, status, GPS, location, and map."
        )

    return _request(aliases.get(text, text))
