import pyttsx3
import speech_recognition as sr
import datetime
import requests
from fpdf import FPDF
import wikipedia
import webbrowser
import pywhatkit as kit
import pygetwindow as gw
import aiprocess as ap
import AppOpener
import markdown
# import gemini_ai
import os
from docx import Document
import time
import pyautogui
import subprocess
import os
import io
import datetime
from database import *
import sys
import psutil
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
print("backend....")

mic_off=False
obj=None
msg = None
engine = pyttsx3.init("sapi5")
commands = ["open", "shutdown", "ip address of my device", "minimise window","close window","maximise window","go to","search on google","search on wikipedia",
            "current temperature","send message","sleep","current date","restart","play video on youtube","help","close","send message","battery","current time","Incomplete","mute","unmute","exit","user","type","theme","pdf","docx","cut","copy","paste","undo","open clipboard","save","new tab","alt tab","select all","close tab","minimise all","show desktop","find","new window","start","notification","new desktop","switch right","switch left","close desktop","volume up","volume down","brightness up","brightness down","bottom right"]
# Text to speak function
def set_speech_rate(rate):
    engine.setProperty('rate', rate)

def speak(text,speed=200):
    set_speech_rate(speed)
    
    if engine._inLoop:
        time.sleep(1)
        engine.endLoop()
    else:
        engine.stop()
    engine.say(text)
    engine.runAndWait()
    # engine.say(text)
    # engine.runAndWait()




# Voice to text
def takecmd():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        if mic_off: return 
        r.pause_threshold = 1
        if mic_off: return 
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)  # Increased timeout
            if mic_off: return 
        except sr.WaitTimeoutError:
            speak("Listening timed out. Please try again.")
            return 
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
            return 
        except sr.RequestError:
            speak("Sorry, there was an issue with the request.")
            return 
        return audio
    
def recoginze(audio):
    print("Recognizing...")
    try :
        if mic_off: return "none"
        if audio is None:
            return "none"
        r = sr.Recognizer()
        query = r.recognize_google(audio)
        if mic_off: return "none"
        print(query)
    except sr.WaitTimeoutError:
            speak("Listening timed out. Please try again.")
            return "none"
    except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
            return "none"
    except sr.RequestError:
            speak("Sorry, there was an issue with the request.")
            return "none"
    return query.lower()

def wish():
    now = int(datetime.now().hour)
    if 5 <= now < 12:
        speak("Good Morning")
    elif 12 <= now < 17:
        speak("Good Afternoon")
    else:
        speak("Good Evening")



def copy():
    pyautogui.hotkey('ctrl', 'c')
    return "Successfully copied to clipboard."

def paste():
    pyautogui.hotkey('ctrl', 'v')
    return "Successfully pasted from clipboard."

def cut():
    pyautogui.hotkey('ctrl', 'x')
    return "Successfully cut to clipboard."

def undo():
    pyautogui.hotkey('ctrl', 'z')
    return "Successfully undone the last action."

def open_clipboard():
    pyautogui.hotkey('win', 'v')
    return "Successfully opened clipboard history."

def save():
    pyautogui.hotkey('ctrl', 's')
    return "Successfully saved the file."

def new_tab():
    pyautogui.hotkey('ctrl', 't')
    return "Successfully opened a new tab."

def select_all():
    pyautogui.hotkey('ctrl', 'a')
    return "Successfully selected all text/items."

def close_tab():
    pyautogui.hotkey('ctrl', 'w')
    return "Successfully closed the tab."

def alt_tab():
    pyautogui.hotkey('alt', 'tab')
    return "Successfully switched to the next window."

def show_desktop():
    pyautogui.hotkey('win', 'd')
    return "Successfully minimized all windows and showed the desktop."

def minimize_all():
    pyautogui.hotkey('win', 'm')
    return "Successfully minimized all windows."

def find():
    pyautogui.hotkey('ctrl', 'f')
    return "Successfully opened the Find/Search dialog."

def new_window():
    pyautogui.hotkey('ctrl', 'n')
    return "Successfully opened a new window."

def open_start():
    pyautogui.press('win')
    return "Successfully opened the Start menu."

def notifications():
    pyautogui.hotkey('win', 'n')
    return "Successfully opened the notifications panel."

def new_virtual_desktop():
    pyautogui.hotkey('ctrl', 'win', 'd')
    return "Successfully created a new virtual desktop."

def switch_virtual_desktop_right():
    pyautogui.hotkey('ctrl', 'win', 'right')
    return "Successfully switched to the next virtual desktop."
def switch_virtual_desktop_left():
    pyautogui.hotkey('ctrl', 'win', 'left')
    return "Successfully switched to the previous virtual desktop."

def close_virtual_desktop():
    pyautogui.hotkey('ctrl', 'win', 'f4')
    return "Successfully closed the current virtual desktop."

def volume_up():
    pyautogui.press('volumeup')
    return "Successfully increased the volume."

def volume_down():
    pyautogui.press('volumedown')
    return "Successfully decreased the volume."

def brightness_up():
    pyautogui.press('brightnessup')
    return "Successfully increased the brightness."

def brightness_down():
    pyautogui.press('brightnessdown')
    return "Successfully decreased the brightness."

def bottom_right():
    pyautogui.hotkey('win', 'a')
    return "Successfully opened the Action Center (from here you can toggle airplane mode)."

def wiki(query):
    
    try: 
        result=wikipedia.summary(query,sentences=2)
        print(f"According to wikipedia {result} for more information go to wikipedia.com")
        return f"According to wikipedia {result} for more information go to wikipedia.com"
        
    except Exception as e:
        return f"Something went wrong {e}"
       

def google_search(query):
    try:
        kit.search(query)
        return f"{query} Searching from google"
    except Exception as e:
        return f"Something went wrong {e}"


def ytvideo(video_name):
    try:
        kit.playonyt(video_name)
        return f"{video_name} is going to play on YouTube"
    except Exception as e:
        return f"Something went wrong {e}"

def temperature(city):
    api_key = "32b87d5cde3a4809b7344238251601"  # replace with your actual WeatherAPI key
    base_url = "http://api.weatherapi.com/v1/current.json"
    
    complete_url = f"{base_url}?key={api_key}&q={city}"
    response = requests.get(complete_url)
    weather_data = response.json()
    
    if "error" not in weather_data:
        # Extract temperature
        temp_celsius = weather_data['current']['temp_c']
        condition = weather_data['current']['condition']['text']
        
        return f"The temperature in {city} is {temp_celsius}°C with {condition}."
    else:
        return "Please Enter valid city name"


def send_message(message):
    msg = message
    return f"sending  message {message}"

def incomplete_command(complete_command):
    return f"The command you provide is incomplete command, the complete {complete_command}"

def open_apps(app_name):
    # pass
    try:
        AppOpener.open(app_name,match_closest=True)
        return f"{app_name} is Opened"
    except Exception as e:
        return f"Something went wrong {e}"
        
        
        
def mute():
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(1, None)
        return "System muted!"
    except Exception as e:
        return f"Something went wrong {e}"


def unmute():
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
    # Unmute the system
        volume.SetMute(0, None)
        return "System unmuted!"
    except Exception as e:
        return f"Something went wrong {e}"

def process_airesponse(response):
    for command in commands:
        if response.startswith(command): 
            param = response[len(command):].strip()  
            return command,param
    return None,None


    
def battery():
    try:
        battery = psutil.sensors_battery()
        if battery is not None:
            percentage = battery.percent
            plugged = battery.power_plugged
            if plugged:
                status="is"
            else:
                status="is Not"
            return f"Your current battery percentage is {percentage}% and currently charger {status} Plugged In"
        else:
            return "Battery not found" 
    except Exception as e:
        return f"Something went wrong {e}"
    

def help_function():
    help_text = (
        "Welcome to the Command Assistant!, My name is Nova, Here are some commands you can use:\n\n"
        "1. **Go to <website name>**\n"
        "   - Example: 'Go to amazon' or 'Go to google'\n"
        "   - Opens the website in your browser. The assistant will append '.com' to the website name if not specified.\n\n"
        
        "2. **Search on Google <query>**\n"
        "   - Example: 'Search on Google Python tutorials'\n"
        "   - Performs a Google search with the specified query.\n\n"
        
        "3. **Open <app/system tool>**\n"
        "   - Example: 'Open calculator' or 'Open notepad'\n"
        "   - Opens the specified application or system tool.\n\n"
        
        "4. **IP address of my device**\n"
        "   - Example: 'IP address of my device'\n"
        "   - Provides the IP address of your device.\n\n"
        
        "5. **Search on Wikipedia <topic>**\n"
        "   - Example: 'Search on Wikipedia Python programming'\n"
        "   - Searches Wikipedia for the specified topic and reads a summary.\n\n"
        
        "6. **Send message**\n"
        "   - Example: 'Send message'\n"
        "   - Prompts you to provide a phone number and a message to send via WhatsApp.\n\n"
        
        "7. **Current temperature <city_name>**\n"
        "   - Example: 'Current temperature in New York'\n"
        "   - Provides the current temperature for the specified city.\n\n"
        
        "8. **Play video on YouTube <video_name>**\n"
        "   - Example: 'Play video on YouTube Python tutorial'\n"
        "   - Searches for and plays the specified video on YouTube.\n\n"
        
        "9. **Current time**\n"
        "   - Example: 'Current time'\n"
        "   - Provides the current time.\n\n"
        
        "10. **AI mode <query>**\n"
        "    - Example: 'AI mode What is the weather like?'\n"
        "    - Interacts with the AI model to process your query in AI mode.\n\n"
        
        "11. **Shutdown**\n"
        "    - Example: 'Shutdown'\n"
        "    - Shuts down the computer.\n\n"
        
        "12. **Restart**\n"
        "    - Example: 'Restart'\n"
        "    - Restarts the computer.\n\n"
        
        "13. **Sleep**\n"
        "    - Example: 'Sleep'\n"
        "    - Puts the computer into sleep mode.\n\n"
        
        "14. **Minimise window**\n"
        "    - Example: 'Minimise window'\n"
        "    - Minimizes the currently active window.\n\n"
        
        "15. **Maximise window**\n"
        "    - Example: 'Maximise window'\n"
        "    - Maximises the currently active window.\n\n"
        
        "16. **Close window**\n"
        "    - Example: 'Close window'\n"
        "    - Closes the currently active window.\n\n"
        
          "17. **type <text>**\n"
        "     - Example: 'Type Hello, my name is Nova'\n"
        "     - Automatically types the specified text as if you typed it manually..\n\n"
        
         "18. **No thanks exit**\n"
        "    - Example: 'No thanks exit'\n"
        "    - Exits the assistant.\n\n"
        
        "If you need help with a specific command or have any questions, just ask!"
    )
    return help_text
    
          
def sleep():
    return "sleep_"
def shutdown():
    return "shutdown_"

def restart():
    return "restart_"




        
        
def ip_address():
    
    try:
        ip=requests.get("https://api.ipify.org").text
        return f"Your IP Address is {ip}"
    except Exception as e:
        return f"Something went wrong {e}"

def minimize():
    
    try:
        window = gw.getActiveWindow()
        if window:
            window.minimize()
            return "current window is minimized"
        else:
            return "Current window can't recognize"
    except Exception as e:
        return f"Something went wrong {e}"
        
        
def maximize():
    
    try:
        window = gw.getActiveWindow()
        if window:
            window.maximize()
            print("success")
            return "Current Window is Maximized"
        else:
            return "Current window can't recognize"
    except Exception as e:
        return f"Something went wrong {e}"
        
              
def closewindow():
    
    try:
        window = gw.getActiveWindow()
        if window:
            window.close()
            return "Current Window is Closed"
        else:
            return "Current can't recognize"
    except Exception as e:
        return f"Something went wrong {e}"
        


def open_website(web_name):
    try:
        webbrowser.open(f"http://{web_name}")
        return f"Opening {web_name} in your browser..."
    except Exception as e:
        return f"Failed to open {web_name}"

def user_name():
    f_name,l_name=get_username()
    return f"Your name is {f_name} {l_name}. How may I assist you further?"

 
def close_apps(app_name):
    try:
        captured_output = io.StringIO()
        sys.stdout = captured_output
        AppOpener.close(app_name)
        sys.stdout = sys.__stdout__
        result = captured_output.getvalue().strip()        
        if "not running" in result:
         return "Sorry I can't close the app due to security concern and permission issues, If the app you want to close is your current window, then try again and say close the current window"
        return f"Closing {app_name}"   
    except Exception as e:
        return f"Something went wrong {e}"

# def ai_mode(query):
#     result=gemini_ai.aispeechmode(query)
#     return result

def current_time():
    time = datetime.now().strftime("%I:%M %p") 
    return f"The current time is {time}"

def exit_fucntion():
    now = datetime.now().hour
    
    if 5 <= now < 12:
        print ("Goodbye! Have a great day ahead!")
        return "Goodbye! Have a great day ahead!"
    elif 12 <= now< 17:
        print("Goodbye! Have a wonderful afternoon!")
        return "Goodbye! Have a wonderful afternoon!"
    elif 17 <= now < 21:
        print("Goodbye! Have a pleasant evening!")
        return  "Goodbye! Have a pleasant evening!"
    else:
        print("Goodbye! Have a restful night!")
        return "Goodbye! Have a restful night!"
    
# def query_fucn(answer):
#     return answer

def write_anything(text):
    
    # Type the modified text
    pyautogui.write(text, interval=0.1)
    return "Your text is successfully written"

def toggle_theme():
    # Query current theme setting from the registry
    result = subprocess.run(
        ["reg", "query", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize", "/v", "AppsUseLightTheme"],
        capture_output=True, text=True)

    # If the result contains 'AppsUseLightTheme' with value 1, it's in light mode, so switch to dark mode
    if "1" in result.stdout:
        # Set to dark theme
        os.system("reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize\" /v AppsUseLightTheme /t REG_DWORD /d 0 /f")
        os.system("reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize\" /v SystemUsesLightTheme /t REG_DWORD /d 0 /f")
        return "Theme is now set to Dark"
    else:
        # Set to light theme
        os.system("reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize\" /v AppsUseLightTheme /t REG_DWORD /d 1 /f")
        os.system("reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize\" /v SystemUsesLightTheme /t REG_DWORD /d 1 /f")
        return "Theme is now set to Light"

def current_date():
    current_date = datetime.now()
    date_str = current_date.strftime("%B %d, %Y")
    return f"Today's date is {date_str}"

def generate_pdf(content):
    # Get the Downloads folder path
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

    # Specify the base filename for the PDF
    base_filename = "NOVA_generated_pdf"
    pdf_filename = base_filename + ".pdf"
    pdf_path = os.path.join(downloads_folder, pdf_filename)

    # Check if file already exists and create a unique filename
    counter = 1
    while os.path.exists(pdf_path):
        pdf_filename = f"{base_filename}({counter}).pdf"
        pdf_path = os.path.join(downloads_folder, pdf_filename)
        counter += 1

    # Create PDF instance
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Set font for the PDF
    pdf.set_font("Arial", size=12)

    # Add content to the PDF
    pdf.multi_cell(0, 10, content)

    # Output the PDF to the Downloads folder
    pdf.output(pdf_path)
    
    if os.name == 'nt': 
        os.startfile(pdf_path)

    return f"PDF generated successfully: {pdf_path}"



def generate_docx(content):
    # Get the Downloads folder path
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

    # Specify the base filename for the DOCX
    base_filename = "NOVA_generated_docx"
    docx_filename = base_filename + ".docx"
    docx_path = os.path.join(downloads_folder, docx_filename)

    # Check if file already exists and create a unique filename
    counter = 1
    while os.path.exists(docx_path):
        docx_filename = f"{base_filename}({counter}).docx"
        docx_path = os.path.join(downloads_folder, docx_filename)
        counter += 1

    # Create a new Word document
    doc = Document()
    doc.add_paragraph(content)

    # Save the document
    doc.save(docx_path)
    
    if os.name == 'nt': 
        os.startfile(docx_path)

    return f"DOCX generated successfully: {docx_path}"


def default_fucntion(query):
    return query

command_actions={
    "open":open_apps,
    "search on wikipedia":wiki,
    "sleep":sleep,
    "minimise window":minimize,
    "maximise window":maximize,
    "close window":closewindow,
    "go to":open_website,
    "search on google":google_search,
    "ip address of my device":ip_address,
    "play video on youtube":ytvideo,
    "restart":restart,
    "shutdown":shutdown,
    "mute":mute,
    "unmute":unmute,
    "current date":current_date,
    "send message":send_message,
    "current temperature":temperature,
    "current time":current_time,
    # "ai mode":ai_mode,
    "battery":battery,
    "help":help_function,
    "close":close_apps,
    "user":user_name,
    "theme":toggle_theme,
    "type":write_anything,
    "pdf":generate_pdf,
    "cut":cut,
    "copy":copy,
    "paste":paste,
    "undo":undo,
    "clipboard":open_clipboard,
    "save":save,
    "new tab":new_tab,
    "alt tab":alt_tab,
    "select all":select_all,
    "close tab":close_tab,
    "minimise all":minimize_all,
    "show desktop":show_desktop,
    "find":find,
    "new window":new_window,
    "start":open_start,
    "notification":notifications,
    "new desktop":new_virtual_desktop,
    "switch left":switch_virtual_desktop_left,
    "switch right":switch_virtual_desktop_right,
    "close desktop":close_virtual_desktop,
    "volume up":volume_up,
    "volume down":volume_down,
    "brightness up":brightness_up,
    "brightness down":brightness_down,
    "bottom right":bottom_right,
    "docx":generate_docx,
    "Incomplete":incomplete_command,
    "exit":exit_fucntion
}


def input_from_gui(user_input,self):
    global obj
    obj=self
    query=ap.processcmd(user_input)
    command,param=process_airesponse(query)
    
    if command==None and param==None:
        result=default_fucntion(query)
        return result
    try:
        if command:
            action = command_actions.get(command)
            if param:
                result=action(param)
                return result# If there is a parameter, pass it to the function
            else:
                result=action()
                return result
    except Exception as e:
                return str(e)

def microphone():
    
        wish()
        speak("How can I help you, Sir?")
        
        while True:
            query = takecmd().lower()
            user_query=query
            if query=="none":
                continue
            query=ap.processcmd(query)
            command,param=process_airesponse(query)
            
            if command==None and param==None:
                default_fucntion(query)

            try:
                if command:
                    action = command_actions.get(command)
                    if param:
                        action(param)  # If there is a parameter, pass it to the function
                    else:
                        action()
            except Exception as e:
                print(e)
            time.sleep(5)
            speak("Sir, Do you have any other work")

def keyboard():
        wish()
        speak("How can I help you, Sir?")
        
        while True:
            query =input("Enter your query: ")
            if query=="none":
                continue
            query=ap.processcmd(query)
            command,param=process_airesponse(query)
            
            if command==None and param==None:
                default_fucntion(query)

            try:
                if command:
                    action = command_actions.get(command)
                    if param:
                        action(param)  # If there is a parameter, pass it to the function
                    else:
                        action()
            except Exception as e:
                print(e)
            time.sleep(5)
            speak("Sir, Do you have any other work")
    
        
if __name__ == "__main__":
    # microphone()
    # keyboard()
    input_from_gui("shutdown")
    
    
    
    
        
    
 
    
    
    
    
        
        