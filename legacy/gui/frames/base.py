

import wx
import logging

__all__ = ['Frame','TaskBarIcon','TaskBarFrame']



class QmApps(object):
    '''
    This class contains a list of QmApp objects
    '''
    global_app = None
    
    def __init__(self,  installSignals = True):
        self.global_app = self
        self.__threads = []
        if installSignals:
            self.installSignals()
            
    def installSignals(self):
        import signal
        signal.signal(signal.SIGINT, self.killThreads)
        signal.signal(signal.SIGBREAK, self.killThreads)
        
    def addThread(self,t):
        if t not in self.__threads:
            self.__threads.append(t)
        
    def startThreads(self):
        for t in self.__threads:
            t.start()
    
    def killThreads(self):
        for t in self.__threads:
            t.kill()



class Frame(wx.Frame):
    ID_MAINPANEL = wx.NewId()
 
    def __init__(self, 
                 parent=None,
                 id=wx.ID_ANY,
                 title='TaskBarIcon',
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE,
                 icon=None,
                 info=None):
  
        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        if icon:
            self.SetIcon(wx.Icon(icon, wx.BITMAP_TYPE_ICO))
  
        self.mainPanel = wx.Panel(self, self.ID_MAINPANEL)
        
        #self.applications = QmApps()
        self.applications = []
        
        self.infoxxx  = info
        
        # Menu Bar
        self.add_menuBar()
  
  
    def OnHide(self, event):
        self.Hide()
  
  
    def OnIconfiy(self, event):
        #wx.MessageBox('Frame has been iconized!', 'Prompt')
        event.Skip()
 
 
    def OnClose(self, event):
        self.ShutDown()
        
    def onExit(self, event):
        self.ShutDown(event)
        
    def add_menuBar(self):
        '''
        Add the menu bar to the main Frame
        '''
        #
        filemenu = wx.Menu()
        #filemenu.AppendSeparator()
        idm = wx.NewId()
        filemenu.Append(idm,"E&xit","Terminate the program")
        wx.EVT_MENU(self, idm, self.onExit)
        #
        toolmenu = wx.Menu()
        idm = wx.NewId()
        toolmenu.Append(idm,"Python &Shell","Run PyCrust python shell")
        wx.EVT_MENU(self, idm, self.onPythonShell)
        #
        helpmenu = wx.Menu()
        idm = wx.NewId()
        helpmenu.Append(idm,"&About","Information about this program")
        wx.EVT_MENU(self, idm, self.onAbout)
        #
        menubar = wx.MenuBar()
        menubar.Append(filemenu,"&File")
        menubar.Append(toolmenu,"&Tools")
        menubar.Append(helpmenu,"&Help")
        #
        self.SetMenuBar(menubar)
    
    def onAbout(self, event):
        if self.infoxxx:
            from qmpy.python.about import AboutBox
            a = AboutBox()
            a.show(self,event,self.infoxxx)
    
    def onPythonShell(self, event):
        if self.__shell:
            # if it already exists then just make sure it's visible
            s = self.__shell
            if s.IsIconized():
                s.Iconize(False)
            s.Raise()
        else:
            # Make a PyShell window
            from wx import py
            namespace = { 'wx'    : wx,
                          'app'   : wx.GetApp(),
                          'frame' : self,
                          }
            self.__shell = wx.py.shell.ShellFrame(None, locals=namespace)
            self.__shell.SetSize((640,480))
            self.__shell.Show()
            # Hook the close event of the main frame window so that we
            # close the shell at the same time if it still exists            
            def CloseShell(evt):
                if self.__shell:
                    self.__shell.Close()
                evt.Skip()
            self.Bind(wx.EVT_CLOSE, CloseShell)
        
    def ShutDown(self, args=None):
        '''
        Function called when closing application
        '''
        self.Destroy()
        for apps in self.applications:
            apps.kill()
    

class TaskBarIcon(wx.TaskBarIcon):
    ID_CLOSE = wx.NewId()
 
    def __init__(self,
                 frame,
                 displayname,
                 icon):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        if icon:
            self.SetIcon(wx.Icon(name=icon, type=wx.BITMAP_TYPE_ICO), displayname)
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick)
        #self.Bind(wx.EVT_TASKBAR_LEFT_CLICK, self.OnTaskBarLeftClick)
        self.Bind(wx.EVT_MENU, self.OnExit, id=self.ID_CLOSE)
  
    def __repr__(self):
        return 'TaskBarIcon Handler'
    
    def __str__(self):
        return self.__repr__()
    
    def OnTaskBarLeftDClick(self, event):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()
  
    def OnExit(self, event):
        self.frame.ShutDown()
    
    # override
    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(self.ID_CLOSE, 'Exit')
        return menu


class TaskBarFrame(Frame):
    
    def __init__(self, 
                 parent=None,
                 id=wx.ID_ANY,
                 title='TaskBarIcon',
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE,
                 icon=None,
                 info=None):
  
        Frame.__init__(self, parent, id, title, pos, size, style, icon, info)
    
        #button  = wx.Button(panel, wx.ID_ANY, 'Hide Frame', pos=(60, 60))
        #self.Bind(wx.EVT_BUTTON, self.OnHide, button)
        # button = wx.Button(panel, wx.ID_ANY, 'Close', pos=(60, 100))
        # self.Bind(wx.EVT_BUTTON, self.OnClose, button)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
  
  
        #self.Bind(wx.EVT_ICONIZE, self.OnIconfiy) # What is the meaning?
  
        self.taskBarIcon = TaskBarIcon(self,displayname=title,icon=icon)
    
        #sizer = wx.BoxSizer()
        #sizer.Add(button, 0)
        #panel.SetSizer(sizer)
        
    def OnHide(self, event):
        self.Hide()
  
    def OnIconfiy(self, event):
        #wx.MessageBox('Frame has been iconized!', 'Prompt')
        event.Skip()
 
    def OnClose(self, event):
        self.Hide()
        
    def ShutDown(self, args=None):
        self.taskBarIcon.Destroy()
        Frame.ShutDown(self, args)
        

        



