import win32api
import wx
import wx.adv
import time
import pyperclip
import keyboard
import threading
import requests

from sql import DataBase
from encryption import *

TRAY_ICON = 'tray_image.png'
TIME_SLEEP_BETWEEN_KEYPRESS = 0.2
EMPTY_NAME = "<<error>>"
API_URL = "http://127.0.0.1:8000/api/v1/translate/"

LETTERS_RUS = "фисвуапршолдьтщзйкыегмцчняФИСDEÀÏРШJËДЬТЩЗЙКЫЕГМЦЧНЯ"
LETTERS_ENG = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

db = DataBase("s_translator.db")
db.connect()
db.create_table_if_not_exists()

last_word = {'word': None, 'translation': None}


def create_menu_item(menu, label, func, enabled=True):
    item = wx.MenuItem(menu, -1, label)
    item.Enable(enabled)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        frame.task_bar_icon = self
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.frame.task_bar_icon = self

    def CreatePopupMenu(self):
        menu = wx.Menu()

        # Just hints to the user
        create_menu_item(menu, 'Do translit: ctrl+shift+`', self.func, enabled=False)
        create_menu_item(menu, 'Do translate: ctrl+shift+1', self.func, enabled=False)

        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def func(self, event):
        pass

    def set_icon(self, path, text=""):
        icon = wx.Icon(path)
        self.SetIcon(icon, text)

    def on_left_down(self, event):
        self.frame.Close()
        self.Destroy()

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self.frame.Destroy()


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
        print("mouse moved")
        self.Close()

    def on_key_pressed(self, event):
        print("Key pressed")
        self.Close()

    def on_timer(self, event):
        self.Close()
        # self.Destroy()


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 700),
                          style=wx.RESIZE_BORDER | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.wnd = None

        self.worker = WorkerThread(self)
        self.worker.start()

        self.timer = wx.Timer(self)

        self.Bind(wx.EVT_ICONIZE, self.new_frame, id=10)
        self.Bind(wx.EVT_ICONIZE, self.do_translit, id=20)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

    def on_timer(self, event):
        self.close_window()

    def close_window(self):
        if self.wnd:
            self.wnd.Close()

    def get_data_from_clipboard(self):
        pyperclip.copy(EMPTY_NAME)
        time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
        keyboard.press_and_release('ctrl+c')
        time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
        data_from_clipboard = pyperclip.paste()
        if data_from_clipboard == EMPTY_NAME:
            keyboard.press_and_release('ctrl+c')

            # in case of processor being busy, increase the time after saving to the clipboard and getting from there
            time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS * 3)

        data_from_clipboard = pyperclip.paste()
        return data_from_clipboard

    def new_frame(self, event):
        mouse_pos = win32api.GetCursorPos()
        message = self.do_translate()
        if message:
            self.wnd = PopupWindow(self, mouse_pos, message=message)
            self.wnd.Show()

            time_till_pop = 3000 + len(message[10:]) * 70
            self.timer.Start(time_till_pop)
        # wx.CallLater(10000, self.Close_window)

    def do_translit(self, event):
        data_from_clipboard = self.get_data_from_clipboard()

        rus = 1
        for i in data_from_clipboard:
            if i in LETTERS_RUS:
                rus += 1
            else:
                rus -= 1

        if rus > 0:
            mytable = data_from_clipboard.maketrans(LETTERS_RUS, LETTERS_ENG)
        else:
            mytable = data_from_clipboard.maketrans(LETTERS_ENG, LETTERS_RUS)

        try:
            translit_data = data_from_clipboard.translate(mytable)

            time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
            pyperclip.copy(translit_data)
            time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)

            print(f"{translit_data = }")

            keyboard.press_and_release('ctrl+v')
        except UnicodeEncodeError:
            print(f"UnicodeEncodeError...")

    def do_translate(self):
        data_from_clipboard = self.get_data_from_clipboard()
        if len(data_from_clipboard) >= 2:
            if data_from_clipboard == last_word['word']:
                translated_text = last_word['translation']
            else:
                if data_from_clipboard != EMPTY_NAME:
                    translated_text = db.check_word(data_from_clipboard)
                    # print(f"{translated_text = }")
                    if not translated_text:
                        rus = 0
                        for i in data_from_clipboard:
                            if i in LETTERS_RUS:
                                rus += 1
                            else:
                                rus -= 1
                        if '.' in data_from_clipboard:
                            data_from_clipboard = data_from_clipboard.replace('.', '. ')
                        if '_' in data_from_clipboard:
                            data_from_clipboard = data_from_clipboard.replace('_', '-')

                        if rus > 0:
                            target_language = 'en'
                            source_language = 'ru'
                        else:
                            target_language = 'ru'
                            source_language = 'en'

                        params = {"word": data_from_clipboard,
                                  'target_language': target_language,
                                  'source_language': source_language,
                                  },

                        response = requests.get(
                            API_URL,
                            params={"encrypted_data": do_encrypt(params)},
                            timeout=5
                        )

                        print(f"{response.status_code = }")
                        print(f"{response.content = }")
                        if response.status_code == 200:
                            translated_text = response.json()['translation']
                            print(f"{response.json()['translation'] = }")
                            # print(f"{response.content = }")
                            print(f"{response.status_code = }")

                            # save only 1-2 word phrases
                            if len(data_from_clipboard.strip().split(' ')) <= 2:
                                db.query_save(data_from_clipboard, translated_text)
                        elif response.status_code == 403:
                            translated_text = f"<<{response.json()['detail']}>>"
                            # print("12111111111111")
                        else:
                            translated_text = f"<<{response.json()}>>"
                            # translated_text = response.json()['error']
                            # translated_text = '<<403 auth error>>'

                        print("new translation")
                    else:
                        print("used existing word from db")
                        pass
                    # print(f"{translated_text = }")
                    pyperclip.copy(translated_text)
                    time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
                else:
                    translated_text = EMPTY_NAME
            last_word['word'] = data_from_clipboard
            last_word['translation'] = translated_text
        else:
            translated_text = None
        print(f"{translated_text = }")
        # keyboard.press_and_release('ctrl+v')
        return translated_text


class WorkerThread(threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window
        self.window.wnd = None
        keyboard.add_hotkey('ctrl+shift+1', self.do_translate)
        keyboard.add_hotkey('ctrl+shift+`', self.do_translit)

    def do_translate(self):
        if self.window.wnd:
            self.window.wnd.Close()
        evt = wx.IconizeEvent(id=10, iconized=True)
        wx.PostEvent(self.window.GetEventHandler(), evt)

    def do_translit(self):
        evt = wx.IconizeEvent(id=20, iconized=True)
        wx.PostEvent(self.window.GetEventHandler(), evt)


class App(wx.App):
    def __init__(self, redirect):
        super().__init__(redirect=redirect)
        self.frame = None

    def OnInit(self):
        self.frame = MainWindow(None, "Focus mode")
        # wx.lib.inspection.InspectionTool().Show()  # to inspect all parameters of windows\panels\widgets
        TaskBarIcon(self.frame)
        return True


app = App(redirect=False)
app.MainLoop()

db.disconnect()
print("Exiting app correctly...")
