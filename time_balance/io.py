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
    
    # Validar presencia de metadata y registros
    if "metadata" not in datos or "registros" not in datos:
        # Intentar validar como formato antiguo (esto permite importar archivos viejos)
        for fecha, info in datos.items():
            _validar_entrada_registro(fecha, info)
        return

    # Validar metadata
    metadatos = datos["metadata"]
    if not isinstance(metadatos, dict):
        raise ValueError("Metadata debe ser un objeto")
    for clave in ("project_name", "horas_base", "minutos_base"):
        if clave not in metadatos:
            raise ValueError(f"Metadata falta clave '{clave}'")

    # Validar registros
    registros = datos["registros"]
    if not isinstance(registros, dict):
        raise ValueError("Registros debe ser un objeto")
    for fecha, info in registros.items():
        _validar_entrada_registro(fecha, info)


def _validar_entrada_registro(fecha, info):
    """Valida una única entrada de registro."""
    if not isinstance(fecha, str):
        raise ValueError("Las claves del historial deben ser strings con formato YYYY-MM-DD")

    try:
        datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Clave de fecha inválida: {fecha}. Debe tener formato YYYY-MM-DD")

    if not isinstance(info, dict):
        raise ValueError(f"Entrada para {fecha} debe ser un objeto con 'horas','minutos','diferencia'.")

    for clave in ('horas', 'minutos', 'diferencia'):
        if clave not in info:
            raise ValueError(f"Entrada para {fecha} falta clave '{clave}'")
        if not isinstance(info[clave], int):
            raise ValueError(f"'{clave}' en {fecha} debe ser un entero")


def exportar_historial(ruta_destino, archivo_path=None):
    """Exporta el historial actual a la ruta indicada."""
    datos = storage.cargar_datos(archivo_path)
    destino = os.path.expanduser(ruta_destino)
    destino = os.path.abspath(destino)
    dir_dest = os.path.dirname(destino)
    if dir_dest and not os.path.exists(dir_dest):
        os.makedirs(dir_dest, exist_ok=True)

    contenido = json.dumps(datos, indent=4, ensure_ascii=False)
    file_descriptor, ruta_temp = tempfile.mkstemp(prefix="export_", suffix=".json", dir=dir_dest or ".")
    try:
        with os.fdopen(file_descriptor, 'w', encoding='utf-8') as archivo_temporal:
            archivo_temporal.write(contenido)
            try:
                archivo_temporal.flush()
                os.fsync(archivo_temporal.fileno())
            except Exception:
                pass

        try:
            os.replace(ruta_temp, destino)
        except OSError as error:
            if getattr(error, 'errno', None) == errno.EXDEV:
                shutil.copy2(ruta_temp, destino)
                os.remove(ruta_temp)
            else:
                raise
    finally:
        if 'ruta_temp' in locals() and os.path.exists(ruta_temp):
            try:
                os.remove(ruta_temp)
            except OSError:
                pass

    return destino


def importar_historial(ruta_fuente, modo=constants.MODE_MERGE, archivo_path=None):
    """Importa un historial desde un archivo externo."""
    fuente = os.path.expanduser(ruta_fuente)
    fuente = os.path.abspath(fuente)
    if not os.path.exists(fuente):
        raise FileNotFoundError(f"Archivo de importación no existe: {fuente}")

    try:
        with open(fuente, 'r', encoding='utf-8') as archivo_json:
            datos_fuente = json.load(archivo_json)
    except json.JSONDecodeError as error:
        raise ValueError(f"JSON inválido en archivo de importación: {error}")

    _validar_historial(datos_fuente)
    
    # Aseguramos que la fuente tenga formato nuevo tras validar
    datos_fuente = storage._migrar_formato_antiguo(datos_fuente)

    destino = storage._resolver_archivo(archivo_path)
    if modo == constants.MODE_OVERWRITE:
        storage._crear_backup(destino)
        storage.guardar_datos(datos_fuente, destino)
        return datos_fuente
    elif modo == constants.MODE_MERGE:
        storage._crear_backup(destino)
        datos_actuales = storage.cargar_datos(destino)
        # Merge de registros
        datos_actuales["registros"].update(datos_fuente["registros"])
        # Mantenemos los metadatos locales (el proyecto destino manda)
        storage.guardar_datos(datos_actuales, destino)
        return datos_actuales
    else:
        raise ValueError(f"Modo desconocido. Usa {constants.MODOS_IMPORTACION_VALIDOS}.")
