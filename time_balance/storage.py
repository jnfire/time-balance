import os
import json
import tempfile
import shutil
import errno
from datetime import datetime
from . import constants


def _resolver_archivo(archivo_path=None):
    """Resuelve la ruta final del archivo de historial.
    Prioridad: argumento > VARIABLE DE ENTORNO > ARCHIVO_DATOS (CWD)
    """
    if archivo_path:
        ruta = archivo_path
    elif constants.ENV_HISTORIAL in os.environ and os.environ[constants.ENV_HISTORIAL].strip():
        ruta = os.environ[constants.ENV_HISTORIAL]
    else:
        ruta = constants.ARCHIVO_DATOS

    ruta = os.path.expanduser(ruta)
    return os.path.abspath(ruta)


def cargar_datos(archivo_path=None):
    """Carga el historial de días desde el archivo JSON."""
    archivo = _resolver_archivo(archivo_path)
    if not os.path.exists(archivo):
        return {}  # Retorna un diccionario vacío si no hay archivo
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except (ValueError, json.JSONDecodeError):
        return {}


def guardar_datos(datos, archivo_path=None):
    """Guarda el historial completo en el archivo usando escritura atómica."""
    archivo = _resolver_archivo(archivo_path)
    dir_dest = os.path.dirname(archivo)
    if dir_dest and not os.path.exists(dir_dest):
        os.makedirs(dir_dest, exist_ok=True)

    # Serializamos y escribimos a fichero temporal antes de reemplazar
    contenido = json.dumps(datos, indent=4, ensure_ascii=False)
    # Aseguramos que el temporal se cree en el mismo directorio de destino
    fd, ruta_temp = tempfile.mkstemp(prefix="historial_", suffix=".json", dir=dir_dest or ".")
    try:
        # Escribimos y forzamos a disco el temporal antes de intentar el replace
        with os.fdopen(fd, 'w', encoding='utf-8') as tmpf:
            tmpf.write(contenido)
            try:
                tmpf.flush()
                os.fsync(tmpf.fileno())
            except Exception:
                # Si fsync no está soportado en la plataforma, continuamos igualmente
                pass

        # Intentamos reemplazo atómico
        try:
            os.replace(ruta_temp, archivo)
            # Intentamos fsync al directorio destino para asegurar persistencia del rename
            try:
                dirfd = os.open(os.path.dirname(archivo) or '.', os.O_RDONLY)
                try:
                    os.fsync(dirfd)
                finally:
                    os.close(dirfd)
            except Exception:
                pass
        except OSError as e:
            # En sistemas con filesystems diferentes, os.replace puede fallar con EXDEV.
            # Como fallback hacemos copy + fsync del destino.
            if getattr(e, 'errno', None) == errno.EXDEV:
                shutil.copy2(ruta_temp, archivo)
                try:
                    # Forzar fsync en el archivo copiado
                    with open(archivo, 'rb') as f:
                        try:
                            os.fsync(f.fileno())
                        except Exception:
                            pass
                except Exception:
                    pass
                try:
                    os.remove(ruta_temp)
                except OSError:
                    pass
            else:
                raise
    finally:
        # Limpieza best-effort del temporal si quedara
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
    # También mantenemos/actualizamos archivo.bak simple
    try:
        shutil.copy2(archivo, f"{archivo}.bak")
    except Exception:
        # Error al crear/actualizar la copia secundaria .bak; no es crítico, se ignora.
        pass
    return backup
