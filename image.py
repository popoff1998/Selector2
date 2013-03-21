# -*- coding: utf-8 -*-

PIXEL_SPACING = 10 #separacion en pixeles
SCALED_WIDTH = 70 #ancho de los iconos escalados
FONT_SIZE = 22

from PyQt4 import QtCore, QtGui
import sys
from PyQt4.QtCore import qVersion, PYQT_VERSION_STR

def versionInfo():
    """Returns a tuple containing some (...) version strings
    @return: tuple(
        ('Platform', platform),
        ('Python Version', version),
        ('Qt Version', version),
        ('PyQt Version', version),
        )
    """

    return (
        ('Platform', sys.platform),
        ('Python Version', sys.version.split()[0]),
        ('Qt Version', qVersion()),
        ('PyQt Version', PYQT_VERSION_STR),
        )


class CompoundImage(QtGui.QGraphicsWidget):
    """
    Esta clase almacena la imagen compuesta de Ctrl + Alt + la tecla de función
    junto a los textos correspondientes
    """

    def __init__(self,key,preStr,postStr,screen):
        from selector_ng import PLATFORM

        
        super(CompoundImage, self).__init__(None)
        self.pixmap = QtGui.QGraphicsPixmapItem()
        painter = QtGui.QPainter()

        IMAGE_PREFIX = PLATFORM.get(sys.platform).get('key_prefix')
        font = QtGui.QFont("calibri",FONT_SIZE,100)
        fm = QtGui.QFontMetrics(font)
        preWidth = fm.width(preStr)
        postWidth = fm.width(postStr)
        #Calculo el tamaño de la imagen compuesta y la inicializo
        img = QtGui.QImage(IMAGE_PREFIX + key + ".png")
        if img.width() == 0:
            img = QtGui.QImage(SCALED_WIDTH,SCALED_WIDTH,\
                               QtGui.QImage.Format_ARGB32)
        SCALED_HEIGHT = (SCALED_WIDTH * img.height()) / img.width()
        image = QtGui.QImage(3*SCALED_WIDTH + \
                             4*PIXEL_SPACING + \
                             preWidth + \
                             postWidth, \
                             SCALED_HEIGHT,QtGui.QImage.Format_ARGB32)
        if qVersion() < '4.8':
            color = 0xFFFFFF
        else:
            color = QtGui.QColor(0, 0, 0,0)
        image.fill(color)
        painter.begin(image)
        painter.setFont(font)
        pos = 0
        #Pinto el texto de la izquierda
        rF = QtCore.QRectF(0,0,preWidth,SCALED_HEIGHT)
        painter.drawText(rF,QtCore.Qt.AlignCenter,preStr)
        pos = preWidth + PIXEL_SPACING

        #Pinto las teclas
        for f in ("Ctrl.png","Alt.png",key+".png"):
            img = QtGui.QImage(IMAGE_PREFIX + f)
            painter.drawImage(pos,0,img.scaledToWidth(SCALED_WIDTH,1))
            pos = pos + SCALED_WIDTH + PIXEL_SPACING

        #Pinto el texto de la derecha
        rF = QtCore.QRectF(pos,0,postWidth,SCALED_HEIGHT)
        painter.drawText(rF,QtCore.Qt.AlignCenter,postStr)
        painter.end()

        pix = QtGui.QPixmap().fromImage(image)
        self.pixmap.setPixmap(pix)
        screenCenter = QtCore.QPointF(screen.center())
        pixmapCenter = QtCore.QPointF(self.pixmap.boundingRect().center())
        self.pixmap.setPos( screenCenter - pixmapCenter)         
        
