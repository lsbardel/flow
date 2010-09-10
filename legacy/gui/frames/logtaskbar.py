
from base import *
import wx
import logging

__all__ = ['LogTaskBarFrame','WxLog']


class WxLog(logging.Handler):
    '''
    Class used to redirect the logging output into a wx control
    '''
    def __init__(self, ctrl):
        logging.Handler.__init__(self)
        self.ctrl = ctrl
        
    def emit(self, record):
        self.ctrl.AppendText(self.format(record)+"\n")



class LogTaskBarFrame(TaskBarFrame):
    ID_LOG = wx.NewId()
    
    def __init__(self, 
                 parent = None,
                 id     = wx.ID_ANY,
                 title  = 'TaskBarIcon',
                 pos    = wx.DefaultPosition,
                 size   = wx.DefaultSize,
                 style  = wx.DEFAULT_FRAME_STYLE,
                 icon   = None,
                 logformat = None):
        TaskBarFrame.__init__(self, parent, id, title, pos, size, style, icon)
        box = wx.BoxSizer(wx.VERTICAL)
        win = self.mainPanel
        #self.log = editor.Editor(win, -1, style=wx.SUNKEN_BORDER)
        self.log = wx.TextCtrl(win,
                               self.ID_LOG,
                               size = (1000,1000),
                               style = wx.EXPAND|wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        box.Add(self.log, 1, wx.ALL|wx.GROW, 1)
        win.SetSizer(box)
        win.SetAutoLayout(True)
        hdlr = WxLog(self.log)
        
        rootLogger = logging.getLogger('')
        rootLogger.setLevel(logging.DEBUG)
        
        if logformat:
            format   = logging.Formatter(logformat)
            hdlr.setFormatter(format)
            
        rootLogger.addHandler(hdlr)
        
        self.apploop = None