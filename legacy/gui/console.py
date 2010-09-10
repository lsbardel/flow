from twisted.internet import wxreactor
wxreactor.install()

import wx, wx.py
from about import info
from django.conf import settings

__all__ = ['start']


logformat   = "%(levelname)-10s %(asctime)s   %(message)s"

def Frame(infob):
    import consol

    frame = consol.Frame(None,
                        -1,
                         infob.Name,
                         size=(800, 600),
                         style=wx.DEFAULT_FRAME_STYLE,
                         logformat = logformat,
                         info      = infob)
    panel = frame.app_panel
    sizer = panel.Sizer
    
    intro = 'Welcome To Prospero python shell (PyShell version %s) ' % wx.py.version.VERSION
    win = wx.py.shell.Shell(frame.app_panel,
                            wx.NewId(),
                            size = (-1,-1),
                            introText=intro)
    frame.application = win
    sizer.Add(win, 1, wx.EXPAND, 0)
    return frame


def start():
    from twisted.internet import reactor
    
    infob = info(name        = "Shell",
                 version     = '0.1',
                 description = [".........",
                                "........."],
                 website     = ("bla.com", "home page"),
                 developers  = ["Luca Sbardella"],
                 license     = [".."])
    
    app   = wx.PySimpleApp()
    reactor.registerWxApp(app)
    frame = Frame(infob)
    app.SetTopWindow(frame)

    frame.Centre()
    frame.Show()
    
    reactor.run()
    
