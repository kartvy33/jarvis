# JARVIS

A simple Python voice assistant for Windows.

## Current version

**JARVIS V1.4**

The project is designed to stay beginner-friendly while leaving room for future laptop, phone and ESP32 control.

## Features

- Laptop microphone input
- Spoken responses with `pyttsx3`
- Local AI through Ollama
- Optional OpenAI Responses API support
- Offline fallback when no AI model is connected
- Safe local maths engine
- Time and date
- Google and YouTube search
- Open Chrome, Notepad, Calculator and File Explorer
- Short conversation memory while JARVIS is running
- AI status command

## 1. Install Python packages

Open Command Prompt in this folder:

```bat
cd C:\Users\acer\Desktop\JARVIS
python -m pip install -r requirements.txt
```

If PyAudio installation gives an error, install the normal 64-bit Python 3.11 build and try the command again.

## 2. Run JARVIS

```bat
python main.py
```

You should hear:

> I am ready. Please say something.

## 3. Local AI with Ollama

This is the preferred AI path because the model runs on your laptop.

Install Ollama, then download a model. A smaller model is easier on disk/RAM. For example:

```bat
ollama pull llama3.2:3b
```

Then start JARVIS:

```bat
python main.py
```

JARVIS automatically checks the local Ollama server.

If you use another Ollama model, set:

```bat
setx OLLAMA_MODEL "your-model-name"
```

Close and reopen Command Prompt after using `setx`.

You can ask JARVIS:

> AI status

## 4. Optional OpenAI AI

OpenAI API access is separate from a ChatGPT subscription and can be billed according to the API account/model.

Set your API key as an environment variable instead of putting it in Python:

```bat
setx OPENAI_API_KEY "YOUR_API_KEY_HERE"
setx OPENAI_MODEL "gpt-5.6"
```

Then open a new Command Prompt and run:

```bat
python main.py
```

Do **not** commit your API key. The repository ignores `.env`.

## 5. Maths

JARVIS calculates locally without AI.

Examples:

- "calculate 25 times 4"
- "calculate 2^10"
- "calculate sqrt(144)"
- "calculate sin(30)"
- "calculate factorial(5)"
- "calculate pi * 10"
- "what is 100 divided by 4"

Supported functions include:

`sqrt`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `log`, `ln`, `exp`, `abs`, `floor`, `ceil`, `factorial`, `round`, and `pow`.

Trigonometric input uses degrees.

## 6. Built-in commands

Examples:

- "what time is it"
- "what is the date"
- "open google"
- "open youtube"
- "open chrome"
- "open notepad"
- "open calculator"
- "open file explorer"
- "search Arduino ESP32"
- "youtube search Python tutorial"
- "AI status"
- "help"
- "shutdown"

Anything that is not recognized as a built-in command is sent to the configured AI backend.

## Project structure

```text
jarvis/
├── main.py
├── ai.py
├── math_engine.py
├── requirements.txt
├── .env.example
├── .gitignore
└── LICENSE
```

## Important

Speech recognition currently uses Google's online speech-recognition service through the SpeechRecognition library. The AI layer can be fully local with Ollama, but speech-to-text is not yet fully offline.

The next architecture step can add:
- phone microphone input
- ESP32/ESP32-S3 microphone input
- laptop automation
- ESP32 device control
- wake-word detection
- offline speech recognition
- plugins/tools for JARVIS
