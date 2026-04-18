# -*- coding: utf-8 -*-
"""Carga de configuracion para selector-ng desde JSON con fallback seguro."""

import json
import logging
import os
from copy import deepcopy
from typing import Any


LOGGER = logging.getLogger(__name__)


DEFAULT_SETTINGS = {
    "runtime": {
        "view_web": False,
        "text_rotate": False,
        "sessions_limit": 0,
        "minimum_sessions_limit": 3,
    },
    "ui": {
        "best_session_size": 3,
        "scale_size": 0.72,
        "scale_transformation_mode": 1,
        "zoom_factor": 1.7,
        "margin_x": 20.0,
        "margin_y": 100.0,
        "default_icon_size": 256.0,
        "default_font_size": 25.0,
        "default_font_weight": 100.0,
        "minimum_font_size": 10.0,
        "copyright_message": "©Tonin 2026",
    },
    "platform": {
        "win32": {
            "background": "./fondo.png",
            "config": "conf.txt",
            "key_prefix": "computer_key_",
        },
        "linux": {
            "background": "/usr/local/uco/selector/fondo.png",
            "config": "conf.txt",
            "key_prefix": "computer_key_",
        },
        "linux2": {
            "background": "/usr/local/uco/selector/fondo.png",
            "config": "/etc/thinstation.network",
            "key_prefix": "/usr/local/uco/selector/computer_key_",
        },
    },
}


def _merge_dict(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    """Merge recursivo de diccionarios preservando defaults."""

    merged = deepcopy(base)
    for key, value in incoming.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def _settings_path() -> str:
    env_path = os.environ.get("SELECTOR_SETTINGS_FILE")
    if env_path:
        return env_path
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "selector_settings.json")


def load_settings() -> dict[str, Any]:
    """Carga la configuracion JSON y la fusiona con defaults."""

    settings = deepcopy(DEFAULT_SETTINGS)
    path = _settings_path()

    if not os.path.exists(path):
        LOGGER.info("No se encontro selector_settings.json, usando defaults: %s", path)
        return settings

    try:
        with open(path, "r", encoding="utf-8") as f:
            custom = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        LOGGER.warning("No se pudo cargar configuracion %s (%s). Se usan defaults.", path, exc)
        return settings

    if not isinstance(custom, dict):
        LOGGER.warning("Formato invalido en %s. Se usan defaults.", path)
        return settings

    return _merge_dict(settings, custom)
