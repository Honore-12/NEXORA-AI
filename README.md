# NEXORA-AI
# 🔮 Nexora AI – Your Interactive Voice AGENT 🎙️✨

> 🧠 A smart, speech-powered assistant built in Python with a beautiful GUI. Nexora listens to your commands and acts like magic – whether it’s sending WhatsApp messages, controlling system volume, telling jokes, or doing math!

---

## 📌 Table of Contents

- [✨ Features](#-features)
- [💻 Demo Screenshots](#-demo)
- [🧠 How It Works](#-how-it-works)
- [📁 File Structure](#-file-structure)
- [⚙️ Requirements](#-requirements)
- [🚀 How to Run](#-how-to-run)
- [🧩 Technologies Used](#-technologies-used)
- [👨🏻‍💻 Author](#-author)
- [📜 License](#-license)

---

## ✨ Features

- 🎧 **Voice Input** – Uses speech recognition to process spoken commands.
- 🧮 **Math Calculations** – Solve spoken arithmetic expressions with BODMAS.
- 🗓️ **Quick & Daily Reminders** – Set reminders with GUI input + speech.
- 📲 **Send WhatsApp Messages** – Through PyWhatKit automation.
- 📸 **Take Screenshots** – One command, saved with timestamp.
- 🔊 **System Volume Control** – Increase, decrease, mute/unmute via voice.
- 📂 **App & Website Launch** – Open VS Code, YouTube, Notepad etc.
- 🧠 **Wikipedia & Google Search** – Just ask!
- 💬 **Text-to-Speech Feedback** – Uses `pyttsx3` for smooth responses.
- 🌙 **Custom GUI + Idle Animation** – Beautiful, responsive GUI with status updates.

---

## 💻 Demo Screenshots


![Screenshot 2025-05-12 215543](https://github.com/user-attachments/assets/73111c36-0939-43ca-b146-5f446fd21057)
![Screenshot 2025-05-12 215605](https://github.com/user-attachments/assets/f254ae7d-b695-4a11-b51a-4a887605578f)
![Screenshot 2025-05-12 220204](https://github.com/user-attachments/assets/91c2b756-8ae7-40fb-96e0-5a0ad618165d)
![Screenshot 2025-05-12 220234](https://github.com/user-attachments/assets/6b0438da-01e3-4bca-a2f4-c1fd8ec581a2)
![Screenshot 2025-05-12 220350](https://github.com/user-attachments/assets/7e401687-de2e-46fb-a38a-42058ba1e555)
![Screenshot 2025-05-12 220417](https://github.com/user-attachments/assets/b1ecf92c-a438-4342-b7bb-9ea6b857447a)
![Screenshot 2025-05-12 220509](https://github.com/user-attachments/assets/8e221dc8-8835-443b-b6af-53c56faf543f)

---

## 🧠 How It Works

### 🔊 Speech Recognition
```python
with sr.Microphone() as source:
    audio = r.listen(source, timeout=6)
    command = r.recognize_google(audio, language='en-in').lower()
````

### 🗣️ Text-to-Speech (TTS)

```python
engine = pyttsx3.init()
engine.say("Hello, Vishnu!")
engine.runAndWait()
```

### 💡 Command Processing

* Processes over 30+ natural language commands.
* Matches phrases like “take screenshot”, “increase volume”, “open YouTube”, etc.
* Has custom logic for math operations using `word2number` + `AST`.

### 🧮 Smart Math Parser

Converts:

> “two plus three times four” → `2 + 3 * 4` → `14` ✅
> Safely evaluated using Python’s abstract syntax tree (`ast`).

### 📲 WhatsApp Integration

Uses `pywhatkit.sendwhatmsg_instantly()` and `pyautogui` to send a message via browser automation.

### 🗓️ Reminder System

* Quick Reminder: Triggers after X seconds/minutes.
* Daily Reminder: Scheduled using `schedule.every().day.at("HH:MM")`.

---

## 📁 File Structure

```
📦 Nexora/
 ┣ 📄 NEXORA AI.py         # Main code for the assistant
 ┣ 📄 README.md            # This file!
 ┗ 📁 assets/              # (Optional) icons, sound files, etc.
```

---

## ⚙️ Requirements

```bash
pip install pyttsx3 pyautogui wikipedia pyjokes pywhatkit pillow speechrecognition comtypes pycaw customtkinter playsound word2number schedule plyer
```

📝 *Tested on Windows 10/11 with Python 3.10+*

---

## 🚀 How to Run

1. Clone this repository

```bash
git clone [https://github.com/Vishnu-tppr/NEXORA-AI.git]
cd nexora-agent
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the assistant

```bash
python NEXORA AI.py
```

✅ Make sure your microphone is connected. Run in **admin mode** if volume/system commands fail.

---

## 🧩 Technologies Used

* Python 3
* [SpeechRecognition](https://pypi.org/project/SpeechRecognition/)
* [Pyttsx3](https://pypi.org/project/pyttsx3/)
* [PyAutoGUI](https://pypi.org/project/pyautogui/)
* [Wikipedia API](https://pypi.org/project/wikipedia/)
* [PyWhatKit](https://pypi.org/project/pywhatkit/)
* [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
* [Plyer](https://plyer.readthedocs.io/) for desktop notifications
* [PyCaw](https://github.com/AndreMiras/pycaw) for system volume control
* [Word2Number](https://github.com/akshaynagpal/w2n) for parsing math
* Multi-threading, logging, and speech scheduling using `schedule`

---

## 👨🏻‍💻 Author

Made with ❤️ by [Vishnu](https://www.linkedin.com/in/vishnu-v-31583b327/)

> “Coded not just with Python, but with passion.” 💻✨

---

## 📜 License

This project is open-source and free to use under the **MIT License**.

---

🌟 If you like this project, leave a ⭐ on the repo and share it with others!

```

