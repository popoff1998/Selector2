# -*- coding: utf-8 -*-

PIXEL_SPACING = 10 #separacion en pixeles
SCALED_WIDTH = 70 #ancho de los iconos escalados
FONT_SIZE = 22

from qt_compat import QtCore, QtGui
import sys


def qVersion():
    return QtCore.qVersion()


PYQT_VERSION_STR = QtCore.PYQT_VERSION_STR

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
    Imagen compuesta con texto + teclas (Ctrl, Alt y tecla de función).
    """

    def __init__(self, key, preStr, postStr, screen, image_prefix=''):

        
        super(CompoundImage, self).__init__(None)
        self.pixmap = QtGui.QGraphicsPixmapItem()
        painter = QtGui.QPainter()

        # El prefijo se inyecta desde el llamador para evitar imports circulares.
        IMAGE_PREFIX = image_prefix or ''
        font = QtGui.QFont("calibri",FONT_SIZE,100)
        fm = QtGui.QFontMetrics(font)

        # Qt moderno prefiere horizontalAdvance; mantenemos fallback.
        if hasattr(fm, 'horizontalAdvance'):
            preWidth = fm.horizontalAdvance(preStr)
            postWidth = fm.horizontalAdvance(postStr)
        else:
            preWidth = fm.width(preStr)
            postWidth = fm.width(postStr)
        # Calcula tamaño final de la imagen compuesta.
        img = QtGui.QImage(IMAGE_PREFIX + key + ".png")
        if img.width() == 0:
            img = QtGui.QImage(SCALED_WIDTH,SCALED_WIDTH,\
                               QtGui.QImage.Format_ARGB32)
        SCALED_HEIGHT = int((SCALED_WIDTH * img.height()) / img.width())
        image = QtGui.QImage(int(3 * SCALED_WIDTH + \
                     4 * PIXEL_SPACING + \
                     preWidth + \
                     postWidth), \
                     int(SCALED_HEIGHT), QtGui.QImage.Format_ARGB32)
        if qVersion() < '4.8':
            color = 0xFFFFFF
        else:
            color = QtGui.QColor(0, 0, 0,0)
        image.fill(color)
        painter.begin(image)
        painter.setFont(font)
        pos = 0
        # Texto izquierdo.
        rF = QtCore.QRectF(0,0,preWidth,SCALED_HEIGHT)
        painter.drawText(rF,QtCore.Qt.AlignCenter,preStr)
        pos = preWidth + PIXEL_SPACING

        # Teclas.
        for f in ("Ctrl.png","Alt.png",key+".png"):
            img = QtGui.QImage(IMAGE_PREFIX + f)
            if img.isNull():
                # Fallback transparente si falta algún icono de tecla.
                img = QtGui.QImage(SCALED_WIDTH, SCALED_HEIGHT,
                                   QtGui.QImage.Format_ARGB32)
                img.fill(QtGui.QColor(0, 0, 0, 0))
                painter.drawImage(pos, 0, img)
            else:
                painter.drawImage(pos,0,img.scaledToWidth(SCALED_WIDTH,1))
            pos = pos + SCALED_WIDTH + PIXEL_SPACING

        # Texto derecho.
        rF = QtCore.QRectF(pos,0,postWidth,SCALED_HEIGHT)
        painter.drawText(rF,QtCore.Qt.AlignCenter,postStr)
        painter.end()

        pix = QtGui.QPixmap().fromImage(image)
        self.pixmap.setPixmap(pix)
        screenCenter = QtCore.QPointF(screen.center())
        pixmapCenter = QtCore.QPointF(self.pixmap.boundingRect().center())
        self.pixmap.setPos( screenCenter - pixmapCenter)         
        
