# -*- coding: utf-8 -*-
"""
Created on Thu Mar 07 08:35:11 2013

@author: tonin

Parser-sesiones para selector-ng
"""

import logging
import re
from typing import Any

from qt_compat import QtGui
from asset_resolver import resolve_asset_path


LOGGER = logging.getLogger(__name__)


class session(object):
    """Objeto para almacenar una sesion."""

    def __init__(
        self,
        indice: int,
        valores: dict[str, str],
        sep_x: float,
        teclasSelector: Any,
        parent: Any,
        pixmap_factory: Any,
        key_prefix: str,
    ) -> None:
        self.indice = indice
        self.valores = valores
        self.title = valores.get("TITLE", "")
        self.type = valores.get("TYPE", "")

        try:
            self.vt = int(valores.get("SCREEN", "0")) + 3
        except ValueError:
            self.vt = 3

        # Resuelve icono desde disco (dinamico) con fallback a qrc.
        icon_name = self.type.strip() or "unknown"
        pixmap_rc = resolve_asset_path(icon_name)

        self.numeroSesiones = parent.numeroSesiones
        self.pixmap = pixmap_factory(
            QtGui.QPixmap(pixmap_rc), self, sep_x, teclasSelector, key_prefix
        )


class config(object):
    """Representa un fichero de configuracion de sesiones.

    Atributos relevantes:
    - text: lineas crudas del fichero.
    - sessionsList: lista normalizada de sesiones.
    - numeroSesiones: cantidad de sesiones validas.
    """

    def __init__(self, filename: str, sessions_limit: int = 0) -> None:
        self.filename = filename
        self.sessions_limit = sessions_limit
        self.text: list[str] = []
        self.sessionsDict: dict[str, dict[str, str]] = {}
        self.sessionsList: list[dict[str, str]] = []
        self.numeroSesiones = 0

        try:
            with open(filename, "r", encoding="utf-8") as f:
                self.text = f.readlines()
        except OSError as exc:
            LOGGER.error(
                "No se pudo leer el fichero de configuracion %s: %s", filename, exc
            )

        self.getSessionsList()

    def getSessionsRawList(self) -> list[list[tuple[str, str, str]]]:
        """Devuelve una lista raw de lineas SESSION_<N>_<KEY>=<VALUE>."""

        # Elimina las lineas de comentario o en blanco.
        text = [x for x in self.text if re.search(r"^[^#].", x)]

        # Parsea los elementos de SESSION.
        raw = [re.findall(r"SESSION_([0-9]+)_(.*)=(.*)", x) for x in text]

        # Elimina elementos vacios.
        self.sessionsRawList = [x for x in raw if len(x) > 0]
        self.sessionsRawList.sort()
        return self.sessionsRawList

    def getSessionsDict(self) -> dict[str, dict[str, str]]:
        """Devuelve sesiones como diccionario de diccionarios (metodo legado)."""

        for linea in self.getSessionsRawList():
            for indice, var, value in linea:
                if int(indice) < self.sessions_limit or self.sessions_limit == 0:
                    self.sessionsDict.setdefault(indice, {})[var] = value
        return self.sessionsDict

    def getSessionsList(self) -> list[dict[str, str]]:
        """Construye la lista normalizada de sesiones filtradas."""

        self.sessionsList = []
        for linea in self.getSessionsRawList():
            for indice, var, value in linea:
                index = int(indice)
                while len(self.sessionsList) < index + 1:
                    self.sessionsList.append({})
                self.sessionsList[index].setdefault(var, value)

        # Elimina huecos vacíos cuando los índices no son consecutivos.
        self.sessionsList = [x for x in self.sessionsList if x]

        # Elimina la sesion del propio selector.
        self.sessionsList = [x for x in self.sessionsList if x.get("TYPE") != "selector"]

        # Aplica limite maximo de sesiones cuando corresponde.
        if self.sessions_limit != 0:
            self.sessionsList = [
                item
                for idx, item in enumerate(self.sessionsList)
                if idx < self.sessions_limit
            ]

        self.numeroSesiones = len(self.sessionsList)
        return self.sessionsList

    def rellenaSesiones(
        self,
        sep_x: float,
        teclasSelector: Any,
        pixmap_factory: Any,
        key_prefix: str = "",
    ) -> None:
        """Construye los objetos session listos para mostrar en la UI."""

        self.sesiones = []
        for idx, values in enumerate(self.sessionsList):
            sess = session(
                idx,
                values,
                sep_x,
                teclasSelector,
                self,
                pixmap_factory,
                key_prefix,
            )
            self.sesiones.append(sess)
