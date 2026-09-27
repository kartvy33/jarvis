"""ESP32 control over HTTP on the local network."""

import os
import urllib.error
import urllib.request
from urllib.parse import quote


ESP32_IP = os.getenv("ESP32_IP", "")
ESP32_PORT = os.getenv("ESP32_PORT", "80")
ESP32_TOKEN = os.getenv("ESP32_TOKEN", "change-me")


def _request(path: str) -> str:
    if not ESP32_IP:
        return "ESP32 is not configured. Set ESP32_IP to your ESP32 IP address."

    url = f"http://{ESP32_IP}:{ESP32_PORT}{path}"
    if ESP32_TOKEN:
        separator = "&" if "?" in url else "?"
        url += separator + "token=" + quote(ESP32_TOKEN)

    try:
        with urllib.request.urlopen(url, timeout=4) as response:
            return response.read().decode("utf-8", errors="replace").strip()
    except urllib.error.URLError as exc:
        return f"I could not reach the ESP32: {exc}"


def esp32_command(command: str) -> str:
    text = command.lower().strip()
    if text.startswith("esp32 "):
        text = text[6:].strip()
    elif text.startswith("esp "):
        text = text[4:].strip()

    if text in {"help", "commands"}:
        return ("ESP32 commands: ESP32 status, ESP32 on, ESP32 off, "
                "ESP32 led on, ESP32 led off, ESP32 restart.")

    routes = {
        "on": "/on",
        "led on": "/on",
        "off": "/off",
        "led off": "/off",
        "status": "/status",
        "restart": "/restart",
    }

    if text not in routes:
        return "I don't know that ESP32 command yet. Say ESP32 help."

    return _request(routes[text])
