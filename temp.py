import speech_recognition as sr
import pyttsx3
import pyautogui
import pygetwindow as gw
import uiautomation as auto
import os
import time

# Initialize text-to-speech engine
engine = pyttsx3.init()
def speak(text):
    print(f"[Assistant]: {text}")
    engine.say(text)
    engine.runAndWait()

# Initialize speech recognizer
recognizer = sr.Recognizer()

def listen_command():
    with sr.Microphone() as source:
        print("Listening for command...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio).lower()
            print(f"[You]: {command}")
            return command
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return None
        except sr.RequestError:
            print("Speech recognition service unavailable.")
            return None

def focus_window(app_name):
    windows = gw.getWindowsWithTitle(app_name)
    if windows:
        windows[0].activate()
        speak(f"Focused on {app_name}")
    else:
        speak(f"Window {app_name} not found")

def click_button(button_name):
    window = auto.GetForegroundControl()
    button_name = button_name.lower().strip()

    print("Scanning for available UI elements...")  # Debugging line
    found = False

    for child in window.GetChildren():
        print(f"Found UI Element: {child.Name}")  # Debugging line
        if child.Name.lower().strip() == button_name:
            child.SetFocus()
            time.sleep(0.5)  # Ensure focus before clicking
            child.Click()
            speak(f"Clicked {button_name}")
            found = True
            break

    if not found:
        speak(f"'{button_name}' not found")

def control_volume(action):
    if action == "up":
        pyautogui.press("volumeup")
        speak("Volume increased")
    elif action == "down":
        pyautogui.press("volumedown")
        speak("Volume decreased")
    elif action == "mute":
        pyautogui.press("volumemute")
        speak("Volume muted")

def manage_window(action):
    if action == "minimize":
        pyautogui.hotkey("win", "down")
        speak("Window minimized")
    elif action == "maximize":
        pyautogui.hotkey("win", "up")
        speak("Window maximized")
    elif action == "close":
        pyautogui.hotkey("alt", "f4")
        speak("Window closed")

def execute_command(command):
    if "click" in command:
        word = command.replace("click", "").strip()
        click_button(word)
    elif "open" in command:
        app = command.replace("open", "").strip()
        os.system(f"start {app}")
        speak(f"Opening {app}")
    elif "focus" in command:
        app = command.replace("focus", "").strip()
        focus_window(app)
    elif "scroll down" in command:
        pyautogui.scroll(-500)
        speak("Scrolled down")
    elif "scroll up" in command:
        pyautogui.scroll(500)
        speak("Scrolled up")
    elif "volume up" in command:
        control_volume("up")
    elif "volume down" in command:
        control_volume("down")
    elif "mute" in command:
        control_volume("mute")
    elif "minimize window" in command:
        manage_window("minimize")
    elif "maximize window" in command:
        manage_window("maximize")
    elif "close window" in command:
        manage_window("close")
    elif "exit" in command:
        speak("Exiting voice navigation.")
        exit()
    else:
        speak("Command not recognized.")

if __name__ == "__main__":
    speak("Voice navigation activated. Say a command.")
    while True:
        user_command = listen_command()
        if user_command:
            execute_command(user_command)
