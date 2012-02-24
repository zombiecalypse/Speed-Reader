#!/usr/bin/python

# Filename: reader_window.py
# Author:   Aaron Karper
# Created:  2012-01-07
# Description:
#           
import wx
import re
import os.path
from pykka.actor import ThreadingActor
from pykka.registry import ActorRegistry
from .text_output_actor import *
from multiprocessing import Value as SharedValue

BEGIN = (0,0)
class TextDisplay(wx.Panel):
    "Centered display of text"
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        sizer = wx.GridSizer(1,1,5,5)
        self._coord = wx.StaticText(self, -1, "")
        self._text = wx.StaticText(self, -1, "bla")
        sizer.Add(self._coord, 0, wx.ALL | wx.CENTRE | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(self._text, 0, wx.ALL | wx.CENTRE | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTRE_VERTICAL)
        self.SetSizer(sizer)

    def SetLabel(self, text, c):
        self._text.SetLabel(text)
        #self._coord.SetLabel(str(c))
        self.Layout()

    def set_label(self, text, c):
        wx.CallAfter(self.SetLabel, text, c)

class ConfigPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self._words_per_minute_input = wx.TextCtrl(self)
        self._words_per_chunk_input = wx.TextCtrl(self)
        label_wpm = wx.StaticText(self, label = 'Words per Minute')
        label_wpc = wx.StaticText(self, label = 'Words per Chunk')

        self._words_per_minute_input.SetValue(str(parent.settings['wpm']))
        self._words_per_chunk_input.SetValue(str(parent.settings['wpc']))
        sizer = wx.GridSizer(2,2)
        sizer.Add(label_wpm)
        sizer.Add(self._words_per_minute_input)
        sizer.Add(label_wpc)
        sizer.Add(self._words_per_chunk_input)
        self.SetSizer(sizer)

    def GetValue(self):
        return dict(wpm = self._words_per_minute_input.GetValue(),
                wpc = self._words_per_chunk_input.GetValue())


class ReaderWindow(ThreadingActor):
    def __init__(self, *args, **kwargs):
        ThreadingActor.__init__(self)
        self.frame = wx.Frame(*args, **kwargs)
        self.load_settings()
        self.make_menues()
        self.make_widgets()
        self.make_text_producers()
        self.running = False

    def load_settings(self):
        self.settings = dict( wpm = 400, wpc = 1 )

    def make_text_producers(self):
        self._text_buffer = TextBuffer.start(
                text = "This is a Demo",
                callback = self.as_message.set_text,
                finished = self.as_message.pause).proxy()

    def set_text(self, text, coord):
        self._text_field.set_label(text, coord)

    def make_menues(self):
        menuBar = wx.MenuBar()
        filemenu = wx.Menu()
        open = filemenu.Append(wx.ID_OPEN, "&Open")
        quit = filemenu.Append(wx.ID_EXIT, "E&xit")

        menuBar.Append(filemenu, "&File")

        self.frame.Bind(wx.EVT_MENU, self.OnQuit, quit)
        self.frame.Bind(wx.EVT_MENU, self.OnOpen, open)
        self.frame.SetMenuBar(menuBar)

    def OnOpen(self, evt):
        self.dirname = ''
        diag = wx.FileDialog(self.frame, "Choose file to be read", self.dirname, '', '*.txt', wx.OPEN)
        if diag.ShowModal() == wx.ID_OK:
            self.filepath = diag.GetPath()
            self.dirname = diag.GetDirectory()
            with open(self.filepath) as f:
                self._text_buffer.use_text(f.read())
        diag.Destroy()

    def OnQuit(self, evt):
        self._text_buffer.pause()
        self.Close()

    def make_widgets(self):
        self._text_field = TextDisplay(self.frame)
        self._go_button = wx.Button(self.frame, label = "Go!")
        self._reset_button = wx.Button(self.frame, label = "Reset")
        self._config_panel = ConfigPanel(self, self.frame)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self._text_field, 1, wx.EXPAND, 10)
        sizer.Add(self._config_panel)
        sizer_h.Add(self._go_button)
        sizer_h.Add(self._reset_button)
        sizer.Add(sizer_h)
        self.frame.Bind(wx.EVT_BUTTON, self.OnGoButton, self._go_button)
        self.frame.Bind(wx.EVT_BUTTON, self.OnResetButton, self._reset_button)
        self.frame.SetSizer(sizer)

    def OnResetButton(self, evt):
        self._text_buffer.coord = BEGIN
        self._text_field.set_label("", BEGIN)

    def OnGoButton(self, evt):
        if self.running:
            self.pause()
        else:
            self.go()

    def pause(self):
        self._text_buffer.pause()
        self._go_button.SetLabel("Go!")
        self.running = False

    def go(self):
        config = self._config_panel.GetValue()
        self._text_buffer.set_word_speed(wpm = config['wpm'], wpc = config['wpc'])
        self._text_buffer.go().get()
        self._go_button.SetLabel("Pause")
        self.running = True

    def Show(self, *args, **kwargs):
        return self.frame.Show(*args, **kwargs)

class SpeedRead(wx.App):
    def OnInit(self):
        frame = ReaderWindow.start(None, title = 'Speed Read').proxy()
        return frame.Show().get()
    def OnExit(self):
        ActorRegistry.stop_all()

if __name__ == '__main__':
    app = SpeedRead()
    app.MainLoop()
