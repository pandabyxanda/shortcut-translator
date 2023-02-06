import os
import sys

import win32api
import wx
import wx.adv
import time
import pyperclip
import keyboard
import threading
import requests

from sql import DataBase
from encryption import do_encrypt
from keyboard_language import get_keyboard_language

# 0.2 seconds, CPU need time between saving to clipboard by ctrl+c and using info from clipboard
TIME_SLEEP_BETWEEN_KEYPRESS = 0.2

EMPTY_NAME = "<<error>>"
TRANSLATOR_API_URL = "https://keeptranslations.na4u.ru/api/v1/translate/"
# TRANSLATOR_API_URL = str(os.environ.get('TRANSLATOR_API_URL', default="http://127.0.0.1:8000/api/v1/translate/"))
LETTERS_RUS = "фисвуапршолдьтщзйкыегмцчняФИСDEÀÏРШJËДЬТЩЗЙКЫЕГМЦЧНЯ"
LETTERS_ENG = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


TRAY_ICON = resource_path("tray_image.png")


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        frame.task_bar_icon = self
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.frame.task_bar_icon = self

    @staticmethod
    def create_menu_item(menu, label, func, enabled=True):
        item = wx.MenuItem(menu, -1, label)
        item.Enable(enabled)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.Append(item)
        return item

    def CreatePopupMenu(self):
        menu = wx.Menu()

        # Just hints to the user
        self.create_menu_item(menu, 'Do translit: ctrl+shift+`', lambda event: None, enabled=False)
        self.create_menu_item(menu, 'Do translate: ctrl+shift+1', lambda event: None, enabled=False)

        menu.AppendSeparator()
        self.create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path, text=""):
        icon = wx.Icon(path)
        self.SetIcon(icon, text)

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self.frame.Destroy()
        # self.frame.worker.stop()


class PopupWindow(wx.Frame):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance:
            cls.__instance.Close()
        cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, parent, mouse_pos=(0, 0), message=''):
        size = (300, 50)
        pos = (mouse_pos[0], mouse_pos[1] - size[1] - 20)
        wx.Frame.__init__(self, parent, title="title1", size=size, pos=pos,
                          style=wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR)
        self.SetBackgroundColour("#f9f7e9")
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(12)

        message_list = message.split("\r\n")
        if len(message_list) == 1 and len(message_list[0]) > 100:
            message = message_list[0]
            n = 100
            message_list = [message[i:i + n] for i in range(0, len(message), n)]

        if len(message_list) == 1:
            message_list = [message_list[0].strip()]

        self.st = []
        text_width, text_height = 0, 0
        for i in range(0, len(message_list)):
            st_t = wx.StaticText(self, label=message_list[i], pos=(0, 0))
            st_t.SetFont(font)
            self.st.append(st_t)
            dc = wx.ClientDC(self.st[i])
            text_dimensions = dc.GetTextExtent(self.st[i].GetLabel())
            if text_dimensions[0] > text_width:
                text_width = text_dimensions[0]
            if text_dimensions[1] > text_height:
                text_height = text_dimensions[1]

        screen_size = wx.DisplaySize()
        if text_width + 10 * 2 + pos[0] > screen_size[0]:
            pos = (
                screen_size[0] - (text_width + 10 * 2) - 50, mouse_pos[1] - (text_height * len(message_list) + 20) - 20)
        else:
            pos = (mouse_pos[0] + 20, mouse_pos[1] - (text_height * len(message_list) + 20) - 20)
        self.SetPosition(pos)
        self.SetSize((text_width + 10 * 2, text_height * len(message_list) + 20))

        for i in range(0, len(self.st)):
            self.st[i].SetPosition((10, i * text_height + 10 - 2))
        self.Bind(wx.EVT_LEFT_DOWN, self.on_key_pressed, id=wx.ID_ANY)
        self.Bind(wx.EVT_MOTION, self.on_mouse_moved, id=wx.ID_ANY)

    def on_mouse_moved(self, event):
        # print("mouse moved")
        self.Close()

    def on_key_pressed(self, event):
        # print("Key pressed")
        self.Close()

    def on_timer(self, event):
        self.Close()
        # self.Destroy()


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 700),
                          style=wx.RESIZE_BORDER | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.wnd = None
        self.ready = True

        self.worker = WorkerThread(self)
        self.worker.start()

        self.timer = wx.Timer(self)

        self.timer_rare_call = wx.Timer(self)

        self.Bind(wx.EVT_ICONIZE, self.new_frame, id=10)
        self.Bind(wx.EVT_ICONIZE, self.do_translit, id=20)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.Bind(wx.EVT_TIMER, self.on_timer_rare_call, self.timer_rare_call)

    def on_timer(self, event):
        self.close_window()

    def close_window(self):
        if self.wnd:
            self.wnd.Close()

    @staticmethod
    def get_data_from_clipboard():
        pyperclip.copy(EMPTY_NAME)
        time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
        keyboard.press_and_release(keys_ctrl_c)
        time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
        data_from_clipboard = pyperclip.paste()
        if data_from_clipboard == EMPTY_NAME:
            keyboard.press_and_release(keys_ctrl_c)

            # in case of processor being busy, increase the time after saving to the clipboard and getting from there
            time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS * 3)

        data_from_clipboard = pyperclip.paste()
        return data_from_clipboard

    def on_timer_rare_call(self, event):
        self.ready = True

    def new_frame(self, event):

        # prevent multiple press
        if self.ready:
            if self.wnd:
                # print(f"{self.wnd = }")
                self.wnd.Close()

            self.timer_rare_call.Start(1000)
            self.ready = False

            mouse_pos = win32api.GetCursorPos()
            data_from_clipboard = self.get_data_from_clipboard()

            if len(data_from_clipboard) < 2:
                message = None
            elif data_from_clipboard == last_word['word']:
                message = last_word['translation']
            elif data_from_clipboard == EMPTY_NAME:
                message = EMPTY_NAME
            else:

                # try to find the translation in local database
                translated_text = db.check_word(data_from_clipboard)
                if translated_text:
                    message = translated_text
                else:
                    message = self.do_translate(data_from_clipboard)

            if message:
                self.wnd = PopupWindow(self, mouse_pos, message=message)
                self.wnd.Show()

                time_till_pop = 3000 + len(message[10:]) * 70
                self.timer.Start(time_till_pop)
                # wx.CallLater(10000, self.Close_window)

    def do_translit(self, event):
        print("translit")
        data_from_clipboard = self.get_data_from_clipboard()
        print(f"{data_from_clipboard = }")
        if data_from_clipboard != EMPTY_NAME:
            rus = 1
            for i in data_from_clipboard:
                if i in LETTERS_RUS:
                    rus += 1
                else:
                    rus -= 1

            if rus > 0:
                my_table = data_from_clipboard.maketrans(LETTERS_RUS, LETTERS_ENG)
            else:
                my_table = data_from_clipboard.maketrans(LETTERS_ENG, LETTERS_RUS)

            try:
                translit_data = data_from_clipboard.translate(my_table)
                pyperclip.copy(translit_data)
                time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
                data_from_clipboard_new = pyperclip.paste()
                if data_from_clipboard_new == data_from_clipboard:
                    pyperclip.copy(translit_data)
                    time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS * 3)
                # print(f"{translit_data = }")
                keyboard.press_and_release(keys_ctrl_v)
            except UnicodeEncodeError:
                print(f"UnicodeEncodeError...")

    @staticmethod
    def do_translate(data_from_clipboard_raw):

        data_from_clipboard = data_from_clipboard_raw.replace('.', '. ').replace('_', '-')

        # if there are more Russian letters in the text, then we translate into English
        rus = 0
        for i in data_from_clipboard:
            if i in LETTERS_RUS:
                rus += 1
            else:
                rus -= 1
        if rus > 0:
            target_language = 'en'
            source_language = 'ru'
        else:
            target_language = 'ru'
            source_language = 'en'

        data = {
            "word": data_from_clipboard,
            'target_language': target_language,
            'source_language': source_language,
        }

        try:
            response = requests.get(
                TRANSLATOR_API_URL,
                params={"encrypted_data": do_encrypt(data)},
                timeout=5
            )

            if response.status_code == 200:
                translated_text = response.json()['translation']

                # save only 1-3 word phrases
                if len(data_from_clipboard.strip().split(' ')) <= 3:
                    db.query_save(data_from_clipboard, translated_text)
            else:
                translated_text = f"<<{response.json()}>>"
        except Exception:
            translated_text = "<<connection error>>"

        pyperclip.copy(translated_text)

        last_word['word'] = data_from_clipboard_raw
        last_word['translation'] = translated_text
        return translated_text


class WorkerThread(threading.Thread):
    """
    This class is needed to constantly monitor keys state simultaneously with
    the execution of the graphical part of the application
    """

    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window
        self.window.wnd = None
        keyboard.add_hotkey(keys_ctrl_shift_1, self.do_translate)
        keyboard.add_hotkey(keys_ctrl_shift_yo, self.do_translit)

    def do_translate(self):
        if self.window.wnd:
            self.window.wnd.Close()
        evt = wx.IconizeEvent(id=10, iconized=True)
        wx.PostEvent(self.window.GetEventHandler(), evt)

    def do_translit(self):
        evt = wx.IconizeEvent(id=20, iconized=True)
        wx.PostEvent(self.window.GetEventHandler(), evt)

    # def run(self):
    #     # Do some long running task
    #     keyboard.wait()
    # while True:
    #     print("Waiting for")
    #     time.sleep(5)
    # wx.CallAfter(self.window.button.Enable)


class App(wx.App):
    def __init__(self, redirect):
        super().__init__(redirect=redirect)
        self.frame = None

    def OnInit(self):
        self.frame = MainWindow(None, "Focus mode")
        # wx.lib.inspection.InspectionTool().Show()  # to inspect all parameters of windows\panels\widgets
        TaskBarIcon(self.frame)
        return True


if __name__ == "__main__":
    db = DataBase("s_translator.db")
    db.connect()
    db.create_table_if_not_exists()

    last_word = {'word': None, 'translation': None}

    # keyboard lib does not work correctly with the names of the keys set in dif language
    current_language = get_keyboard_language()
    # print(f"{current_language = }")
    if 'eng' in current_language.lower():
        keys_ctrl_c = 'ctrl+c'
        keys_ctrl_v = 'ctrl+v'
        keys_ctrl_shift_yo = 'ctrl+shift+`'
    else:
        keys_ctrl_c = 'ctrl+с'
        keys_ctrl_v = 'ctrl+м'
        keys_ctrl_shift_yo = 'ctrl+shift+ё'
    keys_ctrl_shift_1 = 'ctrl+shift+1'

    app = App(redirect=False)
    app.MainLoop()

    db.disconnect()
    print("Exiting app correctly...")
