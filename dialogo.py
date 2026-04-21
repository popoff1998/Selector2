# -*- coding: utf-8 -*-
"""Dialog UI for session confirmations. Compatible with PyQt4/PyQt5."""

from qt_compat import QtCore, QtGui

# UTF-8 handling for PyQt4/PyQt5 compatibility
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


def escape_accents_for_html(text):
    """Convierte acentos a entidades HTML para máxima compatibilidad."""
    replacements = {
        'á': '&aacute;', 'à': '&agrave;', 'ä': '&auml;', 'ã': '&atilde;',
        'é': '&eacute;', 'è': '&egrave;', 'ê': '&ecirc;', 'ë': '&euml;',
        'í': '&iacute;', 'ì': '&igrave;', 'î': '&icirc;', 'ï': '&iuml;',
        'ó': '&oacute;', 'ò': '&ograve;', 'ô': '&ocirc;', 'ö': '&ouml;', 'õ': '&otilde;',
        'ú': '&uacute;', 'ù': '&ugrave;', 'û': '&ucirc;', 'ü': '&uuml;',
        'ñ': '&ntilde;', 'ç': '&ccedil;',
        'Á': '&Aacute;', 'À': '&Agrave;', 'Ä': '&Auml;', 'Ã': '&Atilde;',
        'É': '&Eacute;', 'È': '&Egrave;', 'Ê': '&Ecirc;', 'Ë': '&Euml;',
        'Í': '&Iacute;', 'Ì': '&Igrave;', 'Î': '&Icirc;', 'Ï': '&Iuml;',
        'Ó': '&Oacute;', 'Ò': '&Ograve;', 'Ô': '&Ocirc;', 'Ö': '&Ouml;', 'Õ': '&Otilde;',
        'Ú': '&Uacute;', 'Ù': '&Ugrave;', 'Û': '&Ucirc;', 'Ü': '&Uuml;',
        'Ñ': '&Ntilde;', 'Ç': '&Ccedil;',
    }
    result = text
    for char, entity in replacements.items():
        result = result.replace(char, entity)
    return result


class Ui_Dialog:
    """Dialog confirmation UI compatible with PyQt4/PyQt5."""

    def setupUi(self, Dialog, text):
        """Setup dialog with confirmation message text."""
        self.text = text
        Dialog.setObjectName("Dialog")
        Dialog.setMinimumWidth(740)
        Dialog.setMaximumWidth(900)
        Dialog.setMinimumHeight(450)
        
        font = QtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(19)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        Dialog.setFont(font)
        Dialog.setStyleSheet(
            "QDialog { background-color: rgb(255, 255, 255); border: 2px solid black; border-radius: 10px; }\n"
            "font: 75 19pt \"Helvetica\";"
        )

        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(190, 410, 311, 71))
        
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
        self.textBrowser.setGeometry(QtCore.QRect(20, 20, 700, 380))
        
        # Permitir que se expanda al contenido
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.textBrowser.setSizePolicy(sizePolicy)
        
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
        
        # Adaptar el tamaño del diálogo al contenido
        Dialog.adjustSize()

    def retranslateUi(self, Dialog):
        """Set dialog text and title."""
        Dialog.setWindowTitle(_translate("Dialog", "ATENCIÓN", None))
        
        # Personalizar textos de botones y remover iconos
        cancel_btn = self.buttonBox.button(QtGui.QDialogButtonBox.Cancel)
        ok_btn = self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        
        cancel_btn.setText(_translate("Dialog", "Cancelar", None))
        ok_btn.setText(_translate("Dialog", "Ok", None))
        
        # Remover iconos
        cancel_btn.setIcon(QtGui.QIcon())
        ok_btn.setIcon(QtGui.QIcon())

        # Estructura HTML con charset UTF-8 para acentos
        textBodyHead = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n" \
                       "<html><head><meta charset=\"utf-8\"><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />" \
                       "<meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n" \
                       "p, li { white-space: pre-wrap; }\n" \
                       "</style></head><body style=\" font-family:'Helvetica'; font-size:16pt; font-weight:72; font-style:normal;\">\n"

        textLineHead = "<p style=\" margin-top:0px; margin-bottom:15px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">"
        textLineTail = "</span></p>\n"
        textBodyTail = "</body></html>"

        _text = textBodyHead
        # Reemplaza <br> con saltos de línea
        text_with_newlines = self.text.replace("<br>", "\n").replace("<br/>", "\n").replace("<BR>", "\n")
        
        # Convertir acentos a entidades HTML para máxima compatibilidad con diferentes sistemas
        text_with_newlines = escape_accents_for_html(text_with_newlines)
        
        for line in text_with_newlines.split("\n"):
            if line.strip():
                _text += textLineHead + line + textLineTail
        
        _text += textBodyTail
        
        # Usar setHtml directamente sin _translate para preservar entidades
        self.textBrowser.setHtml(_text)
        
        # Calcular la altura necesaria para el contenido
        doc = self.textBrowser.document()
        doc_width = 700  # Ancho fijo del textBrowser
        doc.setTextWidth(doc_width)
        
        # Obtener la altura necesaria
        needed_text_height = int(doc.size().height())
        if needed_text_height > 600:
            needed_text_height = 600
        if needed_text_height < 100:
            needed_text_height = 100
        
        # Ajustar la geometría del textBrowser
        self.textBrowser.setGeometry(QtCore.QRect(20, 20, doc_width, needed_text_height))
        
        # Reposicionar los botones debajo del texto
        button_y = needed_text_height + 30
        self.buttonBox.setGeometry(QtCore.QRect(190, button_y, 311, 71))
        
        # Ajustar el tamaño del diálogo
        dialog_height = needed_text_height + 110  # +110 para botones y márgenes
        if dialog_height > 800:
            dialog_height = 800
        if dialog_height < 450:
            dialog_height = 450
        
        Dialog.setMinimumHeight(dialog_height)
        Dialog.adjustSize()
