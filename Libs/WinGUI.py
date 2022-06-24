from win32gui import GetWindowText, GetForegroundWindow, GetCurrentObject
import time
import win32gui

while True:
    print (win32gui.GetDlgItemText(GetForegroundWindow()))
    time.sleep(0.01)