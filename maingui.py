# ========================== Standard Library Imports ==========================
import sys
import os
import threading
import time
import re
# ==============================================================================


# ========================== PyQt5 Core GUI Imports ============================
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMenu, QVBoxLayout, QAction,
    QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QScrollArea, QFrame
)
from PyQt5.QtCore import (
    Qt, QSize, QThread, pyqtSignal, QPropertyAnimation, QEvent
)
from PyQt5.QtGui import QIcon, QMovie, QPixmap
from PyQt5 import QtGui
# ==============================================================================


# ========================== Text/HTML Handling ================================
# Utilities to convert markdown to HTML, handle HTML encoding, etc.
import html
import markdown
# ==============================================================================


# ========================== Custom Project Modules ============================
from CustomMessageBox import *    # Custom UI message popups
from backend import *             # Core assistant functions
import backend as b               # Alias for backend usage
import database as db            # Interface to database (chat memory)
# ==============================================================================

print("maingui...")
BtnTextFont = '25px'#deafult text size
toggleMic = True # true means mic mode is toggled
themeColor = '#0085FF' #the blue theme color
speaking = True  # is reprsent if the speaking is working or not
prompt = "none" # it is used to send the input from gui to chatthread 
thread = True # to check if the user want to destroy the thread
up_key_press_count = 0 # to count the up arrow key press count
btnStyle = f"background-color: #07151E; font-size: {BtnTextFont}; color: {themeColor}; padding: 5px; border-radius:30px; border:5px solid {themeColor}" #common button style
movie = None # varidle for animation , it is global because it needs to take the animation in the popup and the maingui



# =============================== PopupWindow Class ================================
# Purpose: Provides a compact always-on-top floating window for microphone controls,
# mute toggle, and quick access to the main window.
# ==================================================================================
class PopupWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # ---------------- Window Settings ----------------
        self.setWindowIcon(QIcon('icons/nova_no_bg.png'))
        self.initUI()

    def initUI(self):
        # ---------------- Window Attributes ----------------
        self.setWindowTitle('NOVA')
        self.setStyleSheet("background-color: #07151E; color: #ffffff;")
        self.setGeometry(400, 0, 300, 100)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)

        # ---------------- Shared Button Style ----------------
        btnStyle = f"background-color: #07151E; font-size: {BtnTextFont}; color: {themeColor}; padding: 10px; border-radius:15px; border:5px solid {themeColor}"

        # ---------------- Main Vertical Layout ----------------
        layout = QVBoxLayout()

        # ========================== Top Mic Button Section ==========================
        # Purpose: Contains mic button created from main window with functionality.
        self.mic_button = self.main_window.create_mic_button_popup()
        self.mic_button.clicked.connect(self.main_window.micon)
        # ===========================================================================

        # ========================== Show Main Window Button =========================
        # Purpose: Opens main window UI from popup.
        self.show_main_button = QPushButton(self)
        self.show_main_button.setIcon(QIcon('icons/popup_open.png'))
        self.show_main_button.setIconSize(QSize(40, 40))
        self.show_main_button.clicked.connect(self.show_main_window)
        self.show_main_button.setStyleSheet(btnStyle)
        self.show_main_button.setFixedSize(60, 60)
        # ===========================================================================

        # ========================== State Label Display =============================
        # Purpose: Displays status text like listening / paused etc.
        self.state = QLabel("")
        self.state.setStyleSheet(f"""
            color:{themeColor};
            font-size: 30px;
            font-weight: bold;
        """)
        self.state.setFixedWidth(400)
        # ===========================================================================

        # ========================== Mute Button Control =============================
        # Purpose: Mutes or unmutes microphone input.
        self.mute_button = QPushButton()
        self.mute_button.setStyleSheet(btnStyle)
        self.mute_button.setIcon(QIcon('icons/mute.png'))
        self.mute_button.setIconSize(QSize(40, 40))
        self.mute_button.setFixedSize(60, 60)
        self.mute_button.clicked.connect(self.main_window.toggle_mute)
        # ===========================================================================

        # ========================== Bottom Controls Layout ==========================
        # Purpose: Aligns mic, state, mute, and main window button in a row.
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.mic_button)
        bottom_layout.addWidget(self.state, alignment=Qt.AlignCenter)
        bottom_layout.addWidget(self.mute_button)
        bottom_layout.addWidget(self.show_main_button)
        # ===========================================================================

        # ---------------- Final Layout Assignment ----------------
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    # ========================== Show Main Interface Logic ==========================
    # Purpose: Opens main interface if mic toggle is off and hides popup.
    def show_main_window(self):
        if not toggleMic:
            self.main_window.toggle_input_mode()
        self.hide()
        self.main_window.show_main_interface()
    # ===========================================================================


# ================================= ChatWindow Class =================================
# Purpose: Main QWidget for chat UI. Handles message input, display bubbles, scrolling,
#          styling, and chat history management.
# ====================================================================================



class ChatWindow(QWidget, QThread):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # ============================== Scrollable Chat Area ==============================
        # Purpose: Displays chat messages inside a scrollable region.
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.message_history = []

        # Container for chat messages
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        print(self.maximumWidth())
        # Optional margin control (commented)
        # self.chat_layout.setContentsMargins(int(self.maximumWidth()*0.00002), 0, int(self.maximumWidth()*0.00002), 0)
        self.chat_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.chat_container)
        layout.addWidget(self.scroll_area)

        # ------------------ Scrollbar Styling ------------------
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #0F1C25;
                border: none;
                padding-left: 30px;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                border: none;
                background: #07151E;
                                       
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 4px;
            }
            QScrollBar::handle {
                background: #0085FF;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:hover {
                background: #0085FF;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                background: none;
                height: 0px;
            }
            QScrollBar::add-page, QScrollBar::sub-page {
                background: none;
            }
        """)
        
        # ==================================================================================

        # =============================== Input Area Layout ================================
        # Purpose: Text input field with a send button aligned in a row.
        self.input_layout = QHBoxLayout()
        self.input_layout.addStretch()

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter Your Prompt")
        self.message_input.setStyleSheet(
            f"background-color: #07151E; font-size: {BtnTextFont}; color: #6CCAFF; padding: 5px; border-radius:21px; border:5px solid {themeColor}"
        )
        self.message_input.setFixedSize(600, 100)
        self.input_layout.addWidget(self.message_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setFixedWidth(100)
        self.send_button.setStyleSheet(
            f"background-color: #07151E; font-size: {BtnTextFont}; color: {themeColor}; padding: 5px; border-radius:20px; border:5px solid {themeColor}"
        )
        self.input_layout.addWidget(self.send_button)
        self.input_layout.addStretch()
        layout.addLayout(self.input_layout)
        # ==================================================================================

        # ========================= Window Styling & Scroll Animation ======================
        self.setLayout(layout)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #07151E;
                color: white;
                border: 1px solid #ccc;
                border-radius: 20px;
                font-size: 20px;
                padding: 5px;
            }
            QPushButton {
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 20px;
                padding: 10px;
                background-color: #07151E;
            }
            QPushButton:hover {
                background-color: #128C7E;
            }
        """) 

        scrollbar = self.scroll_area.verticalScrollBar()
        # ==================================================================================

    # ============================== Send Button Function ===============================
    def send_message(self):
        global prompt
        message = self.message_input.toPlainText().strip()
        if message:
            prompt = message
            self.message_input.clear()
    # ===================================================================================

    # ============================= Add Chat Bubble Function ============================
    def add_message(self, message, is_sent=False):
        bubble_widget = self.create_bubble_widget(message, is_sent)
        self.chat_layout.addWidget(bubble_widget)
        self.scroll_area.verticalScrollBar().setSliderPosition(
            self.scroll_area.verticalScrollBar().maximum() + (bubble_widget.height() * 20)
        )
    # ===================================================================================

    # ========================= Get Last Message from History ===========================
    def get_last_message(self,count):
        if self.message_history and count<=len(self.message_history):
            return self.message_history[-1*count]
        return ""
    # ===================================================================================

    # ========================= Create Individual Chat Bubble ===========================
    def create_bubble_widget(self, message, is_sent):
        bubble_frame = QFrame()
        bubble_layout = QVBoxLayout(bubble_frame)

        if message.startswith("You: "):
            is_sent = True
            self.message_history.append(message.replace("You: ", "",1))
            message = message.replace("You: ", "",1)

        # Split message into text and code blocks
        code_blocks = re.findall(r"```(.*?)```", message, re.DOTALL)
        text_parts = re.split(r"```.*?```", message, flags=re.DOTALL)
        message_container = QVBoxLayout()

        for index, text in enumerate(text_parts):
            if text.strip():
                t = text.strip()
                lines = t.split('\n')
                current_start = 0

                if len(lines) > 111:
                    while current_start < len(lines):
                        end_index = min(current_start + 111, len(lines))
                        bubble_text = '\n'.join(lines[current_start:end_index])
                        text_bubble = QLabel()
                        text_bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
                        text_bubble.setWordWrap(True)
                        text_bubble.setTextFormat(Qt.RichText)
                        text_bubble.setStyleSheet(f"""
                            background-color: {themeColor if is_sent else '#0A1E2A'};
                            color: white;
                            border-radius: 10px;
                            padding: 10px;
                            font-size: {BtnTextFont};
                        """)
                        text_bubble.setText(convert_markdown_to_html(bubble_text.strip()))
                        message_container.addWidget(text_bubble)
                        current_start = end_index
                else:
                    text_bubble = QLabel()
                    text_bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
                    text_bubble.setWordWrap(True)
                    text_bubble.setTextFormat(Qt.RichText)
                    text_bubble.setStyleSheet(f"""
                        background-color: {themeColor if is_sent else '#0A1E2A'};
                        color: white;
                        border-radius: 10px;
                        padding: 10px;
                        font-size: {BtnTextFont};
                    """)
                    text_bubble.setText(convert_markdown_to_html(text.strip()))
                    message_container.addWidget(text_bubble)

                if index < len(code_blocks):
                    code_bubble = QLabel()
                    code_bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
                    code_bubble.setText(convert_markdown_to_html(format_code_for_qlabel(code_blocks[index])))
                    code_bubble.setWordWrap(True)
                    code_bubble.setTextFormat(Qt.RichText)
                    code_bubble.setStyleSheet(f"""
                        background-color: #1A2638;
                        color: white;
                        font-family: 'JetBrains Mono', 'Fira Code', monospace;
                        border-radius: 30px solid black;
                        padding: 10px;
                        white-space: pre-wrap;
                        font-size: {BtnTextFont};
                    """)
                    message_container.addWidget(code_bubble)

        alignment_layout = QHBoxLayout()
        if is_sent:
            alignment_layout.addStretch()
            alignment_layout.addLayout(message_container)
        else:
            alignment_layout.addLayout(message_container)
            alignment_layout.addStretch()

        bubble_layout.addLayout(alignment_layout)
        bubble_layout.setContentsMargins(10, 5, 10, 5)
        return bubble_frame
    # ===================================================================================

    # =========================== Delete All Conversation Bubbles ========================
    def delete_conversation(self):
        db.delete_conversation()
        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.chat_container.update()
    # ===================================================================================


# NovaInterface with chat integration# ----------------------------- NOVA INTERFACE MAIN CLASS -----------------------------
class NovaInterface(QWidget):
    def __init__(self):
        global movie  # For mic animation
        movie = QMovie("icons/mic_ani.gif")
        movie.speed = -500

        global in_custom_message_box

        # ---------------- State Display Label ----------------
        self.state = QLabel("")
        self.state.setStyleSheet(f"""
            color:{themeColor};
            font-size: 30px;
            font-weight: bold;
        """)

        super().__init__()

        # ---------------- Chat Window ----------------
        self.chat_window = ChatWindow()
        self.is_popup_mode = False

        # ---------------- Window Attributes ----------------
        self.setWindowIcon(QIcon('icons/nova_no_bg.png'))
        self.initUI()
        self.chat_window.message_input.installEventFilter(self)

    # ---------------- Window State Changes ----------------
    def changeEvent(self, event):  
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized() and not in_custom_message_box:
                print("Window minimized")
                self.show_popup()
            elif self.isMaximized():
                print("Window maximized")
            else:
                self.setBaseSize(1000, 1000)
                self.chat_window.chat_layout.setContentsMargins(0,0,0,0)
                print("Window restored")

        if event.type() == QEvent.ActivationChange:
            if not self.isActiveWindow() and not in_custom_message_box:
                print("Window lost focus")
                self.show_popup()
            else:
                print("Window gained focus")

        super().changeEvent(event)

    # ---------------- Main UI Setup ----------------
    def initUI(self):
        self.setWindowTitle('NOVA')  
        self.setStyleSheet("background-color: #0F1C25; color: #ffffff;")
        self.popup = PopupWindow(self)
        self.setMinimumSize(1200, 1000)

        self.main_layout = QVBoxLayout()

        # ---------------- Top Bar ----------------
        top_layout = QHBoxLayout()

        # SK Button (Top-Right User Menu)
        self.sk_label = QPushButton("U")
        self.sk_label.setStyleSheet(f"""
            background-color: #07151E; 
            color: {themeColor}; 
            font-size:{BtnTextFont};  
            padding: 5px; 
            border-radius: 20px; 
            border:5px solid {themeColor};
        """)
        self.sk_label.setFixedSize(50, 50)
        self.sk_label.clicked.connect(self.show_user_menu)

        # ---------------- User Menu ----------------
        self.user_menu = QMenu(self)
        self.user_menu.setStyleSheet("""
            QMenu {
                background-color: #07151E;
                border: 2px solid #0085FF;
                border-radius: 5px;
            }
            QMenu::item {
                padding: 10px 30px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QMenu::item:selected {
                background-color:  #0085FF;
                color: white;
            }
            QMenu::separator {
                height: 2px;
                background-color: #0085FF;
                margin: 5px 15px;
            }
        """)

        logout_action = QAction('Logout', self)
        logout_action.triggered.connect(self.logout)
        self.user_menu.addAction(logout_action)
        self.user_menu.addSeparator()
        delete_action = QAction('Delete', self)
        delete_action.triggered.connect(self.delete_account)
        self.user_menu.addAction(delete_action)

        # ---------------- NOVA Branding ----------------
        self.nova_icon = QLabel()
        img = QPixmap('icons/nova_no_bg.png')
        self.nova_icon.setPixmap(img)
        self.nova_icon.setStyleSheet("background-color: white; border-radius: 30px; padding: 5px;")
        
        nova_label = QLabel("NOVA")
        nova_label.setStyleSheet(f"color: {themeColor}; font-size: 30px; font-weight: bold;")

        # ---------------- Delete Conversation Button ----------------
        delete_button = QPushButton()
        delete_button.setStyleSheet(f"""
            background-color: #07151E;
            font-size: {BtnTextFont}; 
            color: {themeColor}; 
            padding: 5px; 
            border-radius:20px; 
            border:5px solid {themeColor}
        """)
        delete_button.setIcon(QIcon('icons/delete.png'))
        delete_button.setIconSize(QSize(30, 30))
        delete_button.clicked.connect(self.delete_conversation)

        # Add Top Bar Widgets
        top_layout.addWidget(self.nova_icon)
        top_layout.addWidget(nova_label)
        top_layout.addStretch()
        top_layout.addWidget(delete_button)
        top_layout.addWidget(self.sk_label)

        # ---------------- Bottom Controls ----------------
        self.bottom_layout = QHBoxLayout()

        # Mic Button
        self.mic_button = self.create_mic_button()       
        self.mic_button.clicked.connect(self.micon)
        self.mic_button.setStyleSheet("border: none;")

        control_size = 40

        # Text Mode Button
        self.text_mode_button = QPushButton()
        self.text_mode_button.setStyleSheet(btnStyle)
        self.text_mode_button.setIcon(QIcon('icons/keyboard.png'))
        self.text_mode_button.setIconSize(QSize(control_size, control_size))
        self.text_mode_button.clicked.connect(self.toggle_input_mode)

        # Mute Button
        self.mute_button = QPushButton()
        self.mute_button.setStyleSheet(btnStyle)
        self.mute_button.setIcon(QIcon('icons/mute.png'))
        self.mute_button.setIconSize(QSize(control_size, control_size))
        self.mute_button.clicked.connect(self.toggle_mute)

        # Float Button
        self.float_window_button = QPushButton()
        self.float_window_button.setStyleSheet(btnStyle)
        self.float_window_button.setIcon(QIcon('icons/popup_open.png'))
        self.float_window_button.setIconSize(QSize(control_size, control_size))
        self.float_window_button.clicked.connect(self.show_popup)

        self.bottom_layout.addStretch()
        self.bottom_layout.addWidget(self.text_mode_button)
        self.bottom_layout.addWidget(self.mic_button)
        self.bottom_layout.addWidget(self.mute_button)
        self.bottom_layout.addWidget(self.float_window_button)
        self.bottom_layout.addStretch()

        self.bottom = QWidget()
        self.bottom.setLayout(self.bottom_layout)
        self.bottom.setStyleSheet(f"""
            border: 5px solid {themeColor};
            border-radius: 40px;
            background-color: #07151E;
            padding: 0px;
        """)

        self.b = QHBoxLayout()
        self.b.addStretch()
        self.b.addWidget(self.bottom)
        self.b.addStretch()

        # ---------------- Chat Window (Centered and Fixed Width) ----------------
        self.chat_window.setFixedWidth(1200)
        self.chatwindow = QHBoxLayout()
        self.chatwindow.addStretch()
        self.chatwindow.addWidget(self.chat_window)
        self.chatwindow.addStretch()

        # ---------------- Add Everything to Main Layout ----------------
        self.main_layout.addLayout(top_layout)
        self.main_layout.addLayout(self.chatwindow)
        self.main_layout.addLayout(self.b)
        self.main_layout.addWidget(self.state, alignment=Qt.AlignCenter)

        self.setLayout(self.main_layout)
        self.chat_window.message_input.hide()
        self.chat_window.send_button.hide()       

    # ----------------- Additional Functional Components -----------------
    def delete_conversation(self):
        threading.Thread(target=self.chat_window.delete_conversation).start()

    def logout(self):
        try:
            if os.path.exists('user_config.txt'):
                os.remove('user_config.txt')
            self.close()
            if(os.path.exists("signup_login.exe")):
                os.system("signup_login.exe")
            else:
                os.system("python signup_login.py") 
        except Exception as e:
            print(f"Error during logout: {e}")

    def delete_account(self):
        global in_custom_message_box
        try:
            in_custom_message_box = True
            result = CustomMessageBox.show_message(text="Are you sure you want to delete your account?", B1="Yes", B2="No")
            if result == 1:
                db.delete_account() 
                if os.path.exists('user_config.txt'):
                    os.remove('user_config.txt')
                self.close()
                if(os.path.exists("signup_login.exe")):
                    os.system("signup_login.exe")
                else:
                    os.system("python signup_login.py") 
        except Exception as e:
            print(f"Error during account deletion: {e}")
        finally:
            in_custom_message_box = False

    def show_main_interface(self):
        self.is_popup_mode = False
        self.setWindowFlags(Qt.Window)
        self.showMaximized()

    def toggle_input_mode(self):
        global toggleMic
        if self.chat_window.message_input.isVisible():
            self.chat_window.message_input.hide()
            self.chat_window.send_button.hide()
            self.mic_button.show()
            self.text_mode_button.setIcon(QIcon('icons/keyboard.png'))
            toggleMic = True
            if not self.is_popup_mode:
                b.mic_off = False
        else:
            self.chat_window.message_input.show()
            self.chat_window.send_button.show()
            self.mic_button.hide()
            self.text_mode_button.setIcon(QIcon('icons/mic.png'))
            toggleMic = False
            b.mic_off = True

    def create_mic_button(self):
        global movie
        mic_size = 100
        mic_button = QPushButton(self)
        mic_button.setFixedSize(mic_size , mic_size)
        mic_label = QLabel(mic_button)
        mic_label.setGeometry(0, 0, mic_size , mic_size)
        mic_label.setMovie(movie)
        mic_label.setScaledContents(True)
        movie.start()
        return mic_button

    def create_mic_button_popup(self):
        global movie
        mic_size = 100
        mic_button = QPushButton(self)
        mic_button.setFixedSize(mic_size , mic_size)
        mic_label = QLabel(mic_button)
        mic_label.setGeometry(0, 0, mic_size , mic_size)
        mic_label.setMovie(movie)
        mic_label.setScaledContents(True)
        movie.start()
        return mic_button

    def show_popup(self):
        global toggleMic
        global movie
        if not toggleMic:
            self.toggle_input_mode()
            b.mic_off = True 
            movie.stop()
            movie.jumpToFrame(0)
        self.hide()
        self.is_popup_mode = True
        self.popup.show()

    def set_name(self, text):
        self.sk_label.setText(text)

    def eventFilter(self, obj, event):
        global  up_key_press_count
        if obj == self.chat_window.message_input and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return and not event.modifiers():
                if not toggleMic:
                    self.chat_window.send_message()
                    up_key_press_count = 0
                return True
            elif event.key() == Qt.Key_Return and event.modifiers() == Qt.ShiftModifier:
                self.chat_window.message_input.insertPlainText("\n")
                return True
            elif event.key() == Qt.Key_Up:
                up_key_press_count += 1 
                last_message = self.chat_window.get_last_message(up_key_press_count)
                if last_message:
                    self.chat_window.message_input.setPlainText(last_message)
                    self.chat_window.message_input.moveCursor(QtGui.QTextCursor.End)
                return True
        return super().eventFilter(obj, event)

    def state_(self, text):
        self.popup.state.setText(text)
        self.state.setText(text)

    def micon(self):
        global movie
        global thread
        if not thread:
            thread_function()
            thread = True
        if b.mic_off: 
            b.mic_off = False
            movie.start()
        else: 
            b.mic_off = True
            movie.stop()
            movie.jumpToFrame(0)
        print("b.mic_off:", b.mic_off)

    def toggle_mute(self):
        global speaking
        speaking = not speaking
        if speaking:
            self.mute_button.setIcon(QIcon('icons/mute.png'))
            self.popup.mute_button.setIcon(QIcon('icons/mute.png'))
        else:
            self.mute_button.setIcon(QIcon('icons/unmute.png'))
            self.popup.mute_button.setIcon(QIcon('icons/unmute.png'))
        print(f"Muted: {not speaking}")

    def sleep_(self):
        global in_custom_message_box
        in_custom_message_box = True
        result = CustomMessageBox.show_message(self, "Are you sure you want to Sleep your pc")
        in_custom_message_box = False
        try:
            if result == 1:
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            else:
                ret = "Sleep canceled"
        except Exception as e:
            ret = f"Something Went wrong {e}"
        self.chat_window.add_message(ret)
        speak(ret)

    def shutdown_(self):
        global in_custom_message_box
        in_custom_message_box = True
        result = CustomMessageBox.show_message(self, "Are you sure you want to shutdown your pc")
        in_custom_message_box = False
        try:
            if result == 1:
                os.system("shutdown /s /t 0")
            else:
                ret = "Shutdown Cancelled"
        except Exception as e:
            ret = f"Something Went wrong {e}"
        self.chat_window.add_message(ret)
        speak(ret)

    def restart_(self):
        global in_custom_message_box
        in_custom_message_box = True
        result = CustomMessageBox.show_message(self, "Are you sure you want to Resatart your pc")
        in_custom_message_box = False
        try:
            if result == 1:
                os.system("shutdown /r /t 0")
            else:
                ret = "Restart canceled"
        except Exception as e:
            ret = f"Something Went wrong {e}"
        self.chat_window.add_message(ret)
        speak(ret)

    def show_user_menu(self):
        self.user_menu.exec_(self.sk_label.mapToGlobal(self.sk_label.rect().bottomLeft()))

    def send_message(self, message):
        global in_custom_message_box
        in_custom_message_box = True
        number = CustomInputBox.show_input_dialog("Please provide the phone number to which I should send messages")
        while len(number) <= 9:
            number = CustomInputBox.show_input_dialog(f"The provided phone number have only {len(number)} digits Please Enter again")
        in_custom_message_box = False
        country_code = "+91"
        number = f"{country_code}{number}"
        threading.Thread(target=kit.sendwhatmsg_instantly, args=(number, message)).start()
        self.chat_window.add_message("Message "+message+"sent to " + number + "\nwill be delivered in a minute")
        speak("Message "+message+" sending to " + number + ", \nwill be delivered in a minute")
        time.sleep(1)

    


# =============================== ChatThread Class ===============================
# Purpose: Handles background operations such as receiving messages,
#          executing system commands (shutdown, sleep, restart),
#          text-to-speech, and maintaining chat state.
# =================================================================================

class ChatThread(QThread):
    # ---------------------------------- Signals ----------------------------------
    message_received = pyqtSignal(str)   # Signal to send message to UI
    micon = pyqtSignal()                 # Signal to control mic icon animation
    restart = pyqtSignal()              # Signal to restart the system
    shutdown = pyqtSignal()             # Signal to shutdown the system
    sleep = pyqtSignal()                # Signal to put system to sleep
    state = pyqtSignal(str)             # Signal to update current state label
    name = pyqtSignal(str)              # Signal to set user's name/initials
    send_message = pyqtSignal(str)      # Signal to trigger WhatsApp message send
    # -----------------------------------------------------------------------------

    def __init__(self, obj):
        super().__init__()

    def run(self):
        flag = True

        # --------------------- Global Variables Used by Thread ---------------------
        global prompt      # Input from GUI for processing
        global thread      # Flag for thread activity
        global speaking    # Indicates whether speaking is enabled
        # ----------------------------------------------------------------------------

        thread = True  # Initialize thread flag

        try:
            # ------------------- Function to Fetch Previous Conversation -------------------
            def fecth_converson():
                self.name.emit(db.get_user_initials())  # Emit user initials

                conversations = db.get_conversations()
                if conversations:
                    for conv in conversations:
                        encrypted_user_input = conv.to_dict().get('user_input')
                        encrypted_assistant_response = conv.to_dict().get('assistant_response')
                        try:
                            # Decrypt conversation data
                            user_input = db.decrypt_data(encrypted_user_input.encode('utf-8')) if isinstance(encrypted_user_input, str) else db.decrypt_data(encrypted_user_input)
                            assistant_response = db.decrypt_data(encrypted_assistant_response.encode('utf-8')) if isinstance(encrypted_assistant_response, str) else db.decrypt_data(encrypted_assistant_response)
                            self.message_received.emit(user_input)
                            self.message_received.emit(assistant_response)
                        except Exception as decryption_error:
                            print(f"Decryption error for conversation ID {conv.id}: {decryption_error}")
            # ----------------------------------------------------------------------------------

            threading.Thread(target=fecth_converson).start()

            # -------------------- Greeting on Thread Start ---------------------
            wish()
            self.state.emit("How can I help you, Sir?")
            speak("How can I help you, Sir?")
            # -------------------------------------------------------------------

            # --------------------- Main Listening Loop --------------------------
            while True:    
                if flag:
                    flag = False

                # ------------------- Microphone Input Handling -------------------
                if toggleMic and not b.mic_off:
                    self.state.emit("Listening...")
                    takecmd_ = takecmd()
                    self.state.emit("Recognizing...")
                    query = recognize(takecmd_).lower()

                # ------------------- Keyboard Input Handling ---------------------
                else:
                    if not toggleMic:
                        self.state.emit("keyboard mode")
                    else:
                        self.state.emit("Listening stopped")
                    time.sleep(0.001)
                    query = prompt
                    prompt = "none"
                # ------------------------------------------------------------------

                if query == "none":
                    continue

                # ------------------ Handle Mic Off Icon Toggle -------------------
                elif toggleMic and not b.mic_off:
                    self.micon.emit()
                    flag = True
                # -----------------------------------------------------------------

                # -------------------- Process the Input Query ---------------------
                self.state.emit("Thinking...")
                self.message_received.emit("You: " + query)

                result = input_from_gui(query, self)

                # ------------------- System Command Triggers ----------------------
                if result == "restart_":
                    self.restart.emit()
                    result = "restarting your computer"

                if result == "shutdown_":
                    self.shutdown.emit()
                    result = "shutdowning your computer"

                if result == "sleep_":
                    self.sleep.emit()
                    result = "sleeping your computer"

                if result.__contains__("sending  message"):
                    speak("Please provide the phone number to which I should send messages.")
                    self.send_message.emit(result.replace("sending  message", "", 1))
                    result = ""
                    
                # ------------------------------------------------------------------

                self.message_received.emit(result)
                self.state.emit("Speaking...")

                # --------------- Save Conversation to DB -------------------------
                db.save_conversation("You: " + query, result)
                # ------------------------------------------------------------------

                # ------------------- Text-to-Speech in Chunks ---------------------
                delimiters = r"[\n,.:!?;]"
                for rt in re.split(delimiters, result):
                    rt = rt.strip()
                    if rt:
                        if (not b.mic_off) or not speaking:
                            self.micon.emit()
                            print("mic off")
                            self.state.emit("muted")
                            break
                        self.state.emit(rt)
                        speak(rt)
                # ------------------------------------------------------------------

                prompt = "none"

                # --------------- Thread Termination Condition ---------------------
                if result.__contains__("Goodbye! "):
                    self.state.emit("")
                    thread = False
                    break
                # ------------------------------------------------------------------

                # -------------------- Re-enable Mic After Response ---------------
                if toggleMic:
                    self.micon.emit()
                time.sleep(1)
                # ------------------------------------------------------------------

        except Exception as e:
            print(e)

    
def thread_function():
    chat_thread.start()          

def format_code_for_qlabel(code):
    if "<!DOCTYPE html>" not in code:
        """ Converts code to an HTML-friendly format while preserving tabs and indentation. """
        html_code = code.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")  # Replace tabs with spaces
        html_code = html_code.replace(" ", "&nbsp;")  # Preserve spaces
        html_code = html_code.replace("\n", "<br>")  # Preserve new lines
        return f"<editor>{html_code}</editor>"
    else:
        return html.escape(code)  # Escape HTML characters in code block

def convert_markdown_to_html(text):
    # Convert markdown to HTML using the markdown library with additional extensions
    extensions = [
        'extra',        # Enables additional Markdown features like tables and footnotes
        'codehilite',   # Adds syntax highlighting for code blocks
        'toc',          # Generates a Table of Contents based on headings
        'nl2br',        # Converts newlines to <br> for better text formatting
        'sane_lists',   # Ensures consistent list formatting
        'fenced_code',  # Enables triple-backtick code blocks
        'admonition'    # Supports note/warning/info boxes
    ]
    
    html_content = markdown.markdown(text, extensions=extensions)
    bootstrap_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                background-color: #07151E;
                color: #E8EAED;
                font-family: Arial, sans-serif;
                margin: 0;
                line-height: 1.6;
                font-size: 1.2rem;
            }}
            h1, h2, h3 {{ 
                color: #6CCAFF;
                font-weight: 500;
            }}
            p {{ 
                font-size: 1.3rem;
                margin-bottom: 1rem;
            }}
            a {{
                color: #6CCAFF;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            code {{
                color: {themeColor};
                padding: 2px 5px;
                border-radius: 3px;
                font-family: monospace;
                background-color: #1A2638;
                border-radius: 10px;
                padding: 10px;
                font-family: 'JetBrains Mono', 'Fira Code', monospace;
            }}
            editor {{
                color: white;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: monospace;
                background-color: #1A2638;
                border-radius: 10px;
                padding: 10px;
                font-family: 'JetBrains Mono', 'Fira Code', monospace;
            }}
            pre {{
                background-color: #1a2638;
                border-radius: 5px;
                padding: 10px;
                overflow-x: auto;
                font-family: monospace;


            }}
            blockquote {{
                border-left: 4px solid #6CCAFF;
                padding-left: 10px;
                color: #B0BEC5;
                margin: 10px 0;
            }}
            ul, ol {{
                padding-left: 2rem;
                font-size: 1.3rem;
            }}
            li {{
                margin-bottom: 0.5rem;
            }}
            img {{
                max-width: 100%;
                height: auto;
                border-radius: 0.5rem;
                margin: 1rem 0;
            }}
        </style>
    </head>
    <body>
        <div>
            {html_content}
        </div>
    </body>
    </html>
    """
    
    return bootstrap_html

if __name__ == '__main__' and os.path.exists("user_config.txt"):
    try:
        app = QApplication(sys.argv)    
        ex = NovaInterface()
        ex.showMaximized()
        chat_thread = ChatThread(ex)
        chat_thread.message_received.connect(ex.chat_window.add_message)    
        chat_thread.micon.connect(ex.micon)
        chat_thread.restart.connect(ex.restart_)
        chat_thread.shutdown.connect(ex.shutdown_)
        chat_thread.sleep.connect(ex.sleep_)
        chat_thread.state.connect(ex.state_)
        chat_thread.name.connect(ex.set_name)
        chat_thread.send_message.connect(ex.send_message)
        chat_thread.start()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
elif not os.path.exists("user_config.txt"):
    if(os.path.exists("signup_login.exe")):
                os.system("signup_login.exe")
    else:            
            os.system("python signup_login.py")      