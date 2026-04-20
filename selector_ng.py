# -*- coding: utf-8 -*-
"""
Created on Thu Mar 07 08:31:30 2013

@author: tonin

Selector-ng
"""

import sys
import os
import logging
import subprocess
import shutil
import xml.etree.ElementTree as ET
import tempfile
import json
from typing import Any, Iterable, Optional


_BOOT_LOGGER = logging.getLogger(__name__)

# Activa/desactiva bytecode segun permisos de escritura del despliegue.
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_CAN_WRITE_MODULE_DIR = os.access(_MODULE_DIR, os.W_OK)
sys.dont_write_bytecode = not _CAN_WRITE_MODULE_DIR

from asset_resolver import resolve_asset_path


def _bool_env_enabled(name: str, default: bool = True) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


def _resolve_runtime_path(path_value: Optional[str]) -> str:
    """Resuelve rutas de config respetando absolutos y relativas al modulo."""

    if not path_value:
        return ""

    expanded = os.path.expandvars(os.path.expanduser(path_value))
    if os.path.isabs(expanded):
        return os.path.normpath(expanded)

    return os.path.normpath(os.path.join(_MODULE_DIR, expanded))


def _sync_selector_qrc_if_needed() -> None:
    """Sincroniza selector_ng_rc.py si qrc/imagenes cambiaron.

    - Prototipo (escritura): regenera cuando detecta desfase.
    - Produccion (solo lectura): no regenera y usa el RC existente.
    """

    if not _bool_env_enabled("SELECTOR_SYNC_QRC", default=True):
        return

    qrc_path = os.path.join(_MODULE_DIR, "selector_ng.qrc")
    rc_py_path = os.path.join(_MODULE_DIR, "selector_ng_rc.py")
    manifest_path = os.path.join(_MODULE_DIR, "selector_ng_rc.manifest.json")

    if not os.path.exists(qrc_path):
        return

    rc_mtime = os.stat(rc_py_path).st_mtime_ns if os.path.exists(rc_py_path) else -1

    try:
        root = ET.parse(qrc_path).getroot()
    except ET.ParseError as exc:
        _BOOT_LOGGER.warning("No se pudo parsear %s (%s)", qrc_path, exc)
        return

    # Calcula la fecha mas reciente entre el .qrc y los ficheros fuente resueltos.
    latest_source_mtime = os.stat(qrc_path).st_mtime_ns
    changed_sources = []
    manifest_entries = []
    qrc_dir = os.path.dirname(qrc_path)
    for node in root.findall(".//file"):
        rel = (node.text or "").strip()
        if not rel:
            continue
        alias_name = os.path.basename(rel)
        base_name = os.path.splitext(alias_name)[0]

        # El resolvedor elige el fichero local más reciente entre variantes.
        resolved_source = resolve_asset_path(base_name)
        if resolved_source.startswith(":/"):
            resolved_source = rel if os.path.isabs(rel) else os.path.join(qrc_dir, rel)

        if not os.path.exists(resolved_source):
            continue

        source_stat = os.stat(resolved_source)
        source_mtime = source_stat.st_mtime_ns
        latest_source_mtime = max(latest_source_mtime, source_mtime)
        manifest_entries.append(
            {
                "alias": alias_name,
                "source": os.path.relpath(resolved_source, _MODULE_DIR).replace("\\", "/"),
                "mtime_ns": source_mtime,
                "size": source_stat.st_size,
            }
        )
        if source_mtime >= rc_mtime:
            changed_sources.append(resolved_source)

    current_fingerprint = {"assets": manifest_entries}
    saved_fingerprint = None
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                saved_fingerprint = json.load(f)
        except (OSError, json.JSONDecodeError):
            saved_fingerprint = None

    fingerprint_changed = saved_fingerprint != current_fingerprint
    stale = rc_mtime <= latest_source_mtime or fingerprint_changed
    if not stale:
        return

    if not _CAN_WRITE_MODULE_DIR:
        _BOOT_LOGGER.info(
            "QRC desactualizado detectado pero entorno en solo lectura; "
            "se usa selector_ng_rc.py existente."
        )
        print(
            "[selector-ng] QRC desactualizado detectado en solo lectura; "
            "se usa selector_ng_rc.py existente."
        )
        return

    commands = []
    for cmd in ("pyrcc5", "pyrcc6", "pyrcc4"):
        resolved = shutil.which(cmd)
        if resolved:
            commands.append([resolved])

    commands.extend(
        [
            [sys.executable, "-m", "PyQt5.pyrcc_main"],
            [sys.executable, "-m", "PyQt6.pyrcc_main"],
        ]
    )

    attempt_errors = []
    for base_cmd in commands:
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".qrc",
                dir=qrc_dir,
                delete=False,
                encoding="utf-8",
            ) as tmp_qrc:
                tmp_qrc_path = tmp_qrc.name
                tmp_qrc.write("<!DOCTYPE RCC><RCC version=\"1.0\">\n")
                tmp_qrc.write("<qresource>\n")
                for entry in manifest_entries:
                    tmp_qrc.write(
                        f'    <file alias="{entry["alias"]}">{entry["source"]}</file>\n'
                    )
                tmp_qrc.write("</qresource>\n</RCC>\n")

            result = subprocess.run(
                base_cmd + ["-o", rc_py_path, tmp_qrc_path],
                cwd=qrc_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
        except OSError:
            continue
        finally:
            if "tmp_qrc_path" in locals() and os.path.exists(tmp_qrc_path):
                try:
                    os.remove(tmp_qrc_path)
                except OSError:
                    pass

        if result.returncode == 0:
            _BOOT_LOGGER.info("QRC sincronizado: %s -> %s", qrc_path, rc_py_path)
            changed_sources_rel = [
                os.path.relpath(path, _MODULE_DIR).replace("\\", "/")
                for path in changed_sources
            ]
            changed_list = ", ".join(changed_sources_rel) if changed_sources_rel else "selector_ng.qrc"
            try:
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(current_fingerprint, f, indent=2, ensure_ascii=False)
            except OSError as exc:
                _BOOT_LOGGER.warning("No se pudo escribir %s: %s", manifest_path, exc)
            print(
                "[selector-ng] RC regenerado: "
                "selector_ng_rc.py | fuentes cambiadas: "
                + changed_list
            )
            return

        attempt_errors.append(
            f"comando={base_cmd!r} stderr={result.stderr.strip() or result.stdout.strip()}"
        )

    _BOOT_LOGGER.warning(
        "No se pudo regenerar selector_ng_rc.py automaticamente. "
        "Instala/expone pyrcc5 o desactiva con SELECTOR_SYNC_QRC=0. %s",
        " | ".join(attempt_errors) if attempt_errors else "sin detalle de error",
    )


from qt_compat import QtCore, QtGui
import selector_ng_rc
import copy
from image import CompoundImage
from selector_settings import load_settings


LOGGER = logging.getLogger(__name__)

# Variables globales de configuración (cargadas desde JSON con fallback).
_SETTINGS = load_settings()

_RUNTIME = _SETTINGS.get("runtime", {})
_UI = _SETTINGS.get("ui", {})

VIEW_WEB = bool(_RUNTIME.get("view_web", False))
TEXT_ROTATE = bool(_RUNTIME.get("text_rotate", False))

SESSIONS_LIMIT = int(_RUNTIME.get("sessions_limit", 0))  # 0=unlimited
MINIMUN_SESSIONS_LIMIT = int(_RUNTIME.get("minimum_sessions_limit", 3))

PLATFORM = _SETTINGS.get("platform", {})

BEST_SESSION_SIZE = int(_UI.get("best_session_size", 3))
SCALE_SIZE = float(_UI.get("scale_size", 0.72))

SCALE_TRANSFORMATION_MODE = int(_UI.get("scale_transformation_mode", 1))  # 0=Fast 1=Smooth

ZOOM_FACTOR = float(_UI.get("zoom_factor", 1.7))
MARGEN_X = float(_UI.get("margin_x", 20.0))
MARGEN_Y = float(_UI.get("margin_y", 100.0))

DEFAULT_ICON_SIZE = float(_UI.get("default_icon_size", 256.0))
DEFAULT_FONT_SIZE = float(_UI.get("default_font_size", 25.0))
DEFAULT_FONT_WEIGHT = float(_UI.get("default_font_weight", 100.0))
MINIMUN_FONT_SIZE = float(_UI.get("minimum_font_size", 10.0))

COPYRIGHT_MESSAGE = str(_UI.get("copyright_message", "©Tonin 2026"))


_sync_selector_qrc_if_needed()


class MyWindow(QtGui.QGraphicsView):
    def __init__(self, scene: Any, app: Any) -> None:
        super(MyWindow,self).__init__(scene)
        self.app = app
        self.setFrameStyle(0)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
    def show(self) -> None:
        self.showFullScreen()
        # Mensaje útil durante pruebas para verificar foco real de la ventana.
        print("Tengo el foco? ", self.hasFocus())
        
    def keyPressEvent(self, e: Any) -> None:
        global ZOOM_FACTOR
        if e.key() == QtCore.Qt.Key_Escape:
            self.app.quit()
        if e.key() == QtCore.Qt.Key_Plus:
            ZOOM_FACTOR = ZOOM_FACTOR + 0.2
#    def changeEvent(self, e):
        #print "Change event ",e.type()


def get_screen_geometry(app: Any) -> Any:
    """Obtiene la geometria de la pantalla activa con fallback legacy."""

    # En Qt5+, usa QScreen para respetar el DISPLAY/servidor X activo.
    if hasattr(app, "primaryScreen"):
        screen_obj = app.primaryScreen()
        if screen_obj is not None and hasattr(screen_obj, "geometry"):
            return screen_obj.geometry()

    # Fallback compatible con Qt4.
    desktop = app.desktop() if hasattr(app, "desktop") else QtGui.QDesktopWidget()
    if hasattr(desktop, "primaryScreen") and hasattr(desktop, "screenGeometry"):
        return desktop.screenGeometry(desktop.primaryScreen())
    return desktop.screenGeometry()
        
class Pixmap(QtGui.QGraphicsWidget):
    clicked = QtCore.pyqtSignal()
    enter = QtCore.pyqtSignal()
    leave = QtCore.pyqtSignal()

    def __init__(
        self,
        pix: Any,
        parent: Any,
        sep_x: float,
        teclasSelector: Any,
        key_prefix: str = '',
        screen_rect: Any = None,
    ) -> None:
        super(Pixmap, self).__init__(None)
        self.setAcceptHoverEvents(True)

        self.orig = QtGui.QPixmap(pix)
        self.p = QtGui.QPixmap(pix)
        self.vt = parent.vt
        self.teclasSelector = teclasSelector
        self.key_prefix = key_prefix
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
        self.orig = self.orig.scaledToHeight(int(scale),SCALE_TRANSFORMATION_MODE)

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
        fontSize = int(fontSize)
        #print fontSize,ICON_SIZE
        font = QtGui.QFont("calibri",fontSize,100) #family,size,weight
        self.label =  QtGui.QGraphicsTextItem()
        self.label.setPlainText(parent.title.title().replace('"',''))
        self.label.setFont(font) 
        Rect = self.label.boundingRect()
        self.label.setPos(xCENTER - Rect.width()/2,yPOS + ICON_SIZE)

        #Ahora creo la imagen de las teclas
        screen = screen_rect or QtGui.QDesktopWidget().screenGeometry()
        self.teclas = CompoundImage("F" + str(self.vt),"Haga click o pulse ", \
                                    u"para ir a esta sesión",screen,
                                    image_prefix=self.key_prefix)
        self.teclas.pixmap.setVisible(False)
        
    def paint(self, painter: Any, option: Any, widget: Any) -> None:
        painter.drawPixmap(QtCore.QPointF(), self.p)

    def mousePressEvent(self, ev: Any) -> None:
        self.teclas.pixmap.setVisible(False)
        self.teclasSelector.pixmap.setVisible(True)
        self.clicked.emit()
        switch_virtual_terminal(self.vt)
        
    def hoverEnterEvent(self, ev: Any) -> None:
        self.teclas.pixmap.setVisible(True)
        self.teclasSelector.pixmap.setVisible(False)
        self.enter.emit()
        
    def hoverLeaveEvent(self, ev: Any) -> None:
        self.teclas.pixmap.setVisible(False)
        self.teclasSelector.pixmap.setVisible(True)
        self.leave.emit()
        
    def setGeometry(self, rect: Any) -> None:
        super(Pixmap, self).setGeometry(rect)

        if rect.size().width() > self.orig.size().width():
            self.p = self.orig.scaled(rect.size().toSize())
        else:
            self.p = QtGui.QPixmap(self.orig)

def scaleQRectF(qr_orig: Any, zoom_factor: float) -> Any:
    """Devuelve un QRectF escalado en el factor indicado."""

    # Copia defensiva para no modificar el rectángulo original.
    qr_dest = copy.copy(qr_orig)

    desp = ((zoom_factor-1) * qr_dest.width())/2
    qr_dest.setX(qr_dest.x() - desp)
    qr_dest.setY(qr_dest.y() - desp)
    qr_dest.setWidth(qr_orig.width() + 2*desp)
    qr_dest.setHeight(qr_orig.height() + 2*desp)
    return qr_dest


def switch_virtual_terminal(vt: int) -> None:
    """Intenta cambiar a la VT indicada de forma segura y portable."""

    # chvt es una utilidad Linux; en otros sistemas no hacemos nada.
    if not sys.platform.startswith('linux'):
        LOGGER.debug("Ignorando cambio de VT en plataforma no Linux: %s", sys.platform)
        return

    try:
        subprocess.run(["chvt", str(vt)], check=False)
    except OSError as exc:
        LOGGER.warning("No se pudo ejecutar chvt %s: %s", vt, exc)

def createStates(objects: Iterable[Any], parent: Any) -> None:
    for obj in objects:
        # Geometría normal y geometría ampliada para hover.
        origRect = obj.geometry()
        zoomRect = scaleQRectF(origRect,ZOOM_FACTOR)
        # Ajuste de posición vertical del label en zoom.
        origY = obj.label.y()
        zoomY = obj.label.y() - zoomRect.y() + origRect.y()

        # Estado con zoom.
        state_zoom = QtCore.QState(parent)
        state_zoom.assignProperty(obj, 'geometry', zoomRect)
        state_zoom.assignProperty(obj.label, 'y' , zoomY)
        if TEXT_ROTATE:
            state_zoom.assignProperty(obj.label, 'rotation' , 360)
        parent.addTransition(obj.enter, state_zoom)

        # Estado sin zoom.
        state_nozoom = QtCore.QState(parent)
        state_nozoom.assignProperty(obj, 'geometry', origRect)
        state_nozoom.assignProperty(obj.label, 'y' , origY)
        if TEXT_ROTATE:
            state_nozoom.assignProperty(obj.label, 'rotation' , 0)
        parent.addTransition(obj.leave, state_nozoom)
        
        # Estado tras click.
        state_clicked = QtCore.QState(parent)
        state_clicked.assignProperty(obj, 'geometry', origRect)
        state_clicked.assignProperty(obj.label, 'y' , origY)
        if TEXT_ROTATE:
            state_clicked.assignProperty(obj.label, 'rotation' , 0)
        parent.addTransition(obj.clicked, state_clicked)

def createAnimations(objects: Iterable[Any], machine: Any) -> None:
    for obj in objects:
        animationGroup = QtCore.QParallelAnimationGroup(obj)
        animationPixmap = QtCore.QPropertyAnimation(obj, b'geometry', obj)
        animationLabel = QtCore.QPropertyAnimation(obj.label, b'y', obj)
        animationGroup.addAnimation(animationPixmap)
        animationGroup.addAnimation(animationLabel)

        if TEXT_ROTATE:
            animationRotate = QtCore.QPropertyAnimation(obj.label, b'rotation', obj)
            animationGroup.addAnimation(animationRotate)
        
        machine.addDefaultAnimation(animationGroup)

def main(argv: Optional[list[str]] = None) -> int:
    from config_parser import config
    from web import Browser

    if argv is None:
        argv = sys.argv

    app = QtGui.QApplication(argv)

    # Algunas versiones/entornos no exponen pyqtRemoveInputHook.
    if hasattr(QtCore, 'pyqtRemoveInputHook'):
        QtCore.pyqtRemoveInputHook()

    # Inicializa la escena a tamaño de la pantalla actual, en coords locales.
    screen = get_screen_geometry(app)
    scene = QtGui.QGraphicsScene(0.0, 0.0, float(screen.width()), float(screen.height()))

    platform_config = PLATFORM.get(sys.platform, PLATFORM.get('win32', {}))
    background_setting = platform_config.get('background')
    Config = _resolve_runtime_path(platform_config.get('config'))
    key_prefix = _resolve_runtime_path(platform_config.get('key_prefix', ''))
    background_path = resolve_asset_path(background_setting)

    background_pixmap = QtGui.QPixmap(background_path)
    if not background_pixmap.isNull():
        scene.setBackgroundBrush(QtGui.QBrush(background_pixmap))
    else:
        LOGGER.warning("No se pudo cargar el fondo: %s", background_path)

    if background_path.startswith(':/'):
        background_url = background_path
    else:
        background_url = QtCore.QUrl.fromLocalFile(background_path).toString()

    app.setStyleSheet(f"QWidget {{border-image: url('{background_url}') }}")
      
    # Lee la configuración y prepara las sesiones.
    cf = config(Config, sessions_limit=SESSIONS_LIMIT)

    if cf.numeroSesiones <= 0:
        LOGGER.error("No hay sesiones configuradas en %s", Config)
        return 1

    # Calcula separación horizontal y rellena objetos de sesión.
    sep_x = (screen.width() - 2*MARGEN_X) / cf.numeroSesiones
    
    teclasSelector = CompoundImage(
        "F6",
        "Pulse ",
        "para volver al selector",
        screen,
        image_prefix=key_prefix,
    )
    teclasSelector.pixmap.setVisible(True)
    scene.addItem(teclasSelector.pixmap)

    cf.rellenaSesiones(
        sep_x,
        teclasSelector,
        pixmap_factory=Pixmap,
        key_prefix=key_prefix,
        screen_rect=screen,
    )
    
    # Añade elementos a la escena y construye lista animable.
    objects = []
    for s in cf.sesiones:
        scene.addItem(s.pixmap)
        scene.addItem(s.pixmap.label)
        scene.addItem(s.pixmap.teclas.pixmap)
        objects.append(s.pixmap)

    if VIEW_WEB:    
        browser = Browser()
        scene.addItem(browser)  
    
    text = scene.addText(str(COPYRIGHT_MESSAGE),QtGui.QFont("calibri",10))
    text.setOpacity(0.5)
    text.setPos(QtCore.QPointF(screen.width() - 100, screen.height() - 30))
    
    # Crea ventana principal y máquina de estados para animaciones.
    window = MyWindow(scene,app)

    machine = QtCore.QStateMachine()
    machine.setGlobalRestorePolicy(QtCore.QStateMachine.RestoreProperties)

    group = QtCore.QState(machine)

    idleState = QtCore.QState(group)
    group.setInitialState(idleState)
    
    createStates(objects , group)
    createAnimations(objects, machine)

    machine.setInitialState(group)
    machine.start()

    # Muestra la ventana maximizada.
    window.show()
    

    return app.exec_()


#Aqui comienza la aplicacion en si
if __name__ == '__main__':
    sys.exit(main())

