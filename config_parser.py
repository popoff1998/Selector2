# -*- coding: utf-8 -*-
"""
Created on Thu Mar 07 08:35:11 2013

@author: tonin

Parser-sesiones para selector-ng
"""

import logging
import re
from typing import Any, Optional

from qt_compat import QtGui
from asset_resolver import resolve_asset_path


LOGGER = logging.getLogger(__name__)


def _read_text_lines_with_fallback(path: str) -> list[str]:
    """Lee texto probando codificaciones frecuentes en despliegues legacy."""

    encodings = ("utf-8", "utf-8-sig", "cp1252", "latin-1")
    last_exc: Optional[Exception] = None
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as f:
                lines = f.readlines()
            if enc != "utf-8":
                LOGGER.warning("%s leido con encoding de fallback: %s", path, enc)
            return lines
        except UnicodeDecodeError as exc:
            last_exc = exc
            continue

    # Ultimo recurso para no bloquear la app por caracteres puntuales corruptos.
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    if last_exc is not None:
        LOGGER.warning(
            "%s no pudo leerse limpiamente en UTF-8/cp1252/latin-1 (%s). "
            "Se cargara con caracteres reemplazados.",
            path,
            last_exc,
        )
    return lines


class session(object):
    """Objeto para almacenar una sesion."""

    @staticmethod
    def _icon_candidates_for_values(valores: dict[str, str]) -> list[str]:
        """Devuelve candidatos de icono priorizando el TITLE de la sesion."""

        candidates: list[str] = []

        title = (valores.get("TITLE") or "").strip().strip('"').strip("'")
        if title:
            candidates.append(title)

            # Intenta equivalencias habituales entre variantes con y sin guiones.
            title_no_separators = re.sub(r"[-_\s]+", "", title)
            if title_no_separators and title_no_separators not in candidates:
                candidates.append(title_no_separators)

            if title_no_separators and title_no_separators != title:
                dashed_title = re.sub(r"(?<=\D)(?=\d)|(?<=\d)(?=\D)", "-", title_no_separators)
                if dashed_title and dashed_title not in candidates:
                    candidates.append(dashed_title)

            normalized_title = re.sub(r"\s+", "-", title)
            if normalized_title != title:
                candidates.append(normalized_title)

            digit_tokens = re.findall(r"\d+", title)
            for token in digit_tokens:
                if token not in candidates:
                    candidates.append(token)

        icon_override = (valores.get("ICON") or "").strip()
        if icon_override:
            candidates.insert(0, icon_override)

        pixmap_override = (valores.get("PIXMAP") or "").strip()
        if pixmap_override and pixmap_override not in candidates:
            candidates.insert(0, pixmap_override)

        image_override = (valores.get("IMAGE") or "").strip()
        if image_override and image_override not in candidates:
            candidates.insert(0, image_override)

        type_name = (valores.get("TYPE") or "").strip()
        if type_name and type_name not in candidates:
            candidates.append(type_name)

        if "unknown" not in candidates:
            candidates.append("unknown")

        return candidates

    @staticmethod
    def _resolve_pixmap_for_values(valores: dict[str, str]) -> str:
        """Busca el primer pixmap valido usando TITLE y luego TYPE."""

        for candidate in session._icon_candidates_for_values(valores):
            pixmap_rc = resolve_asset_path(candidate)
            if not QtGui.QPixmap(pixmap_rc).isNull():
                return pixmap_rc

        return resolve_asset_path("unknown")

    def __init__(
        self,
        indice: int,
        valores: dict[str, str],
        sep_x: float,
        teclasSelector: Any,
        parent: Any,
        pixmap_factory: Any,
        key_prefix: str,
        screen_rect: Any = None,
    ) -> None:
        self.indice = indice
        self.valores = valores
        self.title = valores.get("TITLE", "")
        self.type = valores.get("TYPE", "")

        try:
            self.vt = int(valores.get("SCREEN", "0")) + 3
        except ValueError:
            self.vt = 3

        # Resuelve icono por TITLE con fallback a TYPE y, al final, unknown.
        pixmap_rc = self._resolve_pixmap_for_values(valores)

        self.numeroSesiones = parent.numeroSesiones
        self.pixmap = pixmap_factory(
            QtGui.QPixmap(pixmap_rc),
            self,
            sep_x,
            teclasSelector,
            key_prefix,
            screen_rect,
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
            self.text = _read_text_lines_with_fallback(filename)
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
        screen_rect: Any = None,
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
                screen_rect,
            )
            self.sesiones.append(sess)
