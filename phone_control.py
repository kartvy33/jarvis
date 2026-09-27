"""Android control through ADB.

The module prefers one explicit wireless ADB target when JARVIS_ADB_DEVICE is set.
This avoids "more than one device/emulator" when Android exposes both the IP
connection and the mDNS connection for the same phone.
"""

import os
import re
import subprocess
from urllib.parse import quote

ADB = os.getenv("ADB_PATH", "adb")
ADB_DEVICE = os.getenv("JARVIS_ADB_DEVICE", "").strip()


def _run(args, timeout=15):
    """Run adb, targeting JARVIS_ADB_DEVICE when configured."""
    try:
        command = [ADB]
        if ADB_DEVICE:
            command += ["-s", ADB_DEVICE]
        command += list(args)
        result = subprocess.run(
            command,
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


def _devices():
    code, output = _run(["devices"])
    if code != 0:
        return code, output, []
    devices = []
    for line in output.splitlines():
        if line.strip().endswith("\tdevice"):
            devices.append(line.split()[0])
    return 0, output, devices


def _target_ready():
    code, output, devices = _devices()
    if code != 0:
        return False, output
    if not devices:
        return False, "No Android phone is connected to JARVIS."
    if not ADB_DEVICE and len(devices) > 1:
        return False, (
            "More than one Android device is connected. Set JARVIS_ADB_DEVICE "
            "to the wireless device address, for example 10.254.0.105:40445."
        )
    if ADB_DEVICE and ADB_DEVICE not in devices:
        return False, (
            f"JARVIS is configured for {ADB_DEVICE}, but that device is not connected. "
            "Check adb devices or update JARVIS_ADB_DEVICE."
        )
    return True, ""


def _open_url(url):
    return _run([
        "shell", "am", "start", "-a", "android.intent.action.VIEW",
        "-d", url
    ])


def _keyevent(key):
    return _run(["shell", "input", "keyevent", key])


def _settings(action):
    return _run([
        "shell", "am", "start", "-a", action
    ])


def _package_from_text(value):
    value = value.strip()
    # Package names are the safest way to address arbitrary installed apps.
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+", value):
        return value
    aliases = {
        "youtube": "com.google.android.youtube",
        "chrome": "com.android.chrome",
        "google": "com.google.android.googlequicksearchbox",
        "maps": "com.google.android.apps.maps",
        "gmail": "com.google.android.gm",
        "whatsapp": "com.whatsapp",
        "telegram": "org.telegram.messenger",
        "instagram": "com.instagram.android",
        "github": "com.github.android",
    }
    return aliases.get(value.lower())


def _open_app(name):
    package = _package_from_text(name)
    if not package:
        return (
            "I need the Android package name for that app. "
            "For example: phone open app com.whatsapp. "
            "Common aliases such as YouTube, Chrome, WhatsApp, Telegram and Maps are supported."
        )
    code, output = _run([
        "shell", "monkey", "-p", package, "-c",
        "android.intent.category.LAUNCHER", "1"
    ])
    return f"Opened {name}." if code == 0 else output


def _permission(action, app, permission):
    package = _package_from_text(app) or app.strip()
    if not package:
        return "Tell me the app package name."
    permission = permission.strip()
    if not permission:
        return "Tell me the Android permission, for example android.permission.CAMERA."
    if action == "allow":
        code, output = _run(["shell", "pm", "grant", package, permission])
    else:
        code, output = _run(["shell", "pm", "revoke", package, permission])
    if code == 0:
        return f"Permission {action}ed: {permission} for {package}."
    return output


def _ui_dump():
    path = "/sdcard/window.xml"
    code, output = _run(["shell", "uiautomator", "dump", path])
    if code != 0:
        return output
    code, xml = _run(["shell", "cat", path])
    return xml if code == 0 else output


def phone_command(command: str) -> str:
    text = command.lower().strip()
    if text.startswith("phone "):
        text = text[6:].strip()
    elif text.startswith("android "):
        text = text[8:].strip()

    if text in {"help", "commands"}:
        return (
            "Phone commands: status, home, back, lock, volume up, volume down, mute; "
            "open app <package>; open youtube/chrome/maps/gmail/whatsapp/telegram; "
            "search <query>; search current app <query>; "
            "wifi on/off, bluetooth on/off, data on/off, torch on/off, hotspot; "
            "settings wifi/bluetooth/data/hotspot; tap x y; swipe x1 y1 x2 y2; "
            "type <text>; permission allow/deny <package> <permission>; "
            "ui dump."
        )

    ready, message = _target_ready()
    if not ready:
        return message

    if text in {"status", "check"}:
        return f"Android phone is connected. Target: {ADB_DEVICE or 'single detected device'}."

    actions = {
        "home": "KEYCODE_HOME",
        "back": "KEYCODE_BACK",
        "lock": "KEYCODE_POWER",
        "volume up": "KEYCODE_VOLUME_UP",
        "volume down": "KEYCODE_VOLUME_DOWN",
        "mute": "KEYCODE_VOLUME_MUTE",
        "recent apps": "KEYCODE_APP_SWITCH",
    }
    if text in actions:
        code, output = _keyevent(actions[text])
        return f"Phone command sent: {text}." if code == 0 else output

    if text.startswith("open app "):
        return _open_app(text[9:].strip())
    if text.startswith("launch app "):
        return _open_app(text[11:].strip())

    # Friendly app aliases.
    if text.startswith("open "):
        app = text[5:].strip()
        if app in {"youtube", "chrome", "google", "maps", "gmail", "whatsapp", "telegram", "instagram", "github"}:
            return _open_app(app)

    # Direct Android settings / controls.
    control_actions = {
        "wifi on": ["shell", "svc", "wifi", "enable"],
        "wifi off": ["shell", "svc", "wifi", "disable"],
        "bluetooth on": ["shell", "svc", "bluetooth", "enable"],
        "bluetooth off": ["shell", "svc", "bluetooth", "disable"],
        "data on": ["shell", "svc", "data", "enable"],
        "mobile data on": ["shell", "svc", "data", "enable"],
        "data off": ["shell", "svc", "data", "disable"],
        "mobile data off": ["shell", "svc", "data", "disable"],
        "torch on": ["shell", "cmd", "statusbar", "expand-notifications"],
        "torch off": ["shell", "cmd", "statusbar", "collapse"],
    }
    if text in control_actions:
        code, output = _run(control_actions[text])
        if text.startswith("torch"):
            return (
                "Torch control is Android-version dependent. I opened notifications; "
                "use the torch tile if direct shell control is blocked."
            )
        return f"Phone {text} command sent." if code == 0 else output

    settings_map = {
        "settings wifi": "android.settings.WIFI_SETTINGS",
        "settings bluetooth": "android.settings.BLUETOOTH_SETTINGS",
        "settings data": "android.settings.DATA_USAGE_SETTINGS",
        "settings hotspot": "android.settings.TETHER_SETTINGS",
        "hotspot": "android.settings.TETHER_SETTINGS",
        "open wifi settings": "android.settings.WIFI_SETTINGS",
        "open bluetooth settings": "android.settings.BLUETOOTH_SETTINGS",
        "open hotspot settings": "android.settings.TETHER_SETTINGS",
    }
    if text in settings_map:
        code, output = _settings(settings_map[text])
        return "Opening the requested Android settings." if code == 0 else output

    urls = {
        "open youtube": "https://www.youtube.com",
        "open google": "https://www.google.com",
        "open github": "https://github.com",
    }
    if text in urls:
        code, output = _open_url(urls[text])
        return f"Opening {text[5:]} on the phone." if code == 0 else output

    if text.startswith("search current app "):
        query = text[19:].strip()
        if not query:
            return "Tell me what to search for."
        # Many apps respond to Android's SEARCH key. For apps that do not,
        # JARVIS can still open the keyboard/search UI manually.
        _keyevent("KEYCODE_SEARCH")
        code, output = _run(["shell", "input", "text", quote(query, safe="")])
        if code == 0:
            _keyevent("KEYCODE_ENTER")
            return f"Searching the current app for {query}."
        return output

    if text.startswith("search "):
        query = text[7:].strip()
        if not query:
            return "Tell me what to search for."
        url = "https://www.google.com/search?q=" + quote(query)
        code, output = _open_url(url)
        return f"Searching Google for {query}." if code == 0 else output

    if text.startswith("tap "):
        parts = text[4:].split()
        if len(parts) != 2:
            return "Use: phone tap X Y"
        try:
            x, y = int(parts[0]), int(parts[1])
        except ValueError:
            return "X and Y must be numbers."
        code, output = _run(["shell", "input", "tap", str(x), str(y)])
        return "Tapped the requested screen position." if code == 0 else output

    if text.startswith("swipe "):
        parts = text[6:].split()
        if len(parts) not in {4, 5}:
            return "Use: phone swipe X1 Y1 X2 Y2 [duration_ms]"
        try:
            nums = [int(x) for x in parts]
        except ValueError:
            return "Swipe coordinates must be numbers."
        if len(nums) == 4:
            nums.append(300)
        code, output = _run(["shell", "input", "swipe", *map(str, nums)])
        return "Swipe sent." if code == 0 else output

    if text.startswith("type "):
        value = text[5:].strip()
        if not value:
            return "Tell me what text to type."
        code, output = _run(["shell", "input", "text", quote(value, safe="")])
        return "Text entered." if code == 0 else output

    if text == "ui dump":
        xml = _ui_dump()
        if xml.startswith("<"):
            return "UI dump retrieved. For large screens, use the file directly or ask for a specific UI element."
        return xml

    for prefix, action in (
        ("permission allow ", "allow"),
        ("permission deny ", "deny"),
        ("allow permission ", "allow"),
        ("deny permission ", "deny"),
    ):
        if text.startswith(prefix):
            rest = text[len(prefix):].strip()
            parts = rest.split(maxsplit=1)
            if len(parts) != 2:
                return "Use: phone permission allow PACKAGE PERMISSION"
            return _permission(action, parts[0], parts[1])

    return (
        "I don't know that phone command yet. Say phone help. "
        "For arbitrary apps, use the app package name."
    )


if __name__ == "__main__":
    print(phone_command("phone status"))
