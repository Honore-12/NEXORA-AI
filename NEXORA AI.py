import os
import subprocess
import datetime
import logging
import webbrowser
import pyttsx3
import pyautogui
import wikipedia
import pyjokes
import pywhatkit
from PIL import ImageGrab
import speech_recognition as sr
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from threading import Thread
import time
import customtkinter as ctk
from playsound import playsound
from typing import Optional
import re
import ast  
import operator as op  
from word2number import w2n 
import time
import schedule
from plyer import notification


# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define screenshot save path Use a raw string (r"...") to avoid issues with backslashes, and os.path.normpath for robustness.
SCREENSHOT_SAVE_PATH = os.path.normpath(r"C:\Users\ADMIN\OneDrive\Pictures\Screenshots 1")

# Initialize voice engine
def init_engine():
    try:
        engine = pyttsx3.init('sapi5')
    except Exception:
        logging.warning("SAPI5 engine not available, falling back to default.")
        engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if len(voices) > 1:
        engine.setProperty('voice', voices[1].id)
    else:
        logging.info("Only one voice found, falling back to default voice.")
        engine.setProperty('voice', voices[0].id)
    return engine

engine = init_engine()
r = sr.Recognizer()

# Global flags
speak_enabled = True
speaking = False

# Global GUI element references (bound later)
app = None
command_box = None
response_box = None

# Animation Globals
listening_active = False
unique_animation_phrases = [
   "Zzz... 😴", "Taking a nap... 💤", "Dreaming of commands... ✨",
    "Waiting for your magical voice ✨...", "🥱"
]
current_phrase_index = 0
current_dot_count = 1

# GUI update helpers (thread-safe)
def update_command_box_gui(text):
    if app and command_box:
        def _update():
            command_box.configure(state="normal")
            command_box.delete("0.0", "end")
            command_box.insert("0.0", text)
            command_box.configure(state="disabled")
        app.after(0, _update)

def update_response_box_gui(text):
    if app and response_box:
        def _update():
            response_box.configure(state="normal")
            response_box.insert("end", text + "\n")
            response_box.see("end")
            response_box.configure(state="disabled")
        app.after(0, _update)

# Speak function that also updates GUI
def speak(message: str, gui_prefix: str = "Nexora:"): 
    global speak_enabled, speaking
    if speak_enabled:
        print(f"Assistant: {message}")
        # Use gui_prefix here to allow _respond to customize the GUI message
        update_response_box_gui(f"{gui_prefix} {message}") 
        if not speaking:
            speaking = True
            try:
                engine.say(message)
                engine.runAndWait()
            except Exception as e:
                logging.error(f"TTS engine error: {e}")
            finally:
                speaking = False
    else:
        print(f"Assistant (muted): {message}")
        update_response_box_gui(f"Nexora (muted): {message}")

def stop_speaking():
    global speaking
    engine.stop()
    speaking = False

# Function to respond to the user
def _respond(message: str, gui_prefix: str = "Nexora:") -> None:
    speak(message, gui_prefix=gui_prefix)


def _get_input_from_dialog(
    prompt_speech: str,
    prompt_gui: str,
    dialog_text: str,
    dialog_title: str
) -> Optional[str]:

    _respond(prompt_speech, gui_prefix=prompt_gui)
    dialog = ctk.CTkInputDialog(text=dialog_text, title=dialog_title)
    user_input = dialog.get_input()

    if not user_input:
        abortion_msg = f"Input for '{dialog_title.replace('WhatsApp: ', '')}' not provided. Aborting operation."
        _respond(abortion_msg, f"{prompt_gui} {dialog_title.replace('WhatsApp: ', '')} aborted.")
        return None
    return user_input
# Function to handle WhatsApp message sending

# Greetings
def wish_me():
    hour = datetime.datetime.now().hour
    if hour < 12: greet = "Good Morning Vishnu!"
    elif hour < 18: greet = "Good Afternoon Vishnu!"
    else: greet = "Good Evening Vishnu!"
    return f"{greet} I am your assistant. How may I help you?"

def listen():
    global listening_active
    with sr.Microphone() as source:
        try:
            r.adjust_for_ambient_noise(source, duration=1)
            update_response_box_gui("Nexora: Listening...")
            update_command_box_gui("Listening your magical voice ✨...")
            listening_active = True
            audio = r.listen(source, timeout=6, phrase_time_limit=12)
        except sr.WaitTimeoutError:
            update_command_box_gui("Waiting for your magical voice ✨...")
            _respond("Are you still there, Vishnu? I couldn't hear anything. Please try again.")
            stop_speaking()
            listening_active = False
            return ""
        except sr.MicrophoneError as e:
            logging.error(f"Microphone error: {e}")
            _respond("It seems I can't access your microphone. Please ensure it's connected and permissions are granted for Nexora.")
            update_command_box_gui("Microphone error. Please check your system settings.")
            listening_active = False
            return ""
        except Exception as e:
            logging.error(f"Listening error: {e}")
            _respond("Oops, something went wrong while preparing to listen. Please try again.") 
            update_command_box_gui("Listening error. Please retry.")
            listening_active = False
            return ""
    try:
        cmd = r.recognize_google(audio, language='en-in').lower()
        logging.info(f"Recognized: {cmd}")
        update_command_box_gui(f"You said: {cmd}") 
        update_response_box_gui(f"Nexora: Understood. Processing '{cmd}'.") 
        listening_active = False
        return cmd
    except sr.UnknownValueError:
        logging.warning("Speech Recognition could not understand audio.")
        update_response_box_gui("Speech not understood. Please try again.")
        listening_active = False
        return ""
    except sr.RequestError as e:
        logging.error(f"Could not request results from Google SR service; {e}")
        _respond("I'm having trouble connecting to the speech recognition service. Please check your internet connection.") 
        update_command_box_gui("Service connection error. Please check internet.")
        listening_active = False
        return ""
    except Exception as e:
        logging.error(f"Recognition error: {e}")
        _respond("There was an' unexpected issue during recognition. Please try speaking again.")
        update_command_box_gui("Recognition failed. Please retry.")
        listening_active = False
        return ""

def remind(title, message):
    print(f"Reminder Triggered: {title} - {message}") 
    if app:
        app.after(0, lambda: notification.notify(
            title=title,
            message=message,
            timeout=15, # Notification stays for 15 seconds
            app_icon=r'c:\Users\ADMIN\Downloads\NEXORA AI.ico' 
        ))
        # Read the reminder message aloud
        app.after(0, lambda: _respond(f"Here's a reminder: {message}", f"Nexora: {title}"))
    else:
        notification.notify(
            title=title,
            message=message,
            timeout=15,
        )
        _respond(f"Here's a reminder: {message}", f"Nexora: {title}")
def start_scheduler_loop():
    while True:
        schedule.run_pending()
        time.sleep(1) 

def set_quick_reminder():
    # Get reminder message using GUI input
    reminder = _get_input_from_dialog(
        prompt_speech="What would you like me to be reminded about?", 
        prompt_gui="Nexora:",
        dialog_text="What should I remind you about?",
        dialog_title="Set Quick Reminder: Message" 
    )
    if not reminder:
        return
    # Get reminder time using GUI input, now accepting units
    time_input_str = _get_input_from_dialog(
        prompt_speech="For how long should I set the reminder? You can say seconds, minutes, hours, or days.",
        prompt_gui="Nexora:",
        dialog_text="Enter the reminder time (e.g., '30 seconds', '5 minutes', '2 hours', '1 day'):",
        dialog_title="Set Quick Reminder: Time" 
    )
    if not time_input_str:
        return
    total_seconds = -1
    try:
        time_input_lower = time_input_str.lower().strip()
        # Pattern to find numbers followed by optional units (sec, min, hr, day)
        match = re.search(r'(\d+)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?|days?)?', time_input_lower)
        if match:
            value_str = match.group(1)
            unit_str = match.group(2) if match.group(2) else 'seconds' # Default unit to seconds if none specified
            value = int(value_str)
            seconds_in_unit = 1 # Default to seconds
            if 'minute' in unit_str or 'min' in unit_str:
                seconds_in_unit = 60
            elif 'hour' in unit_str or 'hr' in unit_str:
                seconds_in_unit = 60 * 60
            elif 'day' in unit_str:
                seconds_in_unit = 24 * 60 * 60
            total_seconds = value * seconds_in_unit
        else:
            try:
                total_seconds = int(time_input_lower)
            except ValueError:
                try:
                    total_seconds = w2n.word_to_num(time_input_lower)
                except ValueError:
                    raise ValueError("Invalid time format. Please enter a number followed by a unit (e.g., '5 minutes') or just a number in seconds.")
        if total_seconds <= 0:
            _respond("Reminder time must be positive. Aborting.")
            return
        target_time = datetime.datetime.now() + datetime.timedelta(seconds=total_seconds)
        target_time_str = target_time.strftime('%I:%M %p') # Simpler format for quick reminder
        def reminder_func():
            time.sleep(total_seconds)
            app.after(0, lambda: _respond(f"Reminder: {reminder}", "Nexora: Quick Reminder Triggered!"))
        Thread(target=reminder_func, daemon=True).start()
        _respond(f"Quick reminder set for {total_seconds} seconds from now.", "Nexora:") #
    except ValueError as e:
        _respond(f"Invalid input for time: {e}", "Nexora: Input Error") 
    except Exception as e:
        logging.error(f"Error setting quick reminder: {e}")
        _respond("An unexpected error occurred while setting the quick reminder.", "Nexora: Error") 

# Function to set a daily reminder using schedule 
def set_daily_scheduled_reminder():
    _respond("Alright, I can help you set a daily reminder.", "Nexora:")

    # Get reminder text using GUI input
    reminder_text = _get_input_from_dialog(
        prompt_speech="What should I remind you about daily?",
        prompt_gui="Nexora: Daily Reminder Text",
        dialog_text="Enter the daily reminder message:",
        dialog_title="Set Daily Reminder: Message"
    )
    if reminder_text is None:
        return
    # Get reminder time (12-hour format with AM/PM) using GUI input
    reminder_time_12hr_str = _get_input_from_dialog(
        prompt_speech="At what time should I remind you daily? Please use the 12-hour format with AM or PM, like 2:30 PM or 10:00 AM.",
        prompt_gui="Nexora: Daily Reminder Time",
        dialog_text="Enter the reminder time (e.g., '10:00 AM', '2:30 PM'):",
        dialog_title="Set Daily Reminder: Time"
    )
    if reminder_time_12hr_str is None:
        return
    # Function to convert 12-hour time string (with AM/PM) to 24-hour HH:MM format
    def convert_12hr_to_24hr(time_str: str) -> Optional[str]:
        time_str = time_str.strip().upper().replace('.', '').replace(' ', '') 
        match = re.match(r'^(1[0-2]|[1-9])(:([0-5]\d))?(AM|PM)$', time_str)
        if not match:
            return None 
        hour_str = match.group(1)
        minute_str = match.group(3) 
        am_pm = match.group(4)
        hour = int(hour_str)
        minute = int(minute_str) if minute_str else 0
        if am_pm == 'AM':
            if hour == 12: # 12 AM is 00 in 24-hour format
                hour = 0
        elif am_pm == 'PM':
            if hour != 12: # 1-11 PM add 12 to the hour
                hour += 12
        return f"{hour:02d}:{minute:02d}"
    reminder_time_24hr_str = convert_12hr_to_24hr(reminder_time_12hr_str)
    if reminder_time_24hr_str is None:
        _respond("That doesn't look like a valid time in 12-hour format with AM or PM. Please try setting the reminder again with the correct format.", "Nexora: Invalid Time Format")
        return
    try:
        schedule.every().day.at(reminder_time_24hr_str).do(remind, title='Daily Reminder', message=reminder_text)
        _respond(f"Okay, I've scheduled a daily reminder for '{reminder_text}' at {reminder_time_12hr_str}.", "Nexora:") 
        logging.info(f"Daily reminder set for '{reminder_text}' at {reminder_time_24hr_str} (24hr)")
    except Exception as e:
        logging.error(f"Error scheduling daily reminder: {e}")
        _respond("Sorry, I ran into an issue while trying to schedule that daily reminder.", "Nexora: Scheduling Error")

def change_volume(action: str):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        cur = volume.GetMasterVolumeLevelScalar()
        if action == 'up': volume.SetMasterVolumeLevelScalar(min(cur + 0.1, 1.0), None)
        elif action == 'down': volume.SetMasterVolumeLevelScalar(max(cur - 0.1, 0.0), None)
        elif action == 'mute': volume.SetMute(1, None)
        elif action == 'unmute': volume.SetMute(0, None)
        _respond(f"Volume {action}.") 
    except Exception as e:
        logging.error(f"Volume control error: {e}. This feature may only work on Windows.")
        _respond("Oops! I couldn't control the volume. This feature usually works best on Windows systems.")

def system_control(command: str):
    try:
        if "shutdown" in command:
            _respond("Okay, Vishnu. Shutting down the system. Goodbye!")
            subprocess.run(["shutdown", "/s", "/t", "1"], check=True)
        elif "restart" in command:
            _respond("Alright, Vishnu. Restarting the system for you.")
            subprocess.run(["shutdown", "/r", "/t", "1"], check=True)
        elif "log off" in command:
            _respond("Logging you off, Vishnu.")
            subprocess.run(["shutdown", "/l"], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"System control command failed: {e}")
        _respond("Oh no! I failed to execute that system command. You might need to run Nexora with administrator privileges for this.")
    except Exception as e:
        logging.error(f"Error during system control: {e}")
        _respond("I'm sorry, an unexpected error popped up while trying to control the system.")
def take_screenshot():
    try:
        # Ensure the directory exists
        os.makedirs(SCREENSHOT_SAVE_PATH, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        # Use the specified path for saving
        path = os.path.join(SCREENSHOT_SAVE_PATH, filename)
        ImageGrab.grab().save(path)
        _respond(f"Screenshot saved as {filename} in your Screenshots folder.")
    except Exception as e:
        logging.error(f"Screenshot error: {e}")
        _respond("Could not take screenshot.") 

def handle_whatsapp_message_gui():
    try:
        # Get Recipient Phone Number
        phone_number = _get_input_from_dialog(
            prompt_speech="Please provide the recipient's phone number in the dialog that appears.",
            prompt_gui="Nexora:",
            dialog_text="Enter recipient phone number ""(e.g., +91XXXXXXXXXX):",
            dialog_title="WhatsApp: Phone Number"
        )
        if phone_number is None:
            return

        # Get Message Text
        message_text = _get_input_from_dialog(
            prompt_speech="Now, please enter your message in the dialog.",
            prompt_gui="Nexora:",
            dialog_text="Enter your message:",
            dialog_title="WhatsApp: Message"
        )
        if message_text is None:
            return

        # Send WhatsApp Message
        prep_msg = f"Preparing to send WhatsApp message to {phone_number}. This will open a browser window."
        _respond(f"{prep_msg} Please do not touch the keyboard or mouse until the message is sent.", "Nexora:")

        pywhatkit.sendwhatmsg_instantly(
            phone_number,
            message_text,
           wait_time=20,
            tab_close=False
        )
        # Give the browser a moment after pywhatkit finishes typing/preparing
        time.sleep(5)
        pyautogui.press('enter')
        # Wait a moment for the message to send, then close the tab
        time.sleep(2)
        pyautogui.hotkey('ctrl', 'w')
        _respond("WhatsApp message sent successfully!", f"Nexora: WhatsApp message sent successfully to {phone_number}.")

    except Exception as e:
        # Catch any unexpected errors during the process
        error_feedback_user = "An error occurred while trying to send the WhatsApp message."
        _respond(f"Sorry, {error_feedback_user} Details: {e}", "Nexora: Error sending WhatsApp message.")
        logging.error(f"{error_feedback_user} Exception: {e}", exc_info=True)

def open_application(cmd: str) -> bool:
    sites = {
        "youtube": "https://www.youtube.com", "google": "https://google.com", "weather": "https://weather.com"
    }
    apps = {
          "camera": "microsoft.windows.camera:", "calculator": "calc.exe", "files": "explorer.exe",
        "notepad": "notepad.exe", "wireless display": "ms-settings:display",
        "vs code": r"C:\Users\ADMIN\OneDrive\Desktop\VS Code.lnk",
        "chat gpt": r"C:\Users\ADMIN\OneDrive\Desktop\ChatGPT.lnk"
    }
    for key, url in sites.items():
        if key in cmd:
            webbrowser.open(url)
            _respond(f"Opening {key}") 
            return True
    for key, exe_or_uri in apps.items():
        if key in cmd:
            try:
                if key == "camera": subprocess.run(f"start {exe_or_uri}", shell=True, check=True)
                else: subprocess.Popen(exe_or_uri)
                _respond(f"Opening {key}") 
            except (FileNotFoundError, subprocess.CalledProcessError) as e:
                logging.error(f"Failed to open {key}: {e}")
                _respond(f"Failed to open {key}.") 
            return True
    return False

def show_help():
    help_intro = "Here are the commands I can assist you with."
    _respond(help_intro) 

    # Prepare the detailed help text for GUI display
    help_text_for_gui = """
Available Commands:
    - Wikipedia search: "Wikipedia [topic]"
    - Google search: "Search for [query]"
    - Tell a Joke: "Tell me a joke"
    - Set Reminder: "Set reminder"
    - Send WhatsApp message: "Send WhatsApp"
    - **Calculator**: "Do calculation" or "Calculate" (e.g., "two plus three times four")
    - Open Websites: "Open YouTube", "Open Google", "Open Telegram", "Open WhatsApp", "Open Chat GPT", "Open Weather"
    - Open Applications: "Open Camera", "Open Calculator", "Open Files", "Open Notepad", "Open Settings", "Open Wireless Display", "Open Vscode"
    - Take Screenshot: "Take a screenshot"
    - Get Current Time: "What time is it?" or "Time"
    - System Volume Control:
        - "Increase volume" / "Volume up"
        - "Decrease volume" / "Volume down"
        - "Mute" / "Unmute"
    - Window Management:
        - "Alt Tab" (switch windows)
        - "Minimise window"
        - "Maximize window"
        - "Close window"
        - "Split window"
        - "Retab window" / "Move window to right"
        - "Lock screen"
    - Display Mode: "Dark mode", "Light mode" (application-specific)
    - System Actions:
        - "Shutdown system"
        - "Restart system"
        - "Log off"
    - Exit Nexora: "Exit", "Quit", "Stop", "See you later", "Goodbye", "Bye Nexora"
    - This help message: "Help" or "Commands"
"""
    # Update the response box with the detailed help text
    update_response_box_gui(help_text_for_gui)

# --- Calculator Functions (Improved with word2number) ---
OPERATOR_MAP = {
    "plus": "+", "add": "+", "addition": "+", "sum": "+",
    "minus": "-", "subtract": "-", "subtraction": "-", "difference": "-",
    "times": "*", "multiply": "*", "multiplied by": "*", 
    "divided by": "/", "divide by": "/", "division": "/",
    "open parenthesis": "(", "open bracket": "(", 
    "close parenthesis": ")", "close bracket": ")",
    "mod": "%", "modulo": "%",
    "power": "**", "to the power of": "**",
    "point": ".", "dot": ".",
    # NEW: Direct symbols for when STT outputs them literally (e.g., "1 + 1")
    "+": "+",
    "-": "-",
    "*": "*",
    "/": "/",
    "%": "%",
    "**": "**", # for cases like "2 ** 3"
    "(": "(",
    ")": ")",
    ".": ".",
    "into": "*",
    "x": "*"
}
# AST-based safe evaluator (respects BODMAS)
_OPERATORS = {
    ast.Add:    op.add,
    ast.Sub:    op.sub,
    ast.Mult:   op.mul,
    ast.Div:    op.truediv,
    ast.Pow:    op.pow,
    ast.Mod:    op.mod,
    ast.UAdd:   op.pos,
    ast.USub:   op.neg,
}

def safe_eval(expr: str) -> float:
    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.BinOp):
            left  = _eval(node.left)
            right = _eval(node.right)
            return _OPERATORS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp):
            val = _eval(node.operand)
            return _OPERATORS[type(node.op)](val)
        raise ValueError(f"Unsupported expression: {node!r}")

    try:
        parsed_expression_tree = ast.parse(expr, mode='eval')
        if not isinstance(parsed_expression_tree, ast.Expression):
            raise ValueError("Only single expressions are allowed.")
        return _eval(parsed_expression_tree.body)
    except SyntaxError as e:
        raise ValueError(f"Invalid mathematical expression syntax: {e}")
    except ValueError as e:
        raise e # Re-raise specific ValueErrors from _eval
    except Exception as e:
        logging.error(f"Error parsing expression in safe_eval: {e}", exc_info=True)
        raise ValueError(f"Error in expression: {e}")

def parse_spoken_math_expression(spoken: str) -> str:
    words = spoken.lower().split()
    tokens = []
    i = 0
    N = len(words)

    while i < N:
        # 1) Try multi-word operators (longest first)
        matched = False
        # Try 3-word phrases first, then 2-word, then 1-word
        for size in (3, 2, 1): 
            if i + size <= N:
                phrase = " ".join(words[i:i+size])
                if phrase in OPERATOR_MAP:
                    tokens.append(OPERATOR_MAP[phrase])
                    i += size
                    matched = True
                    break
        if matched:
            continue
        # 2) Try to greedily parse a number phrase via word2number
        for j in range(N, i, -1): # iterate backwards to find longest match
            seq = " ".join(words[i:j])
            try:
                num = w2n.word_to_num(seq)
                tokens.append(str(num))
                i = j
                matched = True
                break
            except ValueError: 
                pass
        if matched:
            continue
        # 3) If not a multi-word operator or a number phrase, check for single-word operators or direct digits
        w = words[i]
        if re.fullmatch(r"-?\d+(\.\d+)?", w): # Recognize actual digits/floats like "23" or "-4.5"
            tokens.append(w)
        else:
            raise ValueError(f"Unrecognized term in calculation: '{w}'")
        i += 1
    # Join tokens, insert spaces around operators for AST parsing
    expr = "".join(tokens)
    # Use regex to add spaces around operators and parentheses for robust parsing
    spaced = re.sub(r"([+\-*/%()^])", r" \1 ", expr)
    return re.sub(r"\s+", " ", spaced).strip()


def perform_calculation(spoken_expression: str) -> float:
    try:
        expression_for_eval = parse_spoken_math_expression(spoken_expression)
        logging.info(f"Parsed expression for evaluation: '{expression_for_eval}'")
        expression_for_eval = expression_for_eval.replace("^", "**")
        result = safe_eval(expression_for_eval)
        return float(result)
    except ZeroDivisionError:
        raise ValueError("Cannot divide by zero.")
    except ValueError as ve:
        raise ve
    except Exception as e: 
        logging.error(f"Unexpected error during calculation: {e}", exc_info=True)
        raise ValueError("An unexpected error occurred during calculation. Please try again or rephrase.")
def _handle_percentage_calculation_query(query_lower: str) -> bool:
    percentage_match = re.search(r"(\d+)\s*%\s*of\s*(\d+)", query_lower)
    if not percentage_match:
        percentage_match = re.search(r"(\d+)\s*percent\s*of\s*(\d+)", query_lower)
    if percentage_match:
        try:
            percent_val_str = percentage_match.group(1)
            base_val_str = percentage_match.group(2)
            percent_val = float(percent_val_str)
            base_val = float(base_val_str)
            result = (percent_val / 100) * base_val
            _respond(f"{percent_val_str} percent of {base_val_str} is {result}.")
            return True 
        except ValueError:
            _respond("Sorry, I couldn't understand the numbers in the percentage calculation. Please make sure they are digits.")
            logging.error(f"ValueError in percentage calculation for query: {query_lower}")
            return True 
        except Exception as e:
            _respond("An unexpected error occurred while calculating the percentage. Please try again.")
            logging.error(f"Unexpected error in percentage calculation for query '{query_lower}': {e}")
            return True 
    return False

# --- End of Calculator Functions ---

def process_query(query: str):
    if not query: return ''

    if "help" in query or "commands" in query:
        show_help()
        return ''

    if "wikipedia" in query:
        _respond("Searching Wikipedia...") 
        search_term = query.replace("wikipedia", "").strip()
        try:
            summary = wikipedia.summary(search_term, sentences=2)
            _respond("According to Wikipedia,")
            _respond(summary) 
        except wikipedia.exceptions.PageError: _respond(f"Sorry, no results for {search_term}.")
        except wikipedia.exceptions.DisambiguationError as e: _respond(f"Multiple results for {search_term}. Be more specific.")
        except Exception as e: _respond("Sorry, couldn't fetch info.") 
        return ''
    if 'search' in query:
        term = query.replace('search for', '').replace('search', '').strip()
        if term: webbrowser.open(f"https://google.com/search?q={term}"); _respond(f"Searching Google for {term}") 
        else: _respond("What would you like me to search for on Google, Vishnu?")
        return ''
    if 'joke' in query:
        _respond(pyjokes.get_joke()) 
        return ''
    if 'set quick reminder' in query or 'set a quick reminder' in query or 'set reminder for' in query or 'set reminder' in query: 
        Thread(target=set_quick_reminder, daemon=True).start() 
        return ''
    if 'schedule a daily reminder' in query or 'set a daily reminder' in query or 'set daily reminder' in query or 'schedule daily reminder' in query:
        Thread(target=set_daily_scheduled_reminder, daemon=True).start() 
        return ''
    if 'settings' in query:
        pyautogui.hotkey("win", "i")
        _respond("Opening Settings for you.")
    if 'send whatsapp' in query:
        handle_whatsapp_message_gui()
        return ''
    if open_application(query):
        return ''
    if 'screenshot' in query:
        take_screenshot()
        return ''
    if "time" in query:
        _respond(f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}.") 
        return ''
    
    # --- Calculation Command (Improved with word2number integration) ---
    if any(keyword in query for keyword in ("calculate", "do calculation", "what is", "what's")):
        # Step 1: Handle percentage calculation first if it matches
        if _handle_percentage_calculation_query(query):
            return '' 
        # Step 2: If not a percentage, proceed with general calculation logic
        expr_text = query.lower()
        # Remove calculation keywords from the beginning of the query
        for kw in ("what is", "what's", "calculate", "do calculation"):
            if expr_text.startswith(kw):
                expr_text = expr_text[len(kw):].strip()
                break 
        expr_text = expr_text.replace("tell me", "").strip() 
        expr_text = expr_text.rstrip("?")
        if not expr_text: 
            _respond("You asked me to perform a calculation, but no expression was provided.")
            return ''
        try:
            result = perform_calculation(expr_text)
            _respond(f"The result of {expr_text} is {result}")
        except ValueError as e:
            _respond(f"Sorry, I couldn't perform that calculation: {e}")
        except Exception as e:
            _respond("Sorry, I encountered an unexpected error while trying to perform the calculation.")
            logging.error(f"Error in calculation command: {e}")
        return '' 
# --- End of Calculation Command ---

    if "alt tab" in query or "switch tab" in query:
        pyautogui.hotkey("alt", "tab")
        _respond("Switched to the next window.") 
        return ''
    if "dark mode" in query:
        pyautogui.hotkey("ctrl", "shift", "D")
        _respond("Attempted to toggle dark mode.") 
        return ''
    if "light mode" in query:
        pyautogui.hotkey("ctrl", "shift", "L")
        _respond("Attempted to toggle light mode.") 
        return ''
    if "increase volume" in query or "volume up" in query:
        change_volume("up")
        return ''
    if "decrease volume" in query or "volume down" in query:
        change_volume("down")
        return ''
    if "mute" in query:
        change_volume("mute")
        return ''
    if "unmute" in query:
        change_volume("unmute")
        return ''
    if "minimise window" in query:
        pyautogui.hotkey("win", "down")
        _respond("Window minimized.") 
        return ''
    if "maximize window" in query:
        pyautogui.hotkey("win", "up")
        _respond("Window maximized.") 
        return ''
    if "close window" in query:
        pyautogui.hotkey("alt", "f4")
        _respond("Closing the window.") 
        return ''
    if "split window" in query:
        pyautogui.hotkey("win", "left")
        _respond("Window split to the left.") 
        return ''
    if "lock" in query:
        pyautogui.hotkey("win","L")
        _respond("Windows Screen Locked.") 
        return ''
    if "retab window" in query or "move window to right" in query:
        pyautogui.hotkey("win", "right")
        _respond("Window moved to the right.") 
        return ''
    if "select all" in query:
        pyautogui.hotkey("ctrl", "a")
        _respond("All text selected.") 
        return '' 
    if "copy" in query :
        pyautogui.hotkey("ctrl","c")
        _respond("Text copied to clipboard.") 
        return '' 
    if "paste" in query:
        pyautogui.hotkey("ctrl","v")
        _respond("Text pasted from clipboard.") 
        return '' 
    if "clipboard history" in query:
        pyautogui.hotkey("windows","v")
        _respond("Clipboard history opened.") 
        return ''
    if any(term in query for term in ["shutdown", "restart", "log off"]):
        system_control(query)
        return ''
    if any(term in query for term in ["exit", "quit", "stop", "good bye","see you later", "goodbye", "bye nexora"]):
        _respond("Goodbye Vishnu!") 
        try: playsound("activated_nexora_music.mp3")
        except Exception as e: logging.error(f"Error playing exit music: {e}")
        return "exit"
    _respond("I'm not sure how to help with that. You can ask 'help' to see what I can do.")
    return ''

# Main assistant command processing logic for the "Tap to Speak" button
def assistant_thread_worker():
    q = listen()
    if q:
        res = process_query(q)
        if res == "exit": app.after(100, app.destroy)

# Main assistant command processing logic for continuous listening
def start_assistant_core_loop():
    try: playsound("activated_nexora_music.mp3")
    except Exception as e: logging.error(f"Error playing activation music: {e}")
    _respond(wish_me()) 
    while True:
        q = listen()
        if q:
            res = process_query(q)
            if res == "exit": app.after(100, app.destroy); break
        else: time.sleep(1)

# New Idle Animation Function
def animate_idle_state():
    global current_phrase_index, current_dot_count, listening_active, speaking
    if not listening_active and not speaking:
        base_phrase = unique_animation_phrases[current_phrase_index]
        animated_text = f"{base_phrase}{'.'*current_dot_count}"
        update_command_box_gui(animated_text)
        current_dot_count += 1
        if current_dot_count > 5:
            current_dot_count = 1
            current_phrase_index = (current_phrase_index + 1) % len(unique_animation_phrases)
    app.after(500, animate_idle_state)

#----------GUI Setup----------
# Create the main app window
app = ctk.CTk()
app.title("Nexora AGENT - Your Interactive Voice AGENT")
app.geometry("600x600")
app.resizable(False, False)

# Header Frame
header_frame = ctk.CTkFrame(app, fg_color="#3498db", corner_radius=10)
header_frame.pack(pady=20, padx=20, fill="x")
title_label = ctk.CTkLabel(header_frame, text="Nexora (∩^o^)⊃━☆ﾟ.*･｡ﾟ", text_color="white", font=("Segoe UI", 28, "bold"))
title_label.pack(pady=(0, 15))
subtitle_label = ctk.CTkLabel(header_frame, text="Your Interactive Voice Agent", text_color="white", font=("Segoe UI", 16))
subtitle_label.pack(pady=(0, 15))

# Display Area
display_frame = ctk.CTkFrame(app, fg_color="transparent")
display_frame.pack(pady=10, padx=20, fill="both", expand=True)
you_said_label = ctk.CTkLabel(display_frame, text="You said:", anchor="w", font=("Segoe UI", 16))
you_said_label.pack(anchor="w", pady=(0, 5))
command_box = ctk.CTkTextbox(display_frame, height=45, font=("Segoe UI", 14), wrap="word", border_width=1)
command_box.configure(state="disabled")
command_box.pack(fill="x", pady=(0,15))
assistant_says_label = ctk.CTkLabel(display_frame, text="Nexora says:", anchor="w", font=("Segoe UI", 16))
assistant_says_label.pack(anchor="w", pady=(0, 3))
response_box = ctk.CTkTextbox(display_frame, font=("Segoe UI", 14), wrap="word", border_width=1)
response_box.configure(state="disabled")
response_box.pack(fill="both", expand=True)

# Button Frame
button_frame = ctk.CTkFrame(app, fg_color="transparent")
button_frame.pack(pady=15)

def toggle_assistant_active_state():
    global speak_enabled
    speak_enabled = not speak_enabled
    if speak_enabled:
        toggle_assistant_button.configure(text="Nexora: Voice ON", fg_color="#27ae60", hover_color="#2ecc71")
        app.after(10, lambda: _respond("Nexora Voice activated.")) 
    else:
        toggle_assistant_button.configure(text="Nexora: Voice OFF", fg_color="#e74c3c", hover_color="#c0392b")
        app.after(10, lambda: _respond("Nexora Voice deactivated.")) 
        stop_speaking()

toggle_assistant_button = ctk.CTkButton(
    button_frame, text="Nexora: Voice ON", command=toggle_assistant_active_state,
    font=("Segoe UI", 18), height=50, width=180, corner_radius=25,
    fg_color="#27ae60", hover_color="#2ecc71",
)
toggle_assistant_button.pack(side="left", padx=10)

listen_button = ctk.CTkButton(
    button_frame, text="🔊 Tap to Speak",
    command=lambda: Thread(target=assistant_thread_worker, daemon=True).start(),
    font=("Segoe UI", 18), height=50, width=220, corner_radius=25,
    fg_color="#8e44ad", hover_color="#9b59b6"
)
listen_button.pack(side="left", padx=10)

# Footer
footer_label = ctk.CTkLabel(app, text="Powered by VISHNU 💖✨", font=("Segoe UI", 14), text_color="#7f8c8d")
footer_label.pack(pady=(5,10), side="bottom")

# Binding GUI refs into module
def bind_gui_elements():
    globals()['app'] = app
    globals()['command_box'] = command_box
    globals()['response_box'] = response_box

if __name__ == "__main__":
    bind_gui_elements()
    Thread(target=start_assistant_core_loop, daemon=True).start()
    Thread(target=start_scheduler_loop, daemon=True).start()
    app.after(0, animate_idle_state)
    app.mainloop() 