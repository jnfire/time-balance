import os
import sys
import argparse
from datetime import date, datetime
from . import constants
from . import core
from . import storage
from . import io


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
    minutos_objetivo = (constants.HORAS_BASE * 60) + constants.MINUTOS_BASE
    minutos_trabajados = (horas * 60) + minutos
    diferencia = minutos_trabajados - minutos_objetivo

    # Guardamos en el diccionario
    datos[fecha] = {
        "horas": horas,
        "minutos": minutos,
        "diferencia": diferencia
    }

    storage.guardar_datos(datos, archivo_path)
    print(f"\n✅ Registro guardado para el {fecha}.")
    print(f"   Diferencia del día: {core.formatear_tiempo(diferencia)}")


def ver_historial(datos, limite=5):
    """Muestra los últimos registros."""
    if limite > 0:
        print(f"\n--- Últimos {limite} registros ---")
    else:
        print("\n--- Historial completo ---")
        
    # Ordenamos las fechas de más reciente a más antigua
    fechas_ordenadas = sorted(datos.keys(), reverse=True)
    if limite > 0:
        fechas_ordenadas = fechas_ordenadas[:limite]
        
    if not fechas_ordenadas:
        print("No hay registros.")

    for fecha in fechas_ordenadas:
        info = datos[fecha]
        diff_fmt = core.formatear_tiempo(info['diferencia'])
        # Añadimos un '+' visual si es positivo para que se vea mejor
        if info['diferencia'] > 0:
            diff_fmt = "+" + diff_fmt

        print(f"{fecha} | Trab: {info['horas']}h {info['minutos']}m | Saldo: {diff_fmt}")


def menu_interactivo():
    """Bucle del menú interactivo principal."""
    while True:
        datos = storage.cargar_datos()
        saldo_total = core.calcular_saldo_total(datos)

        os.system('cls' if os.name == 'nt' else 'clear')

        print("\n" + "="*50)
        print(f"   SALDO TOTAL ACUMULADO: {core.formatear_tiempo(saldo_total)}")
        print(f"   (Base diaria: {constants.HORAS_BASE}h {constants.MINUTOS_BASE}m)")
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
                destino = io.exportar_historial(ruta)
                print(f"\n✅ Exportado en: {destino}")
            except Exception as e:
                print(f"Error al exportar: {e}")
            input("\nPresiona ENTER para continuar...")
        elif opcion == "4":
            ruta = input("Ruta fuente a importar: ")
            modo_input = input(f"Modo ({constants.MODE_MERGE}/{constants.MODE_OVERWRITE}) [{constants.MODE_MERGE}]: ").strip().lower()
            modo = modo_input if modo_input else constants.MODE_MERGE
            try:
                res = io.importar_historial(ruta, modo=modo)
                print(f"\n✅ Importación completada. Entradas totales ahora: {len(res)}")
            except Exception as e:
                print(f"Error al importar: {e}")
            input("\nPresiona ENTER para continuar...")
        elif opcion == "5":
            print("¡Hasta mañana!")
            break


def main():
    parser = argparse.ArgumentParser(
        description="time-balance: Herramienta sencilla para controlar tu saldo horario."
    )
    parser.add_argument(
        "-s", "--status", action="store_true", help="Muestra solo el saldo total acumulado."
    )
    parser.add_argument(
        "-l", "--list", type=int, nargs="?", const=5, help="Lista los últimos N registros (por defecto 5)."
    )
    parser.add_argument(
        "--version", action="store_true", help="Muestra la versión de la aplicación."
    )

    args = parser.parse_args()

    if args.version:
        from . import __version__
        print(f"time-balance v{__version__}")
        return

    datos = storage.cargar_datos()

    if args.status:
        saldo_total = core.calcular_saldo_total(datos)
        print(f"Saldo acumulado: {core.formatear_tiempo(saldo_total)}")
        return

    if args.list is not None:
        ver_historial(datos, limite=args.list)
        return

    # Si no hay argumentos, lanzamos el menú interactivo
    menu_interactivo()
