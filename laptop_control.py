"""Safe, explicit Windows laptop controls for JARVIS."""

import os
import subprocess
import time
from pathlib import Path

try:
    import pyautogui
except ImportError:
    pyautogui = None


def _need_pyautogui():
    if pyautogui is None:
        return "Laptop GUI control needs PyAutoGUI. Run: python -m pip install pyautogui"
    return None


def laptop_command(command: str) -> str:
    text = command.lower().strip()
    if text.startswith("laptop "):
        text = text[7:].strip()
    elif text.startswith("computer "):
        text = text[9:].strip()

    if text in {"help", "commands"}:
        return ("Laptop commands: laptop screenshot, laptop lock, laptop copy, "
                "laptop paste, laptop minimize, laptop show desktop, "
                "laptop volume up, laptop volume down, laptop mute.")

    err = _need_pyautogui()

    if text in {"lock", "lock laptop", "lock computer"}:
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=False)
        return "Locking the laptop."

    if text in {"screenshot", "take screenshot"}:
        if err:
            return err
        folder = Path.home() / "Pictures" / "JARVIS"
        folder.mkdir(parents=True, exist_ok=True)
        filename = folder / f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
        pyautogui.screenshot(str(filename))
        return f"Screenshot saved to {filename}."

    if text in {"copy", "copy selected text"}:
        if err:
            return err
        pyautogui.hotkey("ctrl", "c")
        return "Copied the selected item."

    if text in {"paste", "paste clipboard"}:
        if err:
            return err
        pyautogui.hotkey("ctrl", "v")
        return "Pasted."

    if text in {"minimize", "minimize window"}:
        if err:
            return err
        pyautogui.hotkey("alt", "space")
        pyautogui.press("n")
        return "Minimized the active window."

    if text in {"show desktop", "desktop"}:
        if err:
            return err
        pyautogui.hotkey("win", "d")
        return "Showing the desktop."

    if text in {"volume up", "increase volume"}:
        if err:
            return err
        pyautogui.press("volumeup")
        return "Volume increased."

    if text in {"volume down", "decrease volume"}:
        if err:
            return err
        pyautogui.press("volumedown")
        return "Volume decreased."

    if text in {"mute", "mute volume"}:
        if err:
            return err
        pyautogui.press("volumemute")
        return "Volume muted."

    return "I don't know that laptop command yet. Say laptop help."
