import wx

# Define a custom event class
class MyEvent(wx.PyEvent):
    def __init__(self, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(wx.NewEventType())
        self.data = data
        print("MyEvent1 ", self.data)

# Define the main window of your application
class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(200, 100))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Connect the custom event to the event handler
        self.Connect(-1, -1, wx.NewEventType(), self.OnMyEvent)

    def OnClose(self, event):
        self.Destroy()

    def OnMyEvent(self, event):
        # Handle the custom event
        data = event.data
        print("Received data from outside:", data)

# Create an instance of the main window and show it
app = wx.App()
frame = MainWindow(None, "My App")
frame.Show()

# Post a custom event from outside the application
wx.PostEvent(frame, MyEvent("Hello from outside!"))

# Start the main event loop
app.MainLoop()