import os
import json
import tempfile
import shutil
import errno
from datetime import datetime
from . import storage
from . import constants


def _validar_historial(datos):
    """Valida la estructura básica del historial cargado """
    if not isinstance(datos, dict):
        raise ValueError("Historial debe ser un objeto/diccionario JSON")
    for fecha, info in datos.items():
        if not isinstance(fecha, str):
            raise ValueError("Las claves del historial deben ser strings con formato YYYY-MM-DD")

        try:
            datetime.strptime(fecha, "%Y-%m-%d")

        except ValueError:
            raise ValueError(f"Clave de fecha inválida: {fecha}. Debe tener formato YYYY-MM-DD")

        if not isinstance(info, dict):
            raise ValueError(f"Entrada para {fecha} debe ser un objeto con 'horas','minutos','diferencia'.")

        for key in ('horas', 'minutos', 'diferencia'):
            if key not in info:
                raise ValueError(f"Entrada para {fecha} falta clave '{key}'")
            if not isinstance(info[key], int):
                raise ValueError(f"'{key}' en {fecha} debe ser un entero")


def exportar_historial(ruta_destino, archivo_path=None):
    """Exporta el historial actual a la ruta indicada.

    Args:
        ruta_destino (str): Ruta de archivo donde guardar el JSON exportado.
        archivo_path (str|None): Ruta del archivo de datos actual (opcional).

    Returns:
        str: Ruta absoluta donde se escribió el archivo.
    """
    datos = storage.cargar_datos(archivo_path)
    destino = os.path.expanduser(ruta_destino)
    destino = os.path.abspath(destino)
    dir_dest = os.path.dirname(destino)
    if dir_dest and not os.path.exists(dir_dest):
        os.makedirs(dir_dest, exist_ok=True)

    # Escribimos de forma atómica
    contenido = json.dumps(datos, indent=4, ensure_ascii=False)
    # Crear el temporal en el mismo directorio de destino para evitar EXDEV
    fd, ruta_temp = tempfile.mkstemp(prefix="export_", suffix=".json", dir=dir_dest or ".")
    try:
        # Escribimos y sincronizamos el temporal antes del rename para mayor robustez
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
            os.replace(ruta_temp, destino)
            # Intentamos fsync al directorio destino para asegurar persistencia del rename
            try:
                dirfd = os.open(os.path.dirname(destino) or '.', os.O_RDONLY)
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
                shutil.copy2(ruta_temp, destino)
                try:
                    # Forzar fsync en el archivo copiado
                    with open(destino, 'rb') as f:
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

    return destino


def importar_historial(ruta_fuente, modo=constants.MODE_MERGE, archivo_path=None):
    """Importa un historial desde un archivo externo.

    Args:
        ruta_fuente (str): Ruta del archivo JSON a importar.
        modo (str): constants.MODE_MERGE (por defecto) o constants.MODE_OVERWRITE.
        archivo_path (str|None): Ruta del archivo de datos destino (opcional).

    Returns:
        dict: El historial resultante cargado y guardado en destino.
    """
    fuente = os.path.expanduser(ruta_fuente)
    fuente = os.path.abspath(fuente)
    if not os.path.exists(fuente):
        raise FileNotFoundError(f"Archivo de importación no existe: {fuente}")

    try:
        with open(fuente, 'r', encoding='utf-8') as f:
            datos_fuente = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido en archivo de importación: {e}")

    _validar_historial(datos_fuente)

    destino = storage._resolver_archivo(archivo_path)
    if modo == constants.MODE_OVERWRITE:
        # Backup del destino
        storage._crear_backup(destino)
        # Guardamos el archivo importado como el nuevo historial
        storage.guardar_datos(datos_fuente, destino)
        return datos_fuente
    elif modo == constants.MODE_MERGE:
        # Creamos backup por precaución
        storage._crear_backup(destino)
        datos_destino = storage.cargar_datos(destino)
        # Merge: la fuente sobrescribe en caso de conflicto
        datos_destino.update(datos_fuente)
        storage.guardar_datos(datos_destino, destino)
        return datos_destino
    else:
        raise ValueError(f"Modo desconocido. Usa {constants.MODOS_IMPORTACION_VALIDOS}.")
