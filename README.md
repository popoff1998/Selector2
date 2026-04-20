# Selector-ng

Selector visual de sesiones escrito originalmente en PyQt y migrado para ejecutarse en Python 3 con compatibilidad Qt.

## Caracteristicas

- Interfaz con iconos, hover y animaciones.
- Carga dinamica de assets:
  - Primero busca imagenes en disco (`./` y `./assets`).
  - Si no existen, usa recursos embebidos (`qrc`) como fallback.
- Sincronizacion automatica de `qrc` en entornos con escritura:
  - Si detecta cambios en `selector_ng.qrc` o en cualquier imagen referenciada en el qrc, regenera `selector_ng_rc.py` al arrancar.
  - En solo lectura no intenta regenerar nada.
- Configuracion externa con `selector_settings.json`.
- Modo compatible con despliegues de solo lectura (NFS RO):
  - Ajusta automaticamente `sys.dont_write_bytecode` segun permisos del directorio.

## Requisitos

- Python 3.10+ (recomendado 3.12)
- PyQt5 (o PyQt4 en entornos legacy)

## Ejecucion

```bash
python selector_ng.py
```

## Configuracion

El fichero principal es `selector_settings.json`.

Secciones:

- `runtime`:
  - `view_web`: mostrar widget web opcional.
  - `text_rotate`: animacion de rotacion de texto.
  - `sessions_limit`: limite de sesiones (`0` = sin limite).
  - `minimum_sessions_limit`: minimo para escalado visual.
- `ui`:
  - Margenes, zoom, tamanos y mensaje de copyright.
- `platform`:
  - Paths por plataforma para `background`, `config` y `key_prefix`.

Tambien puedes cargar otro fichero con variable de entorno:

```bash
SELECTOR_SETTINGS_FILE=/ruta/a/mi_config.json python selector_ng.py
```

## Assets dinamicos

Para cambiar iconos o fondo, basta con reemplazar archivos en disco:

- Iconos de sesion: por `TYPE` en `conf.txt`.
  - Ejemplo: `SESSION_2_TYPE=2019` -> busca `2019.png`, `2019.jpg`, `2019.jpeg`.
  - Si el `TITLE` contiene un nombre o numero de icono, se intenta antes que el `TYPE`.
- Fondo: segun `platform.<plataforma>.background`.

No hace falta regenerar `selector_ng_rc.py` para cambios normales de imagen si el archivo local existe.

Si quieres mantener el fallback embebido al dia en prototipo, la app ya lo intenta automaticamente cuando tiene permisos de escritura.

Puedes desactivar esa sincronizacion con:

```bash
SELECTOR_SYNC_QRC=0 python selector_ng.py
```

## Entornos de prototipo vs explotacion

- Prototipo (escritura permitida): Python puede generar `__pycache__`.
- Prototipo (escritura permitida):
  - Python puede generar `__pycache__`.
  - La app regenera `selector_ng_rc.py` si detecta cambios en `selector_ng.qrc` o sus imagenes fuente.
- Explotacion NFS RO: se desactiva automaticamente escritura de bytecode.
  - Aunque detecte desajuste entre fuentes y RC, usa el `selector_ng_rc.py` existente.

## Tests

Se incluyen pruebas unitarias del parser:

```bash
python -m unittest tests.test_config_parser -v
```

## Estructura principal

- `selector_ng.py`: entrada principal y UI.
- `config_parser.py`: parser de sesiones.
- `image.py`: composicion de imagen de teclas.
- `asset_resolver.py`: resolucion de assets disco/qrc.
- `selector_settings.py`: carga de configuracion con defaults.
- `selector_settings.json`: configuracion editable.

## Notas de mantenimiento

- Si vas a empaquetar en entorno cerrado, mantener `qrc` como fallback sigue siendo buena practica.
- Para cambios funcionales, ejecutar siempre:

```bash
python -m py_compile selector_ng.py config_parser.py image.py web.py qt_compat.py asset_resolver.py selector_settings.py
python -m unittest tests.test_config_parser -v
```
