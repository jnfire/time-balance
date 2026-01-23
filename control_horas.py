# Shim de compatibilidad: exponemos la API pero permitiendo que
# la variable `ARCHIVO_DATOS` local sea modificada por tests/scripts.
import time_balance as tb

# Valor por defecto local (los tests esperan poder modificar esta variable)
ARCHIVO_DATOS = tb.ARCHIVO_DATOS

# Re-exportamos funciones simples directamente o mediante wrappers para
# que usen la variable local ARCHIVO_DATOS cuando corresponde.
formatear_tiempo = tb.formatear_tiempo
calcular_saldo_total = tb.calcular_saldo_total
ver_historial = tb.ver_historial


def cargar_datos(archivo_path=None):
    return tb.cargar_datos(archivo_path or ARCHIVO_DATOS)


def guardar_datos(datos, archivo_path=None):
    return tb.guardar_datos(datos, archivo_path or ARCHIVO_DATOS)


def registrar_jornada(datos, archivo_path=None):
    return tb.registrar_jornada(datos, archivo_path or ARCHIVO_DATOS)


def exportar_historial(ruta_destino, archivo_path=None):
    return tb.exportar_historial(ruta_destino, archivo_path or ARCHIVO_DATOS)


def importar_historial(ruta_fuente, modo='merge', archivo_path=None):
    return tb.importar_historial(ruta_fuente, modo=modo, archivo_path=archivo_path or ARCHIVO_DATOS)


# Reexportar main para entry point y CLI
main = tb.main

__all__ = [
    'ARCHIVO_DATOS', 'cargar_datos', 'guardar_datos', 'formatear_tiempo', 'calcular_saldo_total',
    'registrar_jornada', 'ver_historial', 'exportar_historial', 'importar_historial', 'main'
]
