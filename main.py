"""
JARVIS V1.3 Hybrid
Voice assistant for Windows.
- Speech input: laptop microphone
- Speech output: pyttsx3
- AI: Ollama local model (preferred) or optional OpenAI API
- Built-in math engine
- Windows commands, web search, time/date
"""

import datetime
import os
import sys
import webbrowser

import pyttsx3
import speech_recognition as sr

from ai import ask_ai
from math_engine import calculate

WAKE_NAME = "jarvis"

engine = pyttsx3.init()
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

recognizer = sr.Recognizer()


def speak(text: str) -> None:
    """Speak and print a response."""
    text = str(text).strip()
    if not text:
        return
    print(f"JARVIS: {text}")
    engine.say(text)
    engine.runAndWait()


def listen() -> str:
    """Listen through the default microphone and convert speech to text."""
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=12)
        except sr.WaitTimeoutError:
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


def open_url(url: str, spoken_name: str) -> None:
    webbrowser.open(url)
    speak(f"Opening {spoken_name}.")


def handle_command(command: str) -> bool:
    """Handle a command. Return False to stop JARVIS."""
    if not command:
        return True

    if command in {"exit", "quit", "stop", "shutdown", "goodbye"}:
        speak("Shutting down. Goodbye.")
        return False

    if "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {now}.")
        return True

    if "date" in command or "today" in command:
        today = datetime.datetime.now().strftime("%A, %d %B %Y")
        speak(f"Today is {today}.")
        return True

    if "open google" in command:
        open_url("https://www.google.com", "Google")
        return True

    if "open youtube" in command:
        open_url("https://www.youtube.com", "YouTube")
        return True

    if "open chrome" in command:
        # Windows normally opens Chrome through the URL handler.
        open_url("https://www.google.com", "Chrome")
        return True

    if command.startswith("search "):
        query = command.removeprefix("search ").strip()
        if query:
            open_url(
                "https://www.google.com/search?q=" + webbrowser.quote(query),
                f"Google search for {query}",
            )
        return True

    if command.startswith("calculate "):
        expression = command.removeprefix("calculate ").strip()
        try:
            result = calculate(expression)
            speak(f"The answer is {result}.")
        except ValueError as exc:
            speak(f"I could not calculate that: {exc}")
        return True

    if command.startswith("what is ") and any(ch.isdigit() for ch in command):
        expression = command.removeprefix("what is ").strip()
        try:
            result = calculate(expression)
            speak(f"The answer is {result}.")
            return True
        except ValueError:
            pass

    if command in {"who are you", "what are you"}:
        speak("I am JARVIS, your hybrid Python voice assistant.")
        return True

    if command in {"help", "what can you do"}:
        speak(
            "I can tell the time and date, open websites, search Google, "
            "calculate maths, and answer general questions using the configured AI."
        )
        return True

    # Everything else goes to the AI layer.
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
