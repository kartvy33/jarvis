"""
JARVIS V1.4
A beginner-friendly Windows voice assistant.

Features:
- Laptop microphone speech input
- pyttsx3 speech output
- Local Ollama AI (no API key) or optional OpenAI API
- Safe maths engine with scientific functions
- Windows app commands
- Google/YouTube search and browser commands
- Simple conversation memory during the current run
"""

import datetime
import os
import subprocess
import sys
import webbrowser
from urllib.parse import quote

import pyttsx3
import speech_recognition as sr

from ai import ask_ai, ai_status
from math_engine import calculate, looks_like_math


WAKE_NAME = "jarvis"

engine = pyttsx3.init()
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.7
recognizer.energy_threshold = 300


def speak(text: str) -> None:
    """Print and speak text."""
    text = str(text).strip()
    if not text:
        return
    print(f"JARVIS: {text}")
    engine.say(text)
    engine.runAndWait()


def listen() -> str:
    """Listen through the default Windows microphone."""
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.35)
            audio = recognizer.listen(
                source,
                timeout=6,
                phrase_time_limit=15,
            )
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
        print("JARVIS: I did not understand that.")
        return ""
    except sr.RequestError as exc:
        speak(f"Speech recognition service error: {exc}")
        return ""


def open_url(url: str, spoken_name: str) -> None:
    webbrowser.open(url)
    speak(f"Opening {spoken_name}.")


def open_windows_app(app: str, spoken_name: str) -> None:
    try:
        subprocess.Popen(app, shell=True)
        speak(f"Opening {spoken_name}.")
    except Exception as exc:
        speak(f"I could not open {spoken_name}: {exc}")


def handle_math(command: str) -> bool:
    expression = command
    for prefix in ("calculate ", "what is ", "solve ", "compute "):
        if expression.startswith(prefix):
            expression = expression[len(prefix):].strip()
            break

    if not expression or not looks_like_math(expression):
        return False

    try:
        result = calculate(expression)
        speak(f"The answer is {result}.")
    except ValueError as exc:
        speak(f"I could not calculate that: {exc}")
    return True


def handle_command(command: str) -> bool:
    """Handle a command. Return False to stop JARVIS."""
    if not command:
        return True

    # Exit
    if command in {"exit", "quit", "stop", "shutdown", "goodbye", "close jarvis"}:
        speak("Shutting down. Goodbye.")
        return False

    # Basic information
    if command in {"time", "what time is it", "tell me the time"} or "current time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {now}.")
        return True

    if command in {"date", "today", "what is the date", "what day is it"}:
        today = datetime.datetime.now().strftime("%A, %d %B %Y")
        speak(f"Today is {today}.")
        return True

    # Browser
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
        open_windows_app("start chrome", "Chrome")
        return True

    if command in {"open notepad", "notepad"}:
        open_windows_app("notepad.exe", "Notepad")
        return True

    if command in {"open calculator", "calculator", "open calc"}:
        open_windows_app("calc.exe", "Calculator")
        return True

    if command in {"open file explorer", "open explorer", "file explorer"}:
        open_windows_app("explorer.exe", "File Explorer")
        return True

    # Search
    for prefix in ("search ", "google search ", "search google for "):
        if command.startswith(prefix):
            query = command[len(prefix):].strip()
            if query:
                open_url(
                    "https://www.google.com/search?q=" + quote(query),
                    f"Google search for {query}",
                )
            return True

    if command.startswith("youtube search "):
        query = command.removeprefix("youtube search ").strip()
        if query:
            open_url(
                "https://www.youtube.com/results?search_query=" + quote(query),
                f"YouTube search for {query}",
            )
        return True

    # Maths: try before AI so simple calculations are always local and fast.
    if (
        command.startswith(("calculate ", "what is ", "solve ", "compute "))
        or looks_like_math(command)
    ):
        if handle_math(command):
            return True

    # AI status
    if command in {"ai status", "check ai", "is ai working", "ai mode"}:
        speak(ai_status())
        return True

    # Identity/help
    if command in {"who are you", "what are you"}:
        speak("I am JARVIS, your hybrid Python voice assistant.")
        return True

    if command in {"help", "what can you do", "commands"}:
        speak(
            "I can tell time and date, open Windows apps and websites, "
            "search Google or YouTube, perform maths, and answer general "
            "questions using local or cloud AI."
        )
        return True

    # Everything else goes to the configured AI layer.
    answer = ask_ai(command)
    speak(answer)
    return True


def main() -> None:
    speak("I am ready. Please say something.")

    while True:
        command = listen()
        if not command:
            continue
        if not handle_command(command):
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nJARVIS stopped.")
        sys.exit(0)
