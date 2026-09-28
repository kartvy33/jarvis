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
