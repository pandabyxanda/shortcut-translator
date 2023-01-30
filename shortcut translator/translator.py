import time
import keyboard
import win32api
import wx
# import win32clipboard
import pyperclip
from google_translate import make_google_translation

TIME_SLEEP_BETWEEN_KEYPRESS = 0.2


# def do_test():
#     keyboard.press_and_release('ctrl+c')
#     time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
#
#     win32clipboard.OpenClipboard()
#     # win32clipboard.EmptyClipboard()
#     win32clipboard.SetClipboardText('testing 123')
#     win32clipboard.CloseClipboard()
#     time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
#     keyboard.press_and_release('ctrl+v')


# def do_translit():
#     # # pass
#     # win32clipboard.OpenClipboard()
#     # win32clipboard.EmptyClipboard()
#     # win32clipboard.CloseClipboard()
#     time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
#     keyboard.press_and_release('ctrl+c')
#     time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
#     # # keyboard.press_and_release('del')
#     # time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
#     #
#     win32clipboard.OpenClipboard()
#     data = win32clipboard.GetClipboardData()
#     # print(f"{data = }")
#     win32clipboard.CloseClipboard()
#
#     #
#     letters_rus = "фисвуапршолдьтщзйкыегмцчняФИСDEÀÏРШJËДЬТЩЗЙКЫЕГМЦЧНЯ"
#     letters_eng = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
#     #
#     rus = 1
#     for i in data:
#         if i in letters_rus:
#             rus += 1
#         else:
#             rus -= 1
#
#     if rus > 0:
#         mytable = data.maketrans(letters_rus, letters_eng)
#     else:
#         mytable = data.maketrans(letters_eng, letters_rus)
#     # print(f"{mytable = }")
#     try:
#         translit_data = data.translate(mytable)
#         # print(f"{translit_data = }")
#         # print(f"{translit_data.encode('UTF-8') = }")
#         # print(f"{translit_data.encode('ANSI') = }")
#         # print(f"{translit_data.encode('windows-1251') = }")
#
#         win32clipboard.OpenClipboard()
#         win32clipboard.EmptyClipboard()
#         win32clipboard.SetClipboardText(translit_data)
#         # # data = win32clipboard.GetClipboardData()
#         win32clipboard.CloseClipboard()
#         time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
#
#         win32clipboard.OpenClipboard()
#         data = win32clipboard.GetClipboardData()
#         print(f"{data = }")
#         win32clipboard.CloseClipboard()
#
#         # print(translit_data)
#
#         keyboard.press_and_release('ctrl+v')
#     except UnicodeEncodeError:
#         pass


# def do_translate2():
#     keyboard.press_and_release('ctrl+c')
#     time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
#
#     win32clipboard.OpenClipboard()
#     data = win32clipboard.GetClipboardData()
#     win32clipboard.EmptyClipboard()
#     # win32clipboard.CloseClipboard()
#
#
#
#
#     letters_rus = "фисвуапршолдьтщзйкыегмцчняФИСDEÀÏРШJËДЬТЩЗЙКЫЕГМЦЧНЯ"
#     letters_eng = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
#     rus = 0
#     for i in data:
#         if i in letters_rus:
#             rus += 1
#         else:
#             rus -= 1
#
#     if rus > 0:
#         translated_data = make_google_translation(data, 'en', 'ru')
#         # print("1")
#     else:
#         translated_data = make_google_translation(data, 'ru', 'en')
#         # print("2")
#
#     text = translated_data.get('translatedText')
#     time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
#     # win32clipboard.OpenClipboard()
#     win32clipboard.SetClipboardText(text)
#     win32clipboard.CloseClipboard()
#
#     time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
#     # print(f"{translated_data = }")
#
#
#     print(f"{text = }")
#     keyboard.press_and_release('ctrl+v')


def do_translate():
    mouse_pos = win32api.GetCursorPos()
    # keyboard.press_and_release('ctrl+c')
    # time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
    # data_from_clipboard = pyperclip.paste()
    #
    # letters_rus = "фисвуапршолдьтщзйкыегмцчняФИСDEÀÏРШJËДЬТЩЗЙКЫЕГМЦЧНЯ"
    # # letters_eng = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # rus = 0
    # for i in data_from_clipboard:
    #     if i in letters_rus:
    #         rus += 1
    #     else:
    #         rus -= 1
    #
    # if rus > 0:
    #     translated_data = make_google_translation(data_from_clipboard, 'en', 'ru')
    # else:
    #     translated_data = make_google_translation(data_from_clipboard, 'ru', 'en')
    # # print(f"{translated_data = }")
    #
    # translated_text = translated_data.get('translatedText')
    translated_text = 'Test translated, words, idk....'
    pyperclip.copy(translated_text)
    time.sleep(TIME_SLEEP_BETWEEN_KEYPRESS)
    # print(f"{data_from_clipboard = }")
    # print(f"{translated_text = }")
    # keyboard.press_and_release('ctrl+v')


    class TooltipFrame(wx.Frame):
        def __init__(self, parent, id, title):
            # wx.Frame.__init__(self, parent, id, title)
            size = (200, 50)
            pos = (mouse_pos[0], mouse_pos[1] - size[1] - 20)
            wx.Frame.__init__(self, parent, title=title, size=size, pos=pos,
                              style=wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR)
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
            font.SetPointSize(14)
            # self.opacity = 55
            # self.SetTransparent(self.opacity)
            # self.Centre()
            self.timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
            self.timer.Start(50000)
            # pos = wx.GetMousePosition()
            # self.Show(True)
            # a = wx.TipWindow(self, "This is a tooltip", 500)
            # self.st1 = wx.StaticText(self, label=translated_text, size=size)
            # self.st1.SetFont(font)
            self.Bind(wx.EVT_LEFT_DOWN, self.on_button_click, id=wx.ID_ANY)
            # self.st1.Bind(wx.EVT_LEFT_DOWN, self.on_button_click, id=wx.ID_ANY)
            # self.Bind(wx.KeyEv
            # a = wx.TipWindow(self, "This is a tooltip", 500)
            # a.show()

        def on_key_pressed(self, event):
            print("Key pressed")
            self.Close()
            # a = wx.TipWindow(self, "This is a tooltip", 500)
            # a.show()

        def on_timer(self, event):
            self.Close()
            # self.Destroy()
        # wx.MouseEvent

    app = wx.App()
    frame = TooltipFrame(None, -1, "Tooltip Example")
    frame.Show(True)

    # event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, wx.ID_OK)
    # wx.PostEvent(frame, event)

    app.MainLoop()
    print("main loop of window finished")


# keyboard.add_hotkey('ctrl+1', do_test)
# keyboard.add_hotkey('ctrl+2', do_translit)
keyboard.add_hotkey('ctrl+3', do_translate)

keyboard.wait('esc')


# пиво # water
# Можно немного поработать…You can work a little...1Можно немного поработать...4
# Можно немного поработать. work can. немного поработать
# You can work a little. Вы можете. работать немного

