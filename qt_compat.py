"""Qt compatibility helpers for PyQt4/PyQt5."""

from types import SimpleNamespace


QT_API = "pyqt4"
QtCore = None
QtGui = None
QtWebKit = None

try:
    from PyQt4 import QtCore as _QtCore, QtGui as _QtGui

    QtCore = _QtCore
    QtGui = _QtGui

    try:
        from PyQt4 import QtWebKit as _QtWebKit
    except ImportError:
        _QtWebKit = None
    QtWebKit = _QtWebKit
except ImportError:
    from PyQt5 import QtCore as _QtCore, QtGui as _QtGui, QtWidgets as _QtWidgets

    QT_API = "pyqt5"
    QtCore = _QtCore

    # Keep old QtGui-based code working by exposing QtWidgets symbols via QtGui.
    _attrs = {name: getattr(_QtGui, name) for name in dir(_QtGui)}
    for name in dir(_QtWidgets):
        if not name.startswith("_"):
            _attrs[name] = getattr(_QtWidgets, name)
    QtGui = SimpleNamespace(**_attrs)

    try:
        from PyQt5 import QtWebKitWidgets as _QtWebKitWidgets
    except ImportError:
        _QtWebKitWidgets = None
    QtWebKit = _QtWebKitWidgets
