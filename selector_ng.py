# -*- coding: utf-8 -*-
"""
Created on Thu Mar 07 08:31:30 2013

@author: tonin

Selector-ng
"""

from PyQt4 import QtCore, QtGui
from pprint import pprint
import selector_ng_rc
import copy
import sys
import os
from image import CompoundImage

#variables globales de configuracion
VIEW_WEB=False
TEXT_ROTATE=False

SESSIONS_LIMIT = 0 # 0=unlimited
MINIMUN_SESSIONS_LIMIT=3

PLATFORM = {'win32':{'background':'./fondo.png',
                     'config':'conf.network'},
            'linux2':{'background':'/usr/local/uco/selector/fondo.png',
                      'config':'conf.txt'}
            }

BEST_SESSION_SIZE=3
SCALE_SIZE = 0.72

SCALE_TRANSFORMATION_MODE = 1 # 0=Fast 1=Smooth

ZOOM_FACTOR = 1.7
MARGEN_X = 20.0
MARGEN_Y = 100.0

DEFAULT_ICON_SIZE = 256.0
DEFAULT_FONT_SIZE = 25.0
DEFAULT_FONT_WEIGHT = 100.0
MINIMUN_FONT_SIZE = 10.0

COPYRIGHT_MESSAGE = u'©Tonin 2013'


class MyWindow(QtGui.QGraphicsView):
    def __init__(self,scene,app):
        super(MyWindow,self).__init__(scene)
        self.app = app
        self.setFrameStyle(0)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
    def show(self):
        self.showFullScreen()
        #self.setFocus(0)
        #self.raise_()        
        #self.activateWindow()
        print "Tengo el foco? ",self.hasFocus()
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            sys.exit(app.exec_())
        if e.key() == QtCore.Qt.Key_Plus:
            ZOOM_FACTOR = ZOOM_FACTOR + 0.2
#    def changeEvent(self, e):
        #print "Change event ",e.type()
        
class Pixmap(QtGui.QGraphicsWidget):
    clicked = QtCore.pyqtSignal()
    enter = QtCore.pyqtSignal()
    leave = QtCore.pyqtSignal()

    def __init__(self, pix, parent,sep_x,teclasSelector):
        super(Pixmap, self).__init__(None)
        self.setAcceptHoverEvents(True)

        self.orig = QtGui.QPixmap(pix)
        self.p = QtGui.QPixmap(pix)
        self.vt = parent.vt
        self.teclasSelector = teclasSelector
        #Escalo el Pixmap
        if parent.numeroSesiones < MINIMUN_SESSIONS_LIMIT:
            numeroSesiones = MINIMUN_SESSIONS_LIMIT
        else:
            numeroSesiones = parent.numeroSesiones
            
        if numeroSesiones <= BEST_SESSION_SIZE:
            s = SCALE_SIZE
        else:
            s = 1
            
        scale = (DEFAULT_ICON_SIZE * BEST_SESSION_SIZE * s) \
                /numeroSesiones 
        self.orig = self.orig.scaledToHeight(scale,SCALE_TRANSFORMATION_MODE)

        #Geometria del pixmap
        ICON_SIZE = self.orig.width()
        xCENTER = sep_x*float(parent.indice) + sep_x/2 + MARGEN_X
        xPOS = xCENTER - ICON_SIZE/2
        yPOS = MARGEN_Y
        self.setGeometry(QtCore.QRectF(xPOS ,
                                       yPOS , 
                                       ICON_SIZE ,
                                       ICON_SIZE))

        #Etiqueta
        fontSize = 5+(DEFAULT_FONT_SIZE * ICON_SIZE/DEFAULT_ICON_SIZE) 
        if fontSize < MINIMUN_FONT_SIZE: 
            fontSize = MINIMUN_FONT_SIZE
        #print fontSize,ICON_SIZE
        font = QtGui.QFont("calibri",fontSize,100) #family,size,weight
        self.label =  QtGui.QGraphicsTextItem()
        self.label.setPlainText(parent.title.title().replace('"',''))
        self.label.setFont(font) 
        Rect = self.label.boundingRect()
        self.label.setPos(xCENTER - Rect.width()/2,yPOS + ICON_SIZE)

        #Ahora creo la imagen de las teclas
        screen = QtGui.QDesktopWidget().screenGeometry()
        self.teclas = CompoundImage("F" + str(self.vt),"Haga click o pulse ", \
                                    u"para ir a esta sesión",screen)
        self.teclas.pixmap.setVisible(False)
        
    def paint(self, painter, option, widget):
        painter.drawPixmap(QtCore.QPointF(), self.p)

    def mousePressEvent(self, ev):
        self.teclas.pixmap.setVisible(False)
        self.teclasSelector.pixmap.setVisible(True)
        self.clicked.emit()
        os.system("chvt "+str(self.vt))
        
    def hoverEnterEvent(self,ev):
        self.teclas.pixmap.setVisible(True)
        self.teclasSelector.pixmap.setVisible(False)
        self.enter.emit()
        
    def hoverLeaveEvent(self,ev):
        self.teclas.pixmap.setVisible(False)
        self.teclasSelector.pixmap.setVisible(True)
        self.leave.emit()
        
    def setGeometry(self, rect):
        super(Pixmap, self).setGeometry(rect)

        if rect.size().width() > self.orig.size().width():
            self.p = self.orig.scaled(rect.size().toSize())
        else:
            self.p = QtGui.QPixmap(self.orig)

def scaleQRectF(qr_orig,zoom_factor):
        """Devuelve un RectF escalado del argumento en un factor dado"""
        
        #Si no hago una copia del objeto machaco el original
        qr_dest = copy.copy(qr_orig)
        
        desp = ((zoom_factor-1) * qr_dest.width())/2
        #print "Desplazamiento = " , desp
        qr_dest.setX(qr_dest.x() - desp)
        qr_dest.setY(qr_dest.y() - desp)
        qr_dest.setWidth(qr_orig.width() + 2*desp)
        qr_dest.setHeight(qr_orig.height() + 2*desp)
        return qr_dest

def createStates(objects , parent):
    for obj in objects:
        #Guardo el Rect original y alculo el nuevo Rect para el zoom
        origRect = obj.geometry()
        zoomRect = scaleQRectF(origRect,ZOOM_FACTOR)
        #Lo mismo para el label
        origY = obj.label.y()
        zoomY = obj.label.y() - zoomRect.y() + origRect.y()

        #Estado zoom
        state_zoom = QtCore.QState(parent)
        state_zoom.assignProperty(obj, 'geometry', zoomRect)
        state_zoom.assignProperty(obj.label, 'y' , zoomY)
        if TEXT_ROTATE:
            state_zoom.assignProperty(obj.label, 'rotation' , 360)
        parent.addTransition(obj.enter, state_zoom)

        #Estado nozoom        
        state_nozoom = QtCore.QState(parent)
        state_nozoom.assignProperty(obj, 'geometry', origRect)
        state_nozoom.assignProperty(obj.label, 'y' , origY)
        if TEXT_ROTATE:
            state_nozoom.assignProperty(obj.label, 'rotation' , 0)
        parent.addTransition(obj.leave, state_nozoom)
        
        #Estado click
        state_clicked = QtCore.QState(parent)
        state_clicked.assignProperty(obj, 'geometry', origRect)
        state_clicked.assignProperty(obj.label, 'y' , origY)
        if TEXT_ROTATE:
            state_clicked.assignProperty(obj.label, 'rotation' , 0)
        parent.addTransition(obj.clicked, state_clicked)

def createAnimations(objects, machine):
    for obj in objects:
        animationGroup = QtCore.QParallelAnimationGroup(obj)
        animationPixmap = QtCore.QPropertyAnimation(obj, 'geometry',obj)
        animationLabel = QtCore.QPropertyAnimation(obj.label, 'y',obj)
        animationGroup.addAnimation(animationPixmap)
        animationGroup.addAnimation(animationLabel)

        if TEXT_ROTATE:
            animationRotate = QtCore.QPropertyAnimation(obj.label, 'rotation',obj)
            animationGroup.addAnimation(animationRotate)
        
        machine.addDefaultAnimation(animationGroup)

#Aqui comienza la aplicacion en si
if __name__ == '__main__':

    from config_parser import  session
    from config_parser import  config
    from web import Browser

    app = QtGui.QApplication(sys.argv)
    QtCore.pyqtRemoveInputHook()
    #Inicializo la escena
    screen = QtGui.QDesktopWidget().screenGeometry()
    scene = QtGui.QGraphicsScene(float(screen.x()),float(screen.y()), 
                                 float(screen.width()),float(screen.height()))

    Background = PLATFORM.get(sys.platform).get('background')
    Config     = PLATFORM.get(sys.platform).get('config')
        
    app.setStyleSheet("QWidget {border-image: url("+Background+") }")
      
    #Leo el fichero de configuración y relleno los objetos de sesiones
    #esto ultimo ya genera los objetos Pixmap
    cf = config(Config)

    #Calculo la geometria y relleno mi lista de objetos sesion
    sep_x = (screen.width() - 2*MARGEN_X) / cf.numeroSesiones
    
    teclasSelector = CompoundImage("F6","Pulse ","para volver al selector",screen)
    teclasSelector.pixmap.setVisible(True)
    scene.addItem(teclasSelector.pixmap)

    cf.rellenaSesiones(sep_x,teclasSelector)
    
    #Añado los Pixmaps a la escena, pongo su geometría y
    #creo la lista de objetos para la animación
    objects = []
    for s in cf.sesiones:
        scene.addItem(s.pixmap)
        scene.addItem(s.pixmap.label)
        scene.addItem(s.pixmap.teclas.pixmap)
        objects.append(s.pixmap)

    if VIEW_WEB:    
        browser = Browser()
        scene.addItem(browser)  
    
    #copy_right = QtGui.QLabel(COPYRIGHT_MESSAGE)
    text = scene.addText(unicode(COPYRIGHT_MESSAGE),QtGui.QFont("calibri",10))
    text.setOpacity(0.5)
    text.setPos(QtCore.QPointF(screen.bottomRight()- QtCore.QPoint(100,30)))
    
    #Creo la ventana principal y los estados
    window = MyWindow(scene,app)

    #Lo que viene a continuación es para la animación
    machine = QtCore.QStateMachine()
    machine.setGlobalRestorePolicy(QtCore.QStateMachine.RestoreProperties)

    group = QtCore.QState(machine)

    idleState = QtCore.QState(group)
    group.setInitialState(idleState)
    
    createStates(objects , group)
    createAnimations(objects, machine)

    machine.setInitialState(group)
    machine.start()

    #PRUEBAS
    #raw_input("Pulse una tecla para empezar ...")
    
    #Muestro la ventana maximizada
    window.show()
    

    sys.exit(app.exec_())

