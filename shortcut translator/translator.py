import win32api
import wx
import wx.adv
# import ctypes
import time
import pyperclip
import keyboard
# import multiprocessing
import threading
# import msvcrt
from google_translate import make_google_translation

TRAY_ICON = 'united-kingdom (1).png'
TIME_SLEEP_BETWEEN_KEYPRESS = 0.2


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
        # self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
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
        self.ShowBalloon('title', 'text', msec=1000, flags=wx.ICON_ERROR)

    def on_left_down(self, event):
        print('Tray icon was left-clicked.')
        # print(f"{self.frame.IsIconized() = }")

        self.frame.Close()
        self.Destroy()
        #
        # if self.frame.IsIconized():
        #     self.set_icon(TRAY_ICON)
        #     self.frame.Show()
        #     self.frame.Iconize(iconize=False)
        #
        # else:
        #     self.frame.Hide()
        #     self.frame.Iconize(iconize=True)
        #     self.set_icon(TRAY_ICON2)

    # def on_hello(self, event):
    #     print('Clicked on site menu')

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
        # wx.Frame.__init__(self, parent, id, title)
        size = (300, 50)
        pos = (mouse_pos[0], mouse_pos[1] - size[1] - 20)
        wx.Frame.__init__(self, parent, title="title1", size=size, pos=pos,
                          style=wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR)
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(12)
        # self.opacity = 55
        # self.SetTransparent(self.opacity)
        # self.Centre()
        self.st1 = wx.StaticText(self, label=message, size=size)
        self.st1.SetFont(font)
        dc = wx.ClientDC(self.st1)
        text_width, text_height = dc.GetTextExtent(self.st1.GetLabel())
        # print(text_width, text_height)
        self.SetSize((text_width + 5, text_height + 5))
        pos = (mouse_pos[0], mouse_pos[1] - text_height - 20)
        self.SetPosition(pos)
        self.st1.Bind(wx.EVT_LEFT_DOWN, self.on_key_pressed, id=wx.ID_ANY)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_key_pressed, id=wx.ID_ANY)

    def on_key_pressed(self, event):
        # print("Key pressed")
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
        self.Bind(wx.EVT_LEFT_DOWN, self.on_key_pressed, id=wx.ID_ANY)
        self.wnd = None
        # worker = WorkerThread(self)
        # worker.start()
        self.Bind(wx.EVT_ICONIZE, self.OnMyEvent)

        self.worker = WorkerThread(self)
        self.worker.start()

        self.timer = wx.Timer(self)
        self.timer.Start(5000)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

    def on_timer(self, event):
        # print("new worker")
        print(f"{self.worker = }, {self.worker.is_alive() = }")

        # if not self.worker:

    def Close_window(self):
        if self.wnd:
            self.wnd.Close()

    def OnMyEvent(self, event):
        print(f"my event called")
        # if not self.wnd:
        self.new_frame()

    def new_frame(self):
        mouse_pos = win32api.GetCursorPos()
        message = self.do_translate()
        self.wnd = PopupWindow(self, mouse_pos, message=message)
        self.wnd.Show()
        wx.CallLater(3000, self.Close_window)

    def on_key_pressed(self, event):
        # print("Key pressed")
        self.popup_window.Close()
        self.Close()
        self.task_bar_icon.Destroy()
        # self.Destroy()
        # a = wx.TipWindow(self, "This is a tooltip", 500)
        # a.show()

    def do_translate(self):
        # mouse_pos = win32api.GetCursorPos()
        pyperclip.copy("<<empty>>")
        time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
        keyboard.press_and_release('ctrl+c')
        time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
        data_from_clipboard = pyperclip.paste()

        # letters_rus = "фисвуапршолдьтщзйкыегмцчняФИСDEÀÏРШJËДЬТЩЗЙКЫЕГМЦЧНЯ"
        # # letters_eng = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        # rus = 0
        # for i in data_from_clipboard:
        #     if i in letters_rus:
        #         rus += 1
        #     else:
        #         rus -= 1
        # if '.' in data_from_clipboard:
        #     data_from_clipboard = data_from_clipboard.replace('.', '. ')
        # if '_' in data_from_clipboard:
        #     data_from_clipboard = data_from_clipboard.replace('_', '-')
        # if rus > 0:
        #     translated_data = make_google_translation(data_from_clipboard, 'en', 'ru')
        # else:
        #     translated_data = make_google_translation(data_from_clipboard, 'ru', 'en')
        # # print(f"{translated_data = }")
        #
        # translated_text = translated_data.get('translatedText')
        translated_text = data_from_clipboard
        pyperclip.copy(translated_text)
        time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
        # print(f"{data_from_clipboard = }")11
        print(f"{translated_text = }")
        # keyboard.press_and_release('ctrl+v')
        mouse_pos = win32api.GetCursorPos()
        return translated_text


class WorkerThread(threading.Thread):
    def __init__(self, window):
        threading.Thread.__init__(self)
        self.window = window
        keyboard.add_hotkey('ctrl+3', self.do_test)

    def do_test(self):
        print("Testing")
        evt = wx.IconizeEvent(id=0, iconized=True)
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


#
app = App(redirect=False)

app.MainLoop()
