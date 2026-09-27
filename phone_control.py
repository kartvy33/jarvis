"""Android control through Google's Android Debug Bridge (ADB)."""

import os
import subprocess
import webbrowser
from urllib.parse import quote


ADB = os.getenv("ADB_PATH", "adb")


def _run(args, timeout=10):
    try:
        result = subprocess.run(
            [ADB, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = (result.stdout or result.stderr).strip()
        return result.returncode, output
    except FileNotFoundError:
        return 127, "ADB is not installed or is not in PATH."
    except subprocess.TimeoutExpired:
        return 124, "ADB timed out."


def phone_command(command: str) -> str:
    text = command.lower().strip()
    if text.startswith("phone "):
        text = text[6:].strip()
    elif text.startswith("android "):
        text = text[8:].strip()

    if text in {"help", "commands"}:
        return ("Phone commands: phone status, phone home, phone back, "
                "phone lock, phone volume up, phone volume down, "
                "phone mute, phone open youtube, phone open google.")

    code, output = _run(["devices"])
    if code != 0:
        return output
    lines = [line for line in output.splitlines() if "\tdevice" in line]
    if not lines:
        return "No Android phone is connected to JARVIS."

    if text in {"status", "check"}:
        return "Android phone is connected."

    actions = {
        "home": ["shell", "input", "keyevent", "KEYCODE_HOME"],
        "back": ["shell", "input", "keyevent", "KEYCODE_BACK"],
        "lock": ["shell", "input", "keyevent", "KEYCODE_POWER"],
        "volume up": ["shell", "input", "keyevent", "KEYCODE_VOLUME_UP"],
        "volume down": ["shell", "input", "keyevent", "KEYCODE_VOLUME_DOWN"],
        "mute": ["shell", "input", "keyevent", "KEYCODE_VOLUME_MUTE"],
    }

    if text in actions:
        code, output = _run(actions[text])
        return f"Phone command sent: {text}." if code == 0 else output

    urls = {
        "open youtube": "https://www.youtube.com",
        "open google": "https://www.google.com",
        "open github": "https://github.com",
    }
    if text in urls:
        uri = quote(urls[text], safe=":/?=&")
        code, output = _run(
            ["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", uri]
        )
        return f"Opening {text.replace('open ', '')} on the phone." if code == 0 else output

    if text.startswith("search "):
        query = text[7:].strip()
        if not query:
            return "Tell me what to search for."
        url = "https://www.google.com/search?q=" + quote(query)
        code, output = _run(
            ["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url]
        )
        return f"Searching the phone for {query}." if code == 0 else output

    return "I don't know that phone command yet. Say phone help."


if __name__ == "__main__":
    print(phone_command("phone status"))
