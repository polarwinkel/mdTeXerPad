#!/bin/python3
import wx.adv
import wx
import webbrowser
import subprocess
from os import popen
TRAY_TOOLTIP = 'mdTeXerPad' 
TRAY_ICON = 'static/favicon.svg' 


def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Start', self.on_start)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu
    
    def set_icon(self, path):
        icon = wx.Icon(path)
        self.SetIcon(icon, TRAY_TOOLTIP)
    
    def on_start(self, event):
        webbrowser.open('http://localhost:5000')
    
    def on_left_down(self, event):
        print('This is the mdTeXerPad Taskbar server')
    
    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self.frame.Close()

class App(wx.App):
    def OnInit(self):
        frame=wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        return True

def main():
    server = App(False)
    #flask = popen('gunicorn --bind 0.0.0.0:5000 app:app')
    subprocess.Popen(['python3', 'app.py'])
    server.MainLoop()


if __name__ == '__main__':
    main()
