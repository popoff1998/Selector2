# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 19:52:09 2013

@author: Tonin
"""

import sys
from qt_compat import QtCore, QtGui, QtWebKit

if QtWebKit is not None and hasattr(QtWebKit, 'QGraphicsWebView'):
    _BrowserBase = QtWebKit.QGraphicsWebView
else:
    _BrowserBase = QtGui.QGraphicsWidget


class Browser(_BrowserBase):

    def __init__(self):
        super(Browser,self).__init__(None)
        if QtWebKit is not None and hasattr(self, 'load'):
            self.load(QtCore.QUrl("http://www.uco.es"))
            self.setGeometry(QtCore.QRectF(400,400,1024,600))
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
            #self.setOpacity(0.8)
            self.show()
        
        
        

