#!/usr/bin/env python
import wx
import wx.lib.scrolledpanel as scrolled
import random
import os
import pathlib
import PIL
from PIL import ImageGrab
import time

from affsmaker import generate_affs
from audio import create_audio
from visual import create_visual

from auto_update import get_version_info, update

update_period = 3600

class TabPanel(wx.Panel):
    def __init__(self, parent, name):
        super().__init__(parent=parent)
        self.name = name
        
        colors = ["red", "blue", "gray", "yellow", "green"]
        self.SetBackgroundColour(random.choice(colors))
        
class AffMakerPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.name = "Affsmaker"
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        aff_label = wx.StaticText(self, label="Topic:")
        sizer.Add(aff_label, 0, wx.ALL|wx.EXPAND, 3)
        
        self.topic_input = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self.topic_inputted, self.topic_input)
        sizer.Add(self.topic_input, 0, wx.ALL|wx.EXPAND, 10)
        
        self.affs = wx.StaticText(self, label="")
        sizer.Add(self.affs, 1, wx.ALL|wx.EXPAND, 10)
        
        self.SetSizer(sizer)
        
    def topic_inputted(self, event):
        self.affs.SetLabel("Generating affirmations...")
        
        affs = generate_affs((str(self.topic_input.GetValue())))
        
        affs = "".join(affs).replace("|", "\n")
        
        self.affs.SetLabel(affs)
        
class AudioSubMakerPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.name = "Audio submaker"
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        aff_label = wx.StaticText(self, label="Affs:")
        sizer.Add(aff_label, 0, wx.ALL|wx.EXPAND, 3)
        
        self.aff_input = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        sizer.Add(self.aff_input, 0, wx.ALL|wx.EXPAND, 10)
        
        file_name_label = wx.StaticText(self, label="Filename:")
        sizer.Add(file_name_label, 0, wx.ALL|wx.EXPAND, 3)
        
        self.file_name_input = wx.TextCtrl(self)
        sizer.Add(self.file_name_input, 0, wx.ALL|wx.EXPAND, 10)
        
        backgrond_label = wx.StaticText(self, label="Background Audio:")
        sizer.Add(backgrond_label, 0, wx.ALL|wx.EXPAND, 3)
        
        self.backgrounds = ["Silence"] + os.listdir('Background')
        
        self.background_input = wx.Choice(self, choices=self.backgrounds)
        self.background_input.SetSelection(0)
        self.background = "Silence"
        sizer.Add(self.background_input, 0, wx.ALL|wx.EXPAND, 10)
        
        self.submit_button = wx.Button(self, label="Generate")
        self.Bind(wx.EVT_BUTTON, self.generate, self.submit_button)
        sizer.Add(self.submit_button, 0, wx.ALL|wx.EXPAND, 10)
        
        self.generating_msg = wx.StaticText(self, label="")
        sizer.Add(self.generating_msg, 0, wx.ALL|wx.EXPAND, 10)
    
        self.SetSizer(sizer)
    
    def generate(self, event):
        self.generating_msg.SetLabel("Generating...")
        
        create_audio(self.aff_input.GetValue(), self.file_name_input.GetValue(), self.background_input.GetSelection(), self.backgrounds[self.background_input.GetSelection()])
        
        path_to_sub = pathlib.Path() / "Subs" / (self.file_name_input.GetValue() + ".wav")
        
        self.generating_msg.SetLabel("Generated! Check " + str(path_to_sub.resolve()))
        
class VisualSubMakerPanel(scrolled.ScrolledPanel):
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.name = "Image Submaker"
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        aff_label = wx.StaticText(self, label="Affs:")
        sizer.Add(aff_label, 0, wx.ALL|wx.EXPAND, 3)
        
        self.aff_input = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        sizer.Add(self.aff_input, 0, wx.UP|wx.DOWN|wx.EXPAND, 10)
        
        self.from_clipboard_input = wx.CheckBox(self, label="From Clipboard?")
        self.Bind(wx.EVT_CHECKBOX, self.checkbox_change, self.from_clipboard_input)
        sizer.Add(self.from_clipboard_input, 0, wx.ALL|wx.EXPAND, 10)
        
        self.filename = "copy"
        
        self.image_location = wx.Button(self, label="Get File")
        self.Bind(wx.EVT_BUTTON, self.onOpenFile, self.image_location)
        sizer.Add(self.image_location, 0, wx.UP|wx.DOWN|wx.EXPAND, 10)
        
        self.error_text = wx.StaticText(self, label="")
        self.error_text.Hide()
        sizer.Add(self.error_text, 0, wx.UP|wx.DOWN|wx.EXPAND, 10)
        
        self.image = wx.StaticBitmap(self)
        sizer.Add(self.image, 0, wx.UP|wx.DOWN|wx.EXPAND, 10)
        
        self.submit_button = wx.Button(self, label="Generate")
        self.Bind(wx.EVT_BUTTON, self.generate, self.submit_button)
        sizer.Add(self.submit_button, 0, wx.UP|wx.DOWN|wx.EXPAND, 10)
        
        self.result = wx.StaticBitmap(self)
        sizer.Add(self.result, 0, wx.UP|wx.DOWN|wx.EXPAND, 10)
        
        self.SetSizer(sizer)
        self.SetupScrolling(scroll_x=False)
        self.SetScrollRate(0, 1)
        
    def checkbox_change(self, event):
        self.error_text.SetLabel("")
        self.error_text.Hide()
        
        if not self.from_clipboard_input.GetValue():
            self.image_location.Show()
            self.image.SetBitmap(wx.Bitmap())
            self.GetSizer().Layout()
        else:
            self.image_location.Hide()
            self.filename = "copy"
            
            image = ImageGrab.grabclipboard()
            
            if not image is None:
                aspect_ratio = image.height / image.width
                window_width = self.GetSize()[0]
                image = image.resize((int(window_width), int(window_width * aspect_ratio)))
                
                bitmap = self.static_bitmap_from_pil_image(image)
                self.image.SetBitmap(bitmap)
                self.GetSizer().Layout()
                self.SetupScrolling(scroll_x=False)
            else:
                self.error_text.SetLabel("No image in clipboard.")
                self.error_text.Show()
                self.GetSizer().Layout()
            
    def onOpenFile(self, event):
        """
        Create and show the Open FileDialog
        """
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=str(pathlib.Path().resolve), 
            defaultFile="",
            wildcard="Pictures (*.jpeg,*.png,*.jpg)|*.jpeg;*.png;*.jpg",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            self.filename = paths[0]
        dlg.Destroy()
        
        image = PIL.Image.open(self.filename)
        
        aspect_ratio = image.height / image.width
        window_width = self.GetSize()[0]
        image = image.resize((int(window_width), int(window_width * aspect_ratio)))
        
        bitmap = self.static_bitmap_from_pil_image(image)
        self.image.SetBitmap(bitmap)
        self.GetSizer().Layout()
        self.SetupScrolling(scroll_x=False)
        
    def generate(self, event):
        image = create_visual(self.filename, self.aff_input.GetValue().split(". "))
        
        aspect_ratio = image.height / image.width
        window_width = self.GetSize()[0]
        image = image.resize((int(window_width), int(window_width * aspect_ratio)))
        
        bitmap = self.static_bitmap_from_pil_image(image)
        self.result.SetBitmap(bitmap)
        self.GetSizer().Layout()
        self.SetupScrolling(scroll_x=False)
        
    def static_bitmap_from_pil_image(self, pil_image):
        wx_image = wx.Image(pil_image.size[0], pil_image.size[1])
        wx_image.SetData(pil_image.convert("RGB").tobytes())

        bitmap = wx.Bitmap(wx_image)
        return bitmap

class Window(wx.Frame):
    
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(500, 800))
        
        panel = wx.Panel(self)
        
        self.notebook = wx.Notebook(panel)
        
        self.notebook.AddPage(AffMakerPanel(self.notebook), "Affsmaker")
        self.notebook.AddPage(AudioSubMakerPanel(self.notebook), "Audio Submaker")
        self.notebook.AddPage(VisualSubMakerPanel(self.notebook), "Image Submaker")
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.Layout()
        
        self.CreateStatusBar()
        
        filemenu = wx.Menu()
        
        menu_item = filemenu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.Bind(wx.EVT_MENU, self.OnAbout, menu_item)
        
        filemenu.AppendSeparator()
        menu_item = filemenu.Append(wx.ID_EXIT, "E&xit", " Terminate program")
        self.Bind(wx.EVT_MENU, self.OnExit, menu_item)
        
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        self.SetMenuBar(menuBar)
        self.Show(True)
        
        if time.time() - float(get_version_info()[2]) > update_period:
            should_update = self.ask_for_update()
            
            if should_update:
                dlg = wx.MessageDialog(self, "Restart after the update", "Submaker", wx.OK).ShowModal()
                if dlg == wx.ID_OK:
                    update()
            
        
    def on_tab_change(self, event):
        current_page = self.notebook.GetPage(event.GetSelection())
        
        event.Skip()
        
    def ask_for_update(self):
        dlg = wx.MessageDialog(self, "Submaker needs an update", "Submaker", wx.YES_NO)
        dlg.SetYesNoLabels("Update", "Remind me later")
        if dlg.ShowModal() == wx.ID_YES:
            return True
        else:
            return False
        
    def OnAbout(self, e):
        dlg = wx.MessageDialog(self, "This app is made by Illy", "About submaker", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnExit(self, e):
        self.Close(True)
        
app = wx.App(False)
frame = Window(None, "Submaker")
app.MainLoop()