import pyautogui
import win32api
import wx
import wx.adv
# import ctypes
import time
import pyperclip
import keyboard
# import multiprocessing
import threading

from sql import DataBase
# import msvcrt
from google_translate import make_google_translation

TRAY_ICON = 'united-kingdom (1).png'
TIME_SLEEP_BETWEEN_KEYPRESS = 0.3

db = DataBase("s_translator.db")
db.connect()
db.create_table_if_not_exists()



def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
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
        # create_menu_item(menu, 'Site', self.on_hello)
        # menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path, text=""):
        icon = wx.Icon(path)
        self.SetIcon(icon, text)

    def on_left_down(self, event):
        print('Tray icon was left-clicked.')
        self.frame.Close()
        self.Destroy()

    def on_exit(self, event):
        print('Closing from the tray')
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
        for i in range(0, len(message_list)):
            st_t = wx.StaticText(self, label=message_list[i], pos=(0, 0))
            st_t.SetFont(font)
            self.st.append(st_t)
        raw_max_length_index = \
            [x for x in range(0, len(message_list)) if len(message_list[x]) == max([len(x) for x in message_list])][0]
        # print(f"{raw_max_length_index =}")

        dc = wx.ClientDC(self.st[raw_max_length_index])
        text_width, text_height = dc.GetTextExtent(self.st[raw_max_length_index].GetLabel())

        screen_size = wx.DisplaySize()
        # print(f"{pos = }")
        # print(f"{screen_size = }")
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
        self.st[0].Bind(wx.EVT_MOTION, self.on_mouse_moved, id=wx.ID_ANY)

    def on_mouse_moved(self, event):
        print("mouse moved")
        self.Close()

    def on_key_pressed(self, event):
        print("Key pressed")
        self.Close()
        # a = wx.TipWindow(self, "This is a tooltip", 500)
        # a.show()

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

        # self.Bind(wx.EVT_LEFT_DOWN, self.on_key_pressed, id=wx.ID_ANY)
        self.Bind(wx.EVT_ICONIZE, self.OnMyEvent, id=10)
        self.Bind(wx.EVT_ICONIZE, self.on_translit, id=20)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

    def on_timer(self, event):
        self.Close_window()

    def Close_window(self):
        if self.wnd:
            self.wnd.Close()

    def OnMyEvent(self, event):
        # if not self.wnd:
        self.new_frame()

    def on_translit(self, event):
        # print(f"on_translit_event called")
        # time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
        keyboard.press_and_release('ctrl+c')
        time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
        # # keyboard.press_and_release('del')
        # time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
        #
        # win32clipboard.OpenClipboard()
        # data = win32clipboard.GetClipboardData()
        # # print(f"{data = }")
        # win32clipboard.CloseClipboard()
        data_from_clipboard = pyperclip.paste()
        #
        letters_rus = "фисвуапршолдьтщзйкыегмцчняФИСDEÀÏРШJËДЬТЩЗЙКЫЕГМЦЧНЯ"
        letters_eng = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        #
        rus = 1
        for i in data_from_clipboard:
            if i in letters_rus:
                rus += 1
            else:
                rus -= 1

        if rus > 0:
            mytable = data_from_clipboard.maketrans(letters_rus, letters_eng)
        else:
            mytable = data_from_clipboard.maketrans(letters_eng, letters_rus)
        # print(f"{mytable = }")
        try:
            translit_data = data_from_clipboard.translate(mytable)
            # print(f"{translit_data = }")
            # print(f"{translit_data.encode('UTF-8') = }")
            # print(f"{translit_data.encode('ANSI') = }")
            # print(f"{translit_data.encode('windows-1251') = }")

            # win32clipboard.OpenClipboard()
            # win32clipboard.EmptyClipboard()
            # win32clipboard.SetClipboardText(translit_data)
            # # data = win32clipboard.GetClipboardData()
            # win32clipboard.CloseClipboard()
            time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
            pyperclip.copy(translit_data)
            time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)

            # win32clipboard.OpenClipboard()
            # print(f"{data = }")
            # win32clipboard.CloseClipboard()

            print(f"{translit_data = }")

            keyboard.press_and_release('ctrl+v')
        except UnicodeEncodeError:
            print(f"UnicodeEncodeError...")
            pass

    def new_frame(self):
        mouse_pos = win32api.GetCursorPos()
        message = self.do_translate()
        self.wnd = PopupWindow(self, mouse_pos, message=message)
        self.wnd.Show()
        self.timer.Start(10000)
        # wx.CallLater(10000, self.Close_window)

    def on_key_pressed(self, event):
        # print("Key pressed")
        self.popup_window.Close()
        self.Close()
        self.task_bar_icon.Destroy()

    def do_translate(self):
        # mouse_pos = win32api.GetCursorPos()
        empty_name = "<<empty>>"
        # pyperclip.copy(empty_name)
        time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
        keyboard.press_and_release('ctrl+c')
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
        data_from_clipboard = pyperclip.paste()
        if data_from_clipboard != empty_name:

            translated_text = db.check_word(data_from_clipboard)
            # print(f"{translated_text = }")
            if not translated_text:
                letters_rus = "фисвуапршолдьтщзйкыегмцчняФИСDEÀÏРШJËДЬТЩЗЙКЫЕГМЦЧНЯ"
                # letters_eng = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                rus = 0
                for i in data_from_clipboard:
                    if i in letters_rus:
                        rus += 1
                    else:
                        rus -= 1
                if '.' in data_from_clipboard:
                    data_from_clipboard = data_from_clipboard.replace('.', '. ')
                if '_' in data_from_clipboard:
                    data_from_clipboard = data_from_clipboard.replace('_', '-')
                if rus > 0:
                    translated_data = make_google_translation(data_from_clipboard, 'en', 'ru')
                else:
                    translated_data = make_google_translation(data_from_clipboard, 'ru', 'en')
                # print(f"{translated_data = }")

                translated_text = translated_data.get('translatedText')
                # translated_text = data_from_clipboard
                db.query_save(data_from_clipboard, translated_text)
                print("new translation")
            else:
                print("used existing word from db")

            pyperclip.copy(translated_text)
            time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
        else:
            translated_text = empty_name
        print(f"{translated_text = }")
        # keyboard.press_and_release('ctrl+v')
        mouse_pos = win32api.GetCursorPos()
        return translated_text


class WorkerThread(threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window
        keyboard.add_hotkey('ctrl+shift+1', self.do_test)
        keyboard.add_hotkey('ctrl+shift+`', self.do_translit)

    def do_test(self):
        # print("Testing")
        evt = wx.IconizeEvent(id=10, iconized=True)
        wx.PostEvent(self.window.GetEventHandler(), evt)

    def do_translit(self):
        # print("Testing translit")
        evt = wx.IconizeEvent(id=20, iconized=True)
        wx.PostEvent(self.window.GetEventHandler(), evt)

    # def run(self):
    #     keyboard.wait('esc')


class App(wx.App):
    def __init__(self, redirect):
        # self.db = db
        super().__init__(redirect=redirect)

    def OnInit(self):
        self.frame = MainWindow(None, "Focus mode")
        # wx.lib.inspection.InspectionTool().Show()  # to inspect all parameters of windows\panels\widgets
        TaskBarIcon(self.frame)
        return True



app = App(redirect=False)
app.MainLoop()

db.disconnect()
print("Exiting app correctly...")
