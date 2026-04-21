# -*- coding: utf-8 -*-
"""Dialog UI for session confirmations. Compatible with PyQt4/PyQt5."""

from qt_compat import QtCore, QtGui


class Ui_Dialog:
    """Dialog confirmation UI compatible with PyQt4/PyQt5."""

    def setupUi(self, Dialog, text):
        """Setup dialog with confirmation message text."""
        self.text = text
        Dialog.setObjectName("Dialog")
        Dialog.resize(707, 517)
        
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(19)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        Dialog.setFont(font)
        Dialog.setStyleSheet(
            "background-color: rgb(255, 255, 255);\n"
            "font: 75 19pt \"Helvetica\";"
        )

        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(190, 390, 311, 71))
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        
        font = QtGui.QFont()
        font.setFamily("Sans Serif")
        font.setPointSize(16)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.buttonBox.setFont(font)
        self.buttonBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.buttonBox.setAutoFillBackground(False)
        self.buttonBox.setStyleSheet(
            "font: 16pt \"Sans Serif\";\n"
            "background-color: rgb(213, 213, 213);\n"
            "border-style: solid;\n"
            "border-color: black;\n"
            "border-width: 2px;\n"
            "border-radius: 10px;\n"
            "min-width: 5em"
        )
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        
        self.textBrowser = QtGui.QTextBrowser(Dialog)
        self.textBrowser.setGeometry(QtCore.QRect(40, 40, 621, 301))
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.textBrowser.setFont(font)
        self.textBrowser.setFrameShape(QtGui.QFrame.NoFrame)
        self.textBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textBrowser.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textBrowser.setObjectName("textBrowser")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

    def retranslateUi(self, Dialog):
        """Set dialog text and title."""
        Dialog.setWindowTitle("ATENCIÓN")
        
        # Personalizar textos de botones y remover iconos
        cancel_btn = self.buttonBox.button(QtGui.QDialogButtonBox.Cancel)
        ok_btn = self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        
        cancel_btn.setText("Cancelar")
        ok_btn.setText("Ok")
        
        # Remover iconos
        cancel_btn.setIcon(QtGui.QIcon())
        ok_btn.setIcon(QtGui.QIcon())

        # Estructura HTML idéntica a la versión antigua que funciona
        textBodyHead = (
            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" "
            "\"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
            "<html><head><meta name=\"qrichtext\" content=\"1\" />"
            "<style type=\"text/css\">\n"
            "p, li { white-space: pre-wrap; }\n"
            "</style></head><body style=\" font-family:'Helvetica'; "
            "font-size:15pt; font-weight:72; font-style:normal;\">\n"
        )

        textLineHead = (
            "<p style=\" margin-top:0px; margin-bottom:15px; margin-left:0px; "
            "margin-right:0px; -qt-block-indent:0; text-indent:0px;\">"
            "<span style=\" font-weight:600;\">"
        )
        textLineTail = "</span></p>\n"
        textBodyTail = "</body></html>"

        _text = textBodyHead
        # Reemplaza <br> con saltos de línea
        text_with_newlines = self.text.replace("<br>", "\n").replace("<br/>", "\n").replace("<BR>", "\n")
        
        for line in text_with_newlines.split("\n"):
            if line.strip():
                _text += textLineHead + line + textLineTail
        
        _text += textBodyTail
        self.textBrowser.setHtml(_text)
