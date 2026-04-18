# -*- coding: utf-8 -*-
"""Resolucion de assets con prioridad a disco y fallback a recursos Qt."""

import os
from typing import Iterable

from qt_compat import QtGui


# Directorios de busqueda por defecto para assets locales.
_DEFAULT_ASSET_DIRS = (
    ".",
    "./assets",
)


def _has_extension(name: str) -> bool:
    return "." in os.path.basename(name)


def _build_candidates(name: str, extensions: Iterable[str]) -> list[str]:
    """Construye candidatos de nombre con y sin extension."""

    if _has_extension(name):
        return [name]

    return [name + ext for ext in extensions]


def _normalize_path(path: str) -> str:
    return os.path.normpath(path)


def _resolve_local_asset(name: str) -> str | None:
    """Resuelve la ruta local mas reciente para un asset dado."""

    candidates = []
    for base_dir in _DEFAULT_ASSET_DIRS:
        candidate = _normalize_path(os.path.join(base_dir, name))
        if os.path.exists(candidate):
            candidates.append(candidate)

    if not candidates:
        return None

    return max(candidates, key=os.path.getmtime)


def resolve_asset_path(name: str, extensions=(".png", ".jpg", ".jpeg")) -> str:
    """Devuelve la mejor ruta para un asset: disco primero, qrc despues."""

    local_candidates = []
    for candidate_name in _build_candidates(name, extensions):
        local = _resolve_local_asset(candidate_name)
        if local is not None:
            local_candidates.append(local)

    if local_candidates:
        return max(local_candidates, key=os.path.getmtime)

    # Fallback a recurso embebido Qt.
    for candidate_name in _build_candidates(name, extensions):
        qrc_path = ":/" + candidate_name
        pix = QtGui.QPixmap(qrc_path)
        if not pix.isNull():
            return qrc_path

    # Devuelve el primer candidato por compatibilidad con flujos existentes.
    first = _build_candidates(name, extensions)[0]
    return ":/" + first


def clear_asset_cache() -> None:
    """Compatibilidad historica; ya no hay cache persistente."""

    return None
