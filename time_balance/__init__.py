import os
import json
from datetime import datetime, date
import tempfile
import shutil
import errno

# --- CONFIGURACIÓN ---
HORAS_BASE = 7
MINUTOS_BASE = 45
ARCHIVO_DATOS = "historial_horas.json"
ENV_HISTORIAL = "HISTORIAL_PATH"


def _resolver_archivo(archivo_path=None):
    """Resuelve la ruta final del archivo de historial.
    Prioridad: argumento > VARIABLE DE ENTORNO > ARCHIVO_DATOS (CWD)
    """
    if archivo_path:
        ruta = archivo_path
    elif ENV_HISTORIAL in os.environ and os.environ[ENV_HISTORIAL].strip():
        ruta = os.environ[ENV_HISTORIAL]
    else:
        ruta = ARCHIVO_DATOS

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


def formatear_tiempo(minutos_totales):
    """Convierte minutos a formato legible +/- Xh Ym."""
    signo = ""
    if minutos_totales < 0:
        signo = "-"
        minutos_totales = abs(minutos_totales)

    horas = minutos_totales // 60
    minutos = minutos_totales % 60
    return f"{signo}{horas}h {minutos}m"


def calcular_saldo_total(datos):
    """Recorre todo el historial y suma las diferencias."""
    saldo = 0
    for fecha, info in datos.items():
        saldo += info['diferencia']
    return saldo


def solicitar_fecha():
    """Pide la fecha o usa la de hoy por defecto."""
    hoy = date.today().strftime("%Y-%m-%d")
    print(f"\nFecha del registro (Enter para usar HOY: {hoy})")
    fecha_input = input("O introduce fecha (YYYY-MM-DD): ").strip()

    if not fecha_input:
        return hoy

    # Validar formato simple
    try:
        datetime.strptime(fecha_input, "%Y-%m-%d")
        return fecha_input
    except ValueError:
        print("❌ Formato de fecha incorrecto. Usando fecha de hoy.")
        return hoy


def registrar_jornada(datos, archivo_path=None):
    fecha = solicitar_fecha()

    # --- CONTROL DE DUPLICADOS ---
    if fecha in datos:
        print(f"\n⚠️  ATENCIÓN: Ya existe un registro para el día {fecha}.")
        print(f"   Registrado anteriormente: {datos[fecha]['horas']}h {datos[fecha]['minutos']}m")
        confirmacion = input("¿Quieres SOBREESCRIBIRLO? (s/n): ").lower()
        if confirmacion != 's':
            print("Operación cancelada.")
            return

    print(f"--- Introduciendo datos para: {fecha} ---")
    try:
        horas = int(input("Horas trabajadas: ") or 0)
        minutos = int(input("Minutos trabajados: ") or 0)
    except ValueError:
        print("❌ Error: Introduce números enteros.")
        return

    # Cálculos
    minutos_objetivo = (HORAS_BASE * 60) + MINUTOS_BASE
    minutos_trabajados = (horas * 60) + minutos
    diferencia = minutos_trabajados - minutos_objetivo

    # Guardamos en el diccionario
    datos[fecha] = {
        "horas": horas,
        "minutos": minutos,
        "diferencia": diferencia
    }

    guardar_datos(datos, archivo_path)
    print(f"\n✅ Registro guardado para el {fecha}.")
    print(f"   Diferencia del día: {formatear_tiempo(diferencia)}")


def ver_historial(datos):
    """Muestra los últimos registros."""
    print("\n--- Últimos 5 registros ---")
    # Ordenamos las fechas de más reciente a más antigua
    fechas_ordenadas = sorted(datos.keys(), reverse=True)[:5]
    if not fechas_ordenadas:
        print("No hay registros.")

    for fecha in fechas_ordenadas:
        info = datos[fecha]
        diff_fmt = formatear_tiempo(info['diferencia'])
        # Añadimos un '+' visual si es positivo para que se vea mejor
        if info['diferencia'] > 0:
            diff_fmt = "+" + diff_fmt

        print(f"{fecha} | Trab: {info['horas']}h {info['minutos']}m | Saldo: {diff_fmt}")


# ----------------- Funciones de export/import -----------------

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
    datos = cargar_datos(archivo_path)
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


def importar_historial(ruta_fuente, modo='merge', archivo_path=None):
    """Importa un historial desde un archivo externo.

    Args:
        ruta_fuente (str): Ruta del archivo JSON a importar.
        modo (str): 'merge' (por defecto) o 'overwrite'. En 'merge', las entradas del archivo
                    importado sobrescriben en caso de conflicto. En 'overwrite' se reemplaza
                    totalmente el historial (se crea backup antes).
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

    destino = _resolver_archivo(archivo_path)
    if modo == 'overwrite':
        # Backup del destino
        _crear_backup(destino)
        # Guardamos el archivo importado como el nuevo historial
        guardar_datos(datos_fuente, destino)
        return datos_fuente
    elif modo == 'merge':
        # Creamos backup por precaución
        _crear_backup(destino)
        datos_destino = cargar_datos(destino)
        # Merge: la fuente sobrescribe en caso de conflicto
        datos_destino.update(datos_fuente)
        guardar_datos(datos_destino, destino)
        return datos_destino
    else:
        raise ValueError("Modo desconocido. Usa 'merge' o 'overwrite'.")


# ----------------- CLI / entry point -----------------

def main():
    # Interfaz interactiva única (sin argparse ni subcomandos).
    while True:
        datos = cargar_datos()
        saldo_total = calcular_saldo_total(datos)

        os.system('cls' if os.name == 'nt' else 'clear')

        print("\n" + "="*50)
        print(f"   SALDO TOTAL ACUMULADO: {formatear_tiempo(saldo_total)}")
        print(f"   (Base diaria: {HORAS_BASE}h {MINUTOS_BASE}m)")
        print("="*50)

        print("\nOpciones:")
        print("1. Registrar jornada (o corregir día)")
        print("2. Ver últimos registros")
        print("3. Exportar historial a archivo")
        print("4. Importar historial desde archivo")
        print("5. Salir")

        opcion = input("\nElige opción: ")

        if opcion == "1":
            registrar_jornada(datos)
            input("\nPresiona ENTER para continuar...")
        elif opcion == "2":
            ver_historial(datos)
            input("\nPresiona ENTER para continuar...")
        elif opcion == "3":
            ruta = input("Ruta destino (ej: /ruta/mi_export.json): ")
            try:
                destino = exportar_historial(ruta)
                print(f"\n✅ Exportado en: {destino}")
            except Exception as e:
                print(f"Error al exportar: {e}")
            input("\nPresiona ENTER para continuar...")
        elif opcion == "4":
            ruta = input("Ruta fuente a importar: ")
            modo = input("Modo (merge/overwrite) [merge]: ") or 'merge'
            try:
                res = importar_historial(ruta, modo=modo)
                print(f"\n✅ Importación completada. Entradas totales ahora: {len(res)}")
            except Exception as e:
                print(f"Error al importar: {e}")
            input("\nPresiona ENTER para continuar...")
        elif opcion == "5":
            print("¡Hasta mañana!")
            break


if __name__ == "__main__":
    main()
