import os
import json
import tempfile
import shutil
import errno
from datetime import datetime
from . import constants


def _resolver_archivo(archivo_path=None):
    """Resuelve la ruta final del archivo de historial."""
    if archivo_path:
        ruta = archivo_path
    elif constants.ENV_HISTORIAL in os.environ and os.environ[constants.ENV_HISTORIAL].strip():
        ruta = os.environ[constants.ENV_HISTORIAL]
    else:
        ruta = constants.ARCHIVO_DATOS

    ruta = os.path.expanduser(ruta)
    return os.path.abspath(ruta)


def _migrar_formato_antiguo(datos):
    """Convierte el formato plano antiguo al nuevo formato estructurado."""
    # Si ya tiene metadata, no hacemos nada
    if isinstance(datos, dict) and "metadata" in datos:
        return datos

    # Si es un diccionario vacío o tiene fechas como claves, migramos
    return {
        "metadata": {
            "project_name": "General",
            "horas_base": constants.HORAS_BASE,
            "minutos_base": constants.MINUTOS_BASE,
            "version": "1.0"
        },
        "registros": datos if isinstance(datos, dict) else {}
    }


def cargar_datos(archivo_path=None):
    """Carga el historial y asegura que tenga el formato estructurado."""
    archivo = _resolver_archivo(archivo_path)
    if not os.path.exists(archivo):
        # Devolvemos un esqueleto nuevo si no hay archivo
        return _migrar_formato_antiguo({})
        
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)
            return _migrar_formato_antiguo(datos)
    except (ValueError, json.JSONDecodeError):
        return _migrar_formato_antiguo({})


def guardar_datos(datos, archivo_path=None):
    """Guarda el historial completo usando escritura atómica."""
    archivo = _resolver_archivo(archivo_path)
    dir_dest = os.path.dirname(archivo)
    if dir_dest and not os.path.exists(dir_dest):
        os.makedirs(dir_dest, exist_ok=True)

    contenido = json.dumps(datos, indent=4, ensure_ascii=False)
    fd, ruta_temp = tempfile.mkstemp(prefix="historial_", suffix=".json", dir=dir_dest or ".")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as tmpf:
            tmpf.write(contenido)
            try:
                tmpf.flush()
                os.fsync(tmpf.fileno())
            except Exception:
                pass

        try:
            os.replace(ruta_temp, archivo)
        except OSError as e:
            if getattr(e, 'errno', None) == errno.EXDEV:
                shutil.copy2(ruta_temp, archivo)
                os.remove(ruta_temp)
            else:
                raise
    finally:
        if 'ruta_temp' in locals() and os.path.exists(ruta_temp):
            try:
                os.remove(ruta_temp)
            except OSError:
                pass


def _crear_backup(archivo):
    """Crea un backup con timestamp del archivo dado si existe."""
    if not os.path.exists(archivo):
        return None
    ts = datetime.now().strftime('%Y%m%dT%H%M%S')
    backup = f"{archivo}.bak.{ts}"
    shutil.copy2(archivo, backup)
    try:
        shutil.copy2(archivo, f"{archivo}.bak")
    except Exception:
        pass
    return backup
