import google.generativeai as ai
from google.generativeai.types.generation_types import StopCandidateException
import json
import AppOpener
from config import API_KEY
import database
# from main1 as 



# List of predefined commands
commands_list = [
    "go to <website name>",
    "search on google <query>",
    "open <app/system tool>",
    "close <app/system tool>",
    "ip address of my device",
    "search on wikipedia <topic>",
    "send message <message>",
    "current temperature <city_name>",
    "play video on youtube <video_name>",
    "current time",
    "battery",
    "pdf <content>",
    "docx <content>",
    "theme",
    "current date",
    "ai mode <query>",
    "shutdown",
    "restart",
    "sleep",
    "user",
    "mute",
    "unmute",
    "Incomplete command: <correct_command>",
    "minimise window",
    "maximise window",
    "close window",
    "type <text>",
    "help",
    "exit"
]

# Configure the API once globally to avoid redundant setup

def scanapp():
    # pass
    app_keys=AppOpener.give_appnames()
    return app_keys

def processcmd(command):
    ai.configure(api_key=API_KEY)

# Create a new model and chat object once
    model = ai.GenerativeModel("gemini-2.0-flash")
    chat = model.start_chat()
    app_keys=scanapp()
    

    with open('task.json', 'r') as file:
        task_data = json.load(file)

# Convert the JSON data to a formatted string
    json_data_str = json.dumps(task_data, indent=2)

    previous_chats=database.get_last_five_conversations()
    
    # Refined prompt that asks the AI to match input with the correct command from the list
    prompt = (
    f"Your name is NOVA, You are a command assistant designed to help users, including those who may be illiterate or make mistakes in their input. "
    f"Your task is to interpret the user's intent and correct any spelling mistakes, command structure errors, or word choice issues. "
    f"Consider the following possibilities for mistakes:\n"
    f"- The user might confuse 'go to' for websites and apps. If they say 'go to' followed by a website name, change it to 'go to <website>.com' if not specified. For apps, return 'open <app>' or 'close <app>' as needed, but only if the app name exists in the user's installed apps, which are listed in {app_keys}.\n"
    f"- If the user says 'open' or 'close' followed by a website name, change it to 'go to <website>.com'.\n"
    f"- Ensure the command returns the exact app name required by the AppOpener library from this list: {app_keys}. If the user provides an app name not listed in {app_keys}, inform the user that the app is not available.\n"
    f"- Match user input to the correct app name supported by the AppOpener library from {app_keys}. This includes handling common variations, abbreviations, and misspellings.\n"
    f"- Handle spelling errors or typos in app names and correct them automatically.\n"
    f"- If the user says something like 'go to <website>' or 'open <website>', check if it's a website. Append '.com' if it's missing, and ensure the response is 'go to <website>.com'.\n"
    f"- If the user says 'search on wikipedia', 'wikipedia search', or any variation of that command, return 'search on wikipedia <topic>' and extract the topic from the command.\n"
    f"- If the user only types 'AI' instead of 'AI mode', assume they meant 'AI mode'.\n"
    f"- The user might give incomplete commands. For example, 'go to google' should be interpreted as a web search, while 'search on google' should include a query if missing.\n"
    f"- If the user gives an incomplete command, such as 'open app' without specifying the app, respond with 'Incomplete command: open <app_name>'. This will guide the user towards the correct format.\n"
    f"- If the user says anything resembling 'help', such as 'run help function', 'show help', 'assist', or 'guide', return the 'help' command.\n"
    f"- If the user says anything resembling 'exit', 'no thanks', 'close', or any phrase indicating the intent to stop or exit the software, return 'exit'.\n"
    f"- If the user asks a question related to any domain or field, interpret the question and provide a relevant answer in 200 words or more, returning it in the format: 'AI mode: <answer>'.\n\n"
    f"- If the user wants to type something, return 'type <text>'. For example, if the user says 'I want to type Hello coders', return 'type Hello coders'.\n\n"
    f"Commands List:\n"
    f"{commands_list}\n\n"
    f"Here is the app name mapping from the user's system (available apps):\n"
    f"{app_keys}\n\n"
    f"Task Data:\n"
    f"{json_data_str}\n\n"
    f"Previous Chat History:\n"
    f"{previous_chats}\n\n"
    f"User Input: {command}\n\n"
    f"Response:\n"
    f"- If the user wants to open a website and says something like 'go to <website_name>' or 'open <website_name>', return 'go to <website_name>.com'.\n"
    f"- For apps, return 'open <app_name>' or 'close <app_name>' if the app exists in {app_keys}, or inform the user that the app is not available if it's not in {app_keys}.\n"
    f"- If the command is incomplete, return 'Incomplete command: <correct_command>'.\n"
    f"- If the user asks a question related to any domain or field, interpret the question and return 'AI mode: <answer>'."
    f"- If the user asks to change or switch themes, return theme"
    f"- If the user asks to generate a PDF with provided content, return 'pdf <user_content>'.\n"
    f"- If the user asks to generate a PDF with specific content like code or generated text, and no content is provided, return 'pdf <generated_content_by_u>', where you generate the content (e.g., 'pdf print(\"Hello World\")' if the user asks for 'Hello World code in Python').\n"
    f"- If the user asks to generate a DOCX with provided content, return 'docx <user_content>'.\n"
    f"- If the user asks to generate a DOCX with specific content like code or generated text, and no content is provided, return 'docx <generated_content_by_u>', where you generate the content (e.g., 'docx print('Hello World') if the user asks for 'Hello World code in Python').\n"

    f"- If the user asks about themselves, return 'user'\n"
    f"- If the command is incomplete or not recognized, generate a response yourself and return it.\n"
    f"- If the user refers to something from previous messages, use the context from past interactions in {previous_chats}.\n"
    f"- Maintain a conversational flow and answer accordingly."
)



    try:
        # Send the refined prompt to the AI
        response = chat.send_message(prompt)
        matched_command = response.text.strip()

        # Debug print the raw response from AI
        print(f"Raw AI Response: {matched_command}")

        # Return the processed response from AI
        return matched_command

    except StopCandidateException as e:
        print("AI Error: That question seems to be causing an issue. Please try rephrasing.")
        print(f"Error Details: {e}")
        return "Command not recognized. Please try again."
    except Exception as e:
        print("AI Error: Sorry, something went wrong.")
        print(f"Error: {e}")
        return "Command not recognized. Please try again."
    
# print(processcmd("what time is it"))
# print(app_name)