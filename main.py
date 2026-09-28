"""
JARVIS V1.5
Hybrid Windows voice assistant with laptop, Android and ESP32 control.
"""

import datetime
import os
import sys
import subprocess
import webbrowser
from urllib.parse import quote

import pyttsx3
import speech_recognition as sr

from ai import ask_ai, ai_status
from math_engine import calculate, looks_like_math
from laptop_control import laptop_command
from phone_control import phone_command
from esp32_control import esp32_command
from rover_control import rover_command


engine = pyttsx3.init()
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)
recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.7


def speak(text: str) -> None:
    text = str(text).strip()
    if text:
        print(f"JARVIS: {text}")
        engine.say(text)
        engine.runAndWait()


def listen() -> str:
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.35)
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=15)
    except sr.WaitTimeoutError:
        return ""
    except OSError as exc:
        speak(f"I cannot access the microphone. {exc}")
        return ""
    try:
        text = recognizer.recognize_google(audio)
        print(f"You: {text}")
        return text.lower().strip()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as exc:
        speak(f"Speech recognition service error: {exc}")
        return ""


def open_url(url: str, name: str) -> None:
    webbrowser.open(url)
    speak(f"Opening {name}.")


def open_app(command: str, name: str) -> None:
    try:
        subprocess.Popen(command, shell=True)
        speak(f"Opening {name}.")
    except Exception as exc:
        speak(f"I could not open {name}: {exc}")


def handle_math(command: str) -> bool:
    expression = command
    for prefix in ("calculate ", "what is ", "solve ", "compute "):
        if expression.startswith(prefix):
            expression = expression[len(prefix):].strip()
            break
    if not expression or not looks_like_math(expression):
        return False
    try:
        speak(f"The answer is {calculate(expression)}.")
    except ValueError as exc:
        speak(f"I could not calculate that: {exc}")
    return True


def handle_command(command: str) -> bool:
    if not command:
        return True

    if command in {"exit", "quit", "stop", "shutdown", "goodbye", "close jarvis"}:
        speak("Shutting down. Goodbye.")
        return False

    if command in {"time", "what time is it", "tell me the time"} or "current time" in command:
        speak(f"The time is {datetime.datetime.now().strftime('%I:%M %p')}.")
        return True

    if command in {"date", "today", "what is the date", "what day is it"}:
        speak(f"Today is {datetime.datetime.now().strftime('%A, %d %B %Y')}.")
        return True

    # Laptop / Windows control.
    if command.startswith(("laptop ", "computer ")):
        result = laptop_command(command)
        speak(result)
        return True

    # Android phone control through ADB.
    if command.startswith(("phone ", "android ")):
        result = phone_command(command)
        speak(result)
        return True

    # Smart Rover control through the laptop rover server.\n    if command.startswith(("rover ", "smart rover ", "smartrover ")):\n        result = rover_command(command)\n        speak(result)\n        return True\n\n    # ESP32 control over local Wi-Fi HTTP.
    if command.startswith(("esp32 ", "esp ")):
        result = esp32_command(command)
        speak(result)
        return True

    if command in {"open google", "google"}:
        open_url("https://www.google.com", "Google")
        return True
    if command in {"open youtube", "youtube"}:
        open_url("https://www.youtube.com", "YouTube")
        return True
    if command in {"open github", "github"}:
        open_url("https://github.com", "GitHub")
        return True
    if command in {"open chrome", "chrome"}:
        open_app("start chrome", "Chrome")
        return True
    if command in {"open notepad", "notepad"}:
        open_app("notepad.exe", "Notepad")
        return True
    if command in {"open calculator", "calculator", "open calc"}:
        open_app("calc.exe", "Calculator")
        return True
    if command in {"open file explorer", "open explorer", "file explorer"}:
        open_app("explorer.exe", "File Explorer")
        return True

    for prefix in ("search ", "google search ", "search google for "):
        if command.startswith(prefix):
            query = command[len(prefix):].strip()
            if query:
                open_url("https://www.google.com/search?q=" + quote(query),
                         f"Google search for {query}")
            return True

    if command.startswith("youtube search "):
        query = command.removeprefix("youtube search ").strip()
        if query:
            open_url("https://www.youtube.com/results?search_query=" + quote(query),
                     f"YouTube search for {query}")
        return True

    if (command.startswith(("calculate ", "what is ", "solve ", "compute "))
            or looks_like_math(command)):
        if handle_math(command):
            return True

    if command in {"ai status", "check ai", "is ai working", "ai mode"}:
        speak(ai_status())
        return True

    if command in {"who are you", "what are you"}:
        speak("I am JARVIS, your hybrid Python voice assistant.")
        return True

    if command in {"help", "what can you do", "commands"}:
        speak(
            "I control supported laptop actions, Android phones through ADB, "
            "ESP32 devices over Wi-Fi, websites, maths, and AI. "
            "Say laptop help, phone help, or ESP32 help for device commands."
        )
        return True

    speak(ask_ai(command))
    return True


def main() -> None:
    speak("I am ready. Please say something.")
    while True:
        command = listen()
        if command and not handle_command(command):
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nJARVIS stopped.")
        sys.exit(0)
