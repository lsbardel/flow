
import wx
from wx.lib.wordwrap import wordwrap


class info(object):
    
    def __init__(self,name="<no-name>",
                 version="",
                 copyright="",
                 description=None,
                 website=None,
                 developers=None,
                 license=None):
        info.Name          = name
        info.Version       = version
        info.Copyright     = copyright
        info.Description   = self.__concatenate(description)
        info.WebSite       = website
        info.Developers    = developers
        info.License       = self.__concatenate(license)
        
    def __concatenate(self,li):
        if li:
            return '\n'.join(li)
        else:
            return ''
    

class AboutBox(object):
    
    def show(self, parent, evt, info):
        # First we create and fill the info object
        infod = wx.AboutDialogInfo()
        infod.Name        = info.Name
        infod.Version     = info.Version
        infod.Copyright   = info.Copyright
        infod.Description = wordwrap(info.Description,350, wx.ClientDC(parent))
        infod.WebSite     = info.WebSite
        infod.Developers  = info.Developers

        infod.License = wordwrap(info.License, 500, wx.ClientDC(parent))

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(infod)
        

