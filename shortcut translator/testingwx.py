import wx
import wx.adv
import ctypes

TRAY_ICON = 'united-kingdom (1).png'

# Define the callback function for the hook



# app = wx.App()
# wx.MessageBox("Press any key to quit", "wxPython Keyboard Hook Example")



# app.MainLoop()

class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        frame.task_bar_icon = self
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        # self.frame.task_bar_icon = self

    # def CreatePopupMenu(self):
    #     menu = wx.Menu()
    #     create_menu_item(menu, 'Site', self.on_hello)
    #     menu.AppendSeparator()
    #     create_menu_item(menu, 'Exit', self.on_exit)
    #     return menu

    def set_icon(self, path, text=""):
        icon = wx.Icon(path)
        self.SetIcon(icon, text)
        self.ShowBalloon('title', 'text', msec=1000, flags=wx.ICON_ERROR)

    def on_left_down(self, event):
        print('Tray icon was left-clicked.')
        print(f"{self.frame.IsIconized() = }")
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

    def on_hello(self, event):
        print('Clicked on site menu')

    def on_exit(self, event):

        print('Closing from the tray')
        wx.CallAfter(self.Destroy)
        self.frame.Destroy()







class MyEvent(wx.PyEvent):
    def __init__(self, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(wx.NewEventType())
        self.data = data



class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 700),
                          style=wx.RESIZE_BORDER | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.Connect(-1, -1, wx.NewEventType(), self.OnMyEvent)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_key_pressed, id=wx.ID_ANY)

    def on_key_pressed(self, event):
        print("Key pressed")
        self.Close()
        # a = wx.TipWindow(self, "This is a tooltip", 500)
        # a.show()
    def OnMyEvent(self, event):
        # Handle the custom event
        data = event.data
        print("Received data from outside:", data)


class App(wx.App):
    def __init__(self, redirect):
        # self.db = db
        super().__init__(redirect=redirect)

    def OnInit(self):
        self.frame = MainWindow(None, "Focus mode")
        self.frame.Centre()
        # frame.Show(True)
        # wx.lib.inspection.InspectionTool().Show()  # to inspect all parameters of windows\panels\widgets
        self.SetTopWindow(self.frame)
        TaskBarIcon(self.frame)
        return True


def main():
    # db = sql.DataBase(DATABASE_NAME)
    # db.connect()
    # db.create_table_if_not_exists()

    app = App(redirect=False)

    def low_level_keyboard_proc(nCode, wParam, lParam):
        if wParam == 256:  # WM_KEYDOWN
            print("should be event...")
            wx.PostEvent(app.frame, wx.EVT_MOVE)
            key = lParam[0]
            if key == 17:  # Ctrl key
                if ctypes.windll.user32.GetKeyState(16) & 0x8000:  # Shift key
                    print("Ctrl + Shift + Key Pressed:", chr(key))
                elif ctypes.windll.user32.GetKeyState(18) & 0x8000:  # Alt key
                    print("Ctrl + Alt + Key Pressed:", chr(key))
                else:
                    print("Ctrl + Key Pressed:", chr(key))
            elif key == 16:  # Shift key
                if ctypes.windll.user32.GetKeyState(17) & 0x8000:  # Ctrl key
                    print("Ctrl + Shift + Key Pressed:", chr(key))
                elif ctypes.windll.user32.GetKeyState(18) & 0x8000:  # Alt key
                    print("Shift + Alt + Key Pressed:", chr(key))
                else:
                    print("Shift + Key Pressed:", chr(key))
            elif key == 18:  # Alt key
                if ctypes.windll.user32.GetKeyState(16) & 0x8000:  # Shift key
                    print("Shift + Alt + Key Pressed:", chr(key))
                elif ctypes.windll.user32.GetKeyState(17) & 0x8000:  # Ctrl key
                    print("Ctrl + Alt + Key Pressed:", chr(key))
                else:
                    print("Alt + Key Pressed:", chr(key))
            else:
                if ctypes.windll.user32.GetKeyState(16) & 0x8000:  # Shift key
                    print("Shift + Key Pressed:", chr(key))
                elif ctypes.windll.user32.GetKeyState(17) & 0x8000:  # Ctrl key
                    print("Ctrl + Key Pressed:", chr(key))
                elif ctypes.windll.user32.GetKeyState(18) & 0x8000:  # Alt key
                    print("Alt + Key Pressed:", chr(key))
                else:
                    print("Key Pressed:", chr(key))
        return ctypes.windll.user32.CallNextHookEx(0, nCode, wParam, lParam)

    # def low_level_keyboard_proc1(nCode, wParam, lParam):
    #     if wParam == 256:  # WM_KEYDOWN
    #         print("Key Pressed:", chr(lParam[0]))
    #         [print(x) for x in lParam[:2]]
    #     return ctypes.windll.user32.CallNextHookEx(0, nCode, wParam, lParam)

    # Create a C function pointer for the hook procedure
    CMPFUNC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int))
    low_level_keyboard_pointer = CMPFUNC(low_level_keyboard_proc)

    # Create a hook handle and set the hook
    hook_handle = ctypes.windll.user32.SetWindowsHookExA(13, low_level_keyboard_pointer, 0, 0)

    app.MainLoop()

    # Remove the hook when the program is finished
    ctypes.windll.user32.UnhookWindowsHookEx(hook_handle)
    print('Everything closed correctly')


if __name__ == '__main__':
    main()


