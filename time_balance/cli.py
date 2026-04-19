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


def configurar_proyecto(datos):
    """Permite configurar los metadatos del proyecto."""
    metadatos = datos["metadata"]
    print("\n--- Configuración del Proyecto ---")
    nuevo_nombre = input(f"Nombre del proyecto [{metadatos['project_name']}]: ").strip()
    if nuevo_nombre:
        metadatos["project_name"] = nuevo_nombre

    try:
        horas_str = input(f"Horas base diaria [{metadatos['horas_base']}]: ").strip()
        if horas_str:
            metadatos["horas_base"] = int(horas_str)
        minutos_str = input(f"Minutos base diaria [{metadatos['minutos_base']}]: ").strip()
        if minutos_str:
            metadatos["minutos_base"] = int(minutos_str)
    except ValueError:
        print("❌ Error: Introduce números enteros. Configuración no guardada.")


def registrar_jornada(datos, archivo_path=None):
    fecha = solicitar_fecha()
    metadatos = datos["metadata"]
    registros = datos["registros"]

    # --- CONTROL DE DUPLICADOS ---
    if fecha in registros:
        print(f"\n⚠️  ATENCIÓN: Ya existe un registro para el día {fecha}.")
        print(f"   Registrado anteriormente: {registros[fecha]['horas']}h {registros[fecha]['minutos']}m")
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

    # Cálculos basados en la configuración del archivo
    minutos_objetivo = (metadatos["horas_base"] * 60) + metadatos["minutos_base"]
    minutos_trabajados = (horas * 60) + minutos
    diferencia = minutos_trabajados - minutos_objetivo

    # Guardamos en el diccionario
    registros[fecha] = {
        "horas": horas,
        "minutos": minutos,
        "diferencia": diferencia
    }

    storage.guardar_datos(datos, archivo_path)
    print(f"\n✅ Registro guardado para el {fecha}.")
    print(f"   Diferencia del día: {core.formatear_tiempo(diferencia)}")


def ver_historial(datos, limite=5):
    """Muestra los últimos registros."""
    registros = datos["registros"]
    
    if limite > 0:
        print(f"\n--- Últimos {limite} registros ---")
    else:
        print("\n--- Historial completo ---")
        
    # Ordenamos las fechas de más reciente a más antigua
    fechas_ordenadas = sorted(registros.keys(), reverse=True)
    if limite > 0:
        fechas_ordenadas = fechas_ordenadas[:limite]
        
    if not fechas_ordenadas:
        print("No hay registros.")

    for fecha in fechas_ordenadas:
        info = registros[fecha]
        diferencia_formateada = core.formatear_tiempo(info['diferencia'])
        # Añadimos un '+' visual si es positivo para que se vea mejor
        if info['diferencia'] > 0:
            diferencia_formateada = "+" + diferencia_formateada

        print(f"{fecha} | Trab: {info['horas']}h {info['minutos']}m | Saldo: {diferencia_formateada}")


def menu_interactivo():
    """Bucle del menú interactivo principal."""
    while True:
        datos = storage.cargar_datos()
        metadatos = datos["metadata"]
        saldo_total = core.calcular_saldo_total(datos["registros"])

        os.system('cls' if os.name == 'nt' else 'clear')

        print("\n" + "="*50)
        print(f"   PROYECTO: {metadatos['project_name'].upper()}")
        print(f"   SALDO TOTAL ACUMULADO: {core.formatear_tiempo(saldo_total)}")
        print(f"   (Base diaria: {metadatos['horas_base']}h {metadatos['minutos_base']}m)")
        print("="*50)

        print("\nOpciones:")
        print("1. Registrar jornada (o corregir día)")
        print("2. Ver últimos registros")
        print("3. Configurar proyecto (nombre/jornada)")
        print("4. Exportar historial a archivo")
        print("5. Importar historial desde archivo")
        print("6. Salir")

        opcion = input("\nElige opción: ")

        if opcion == "1":
            registrar_jornada(datos)
            input("\nPresiona ENTER para continuar...")
        elif opcion == "2":
            ver_historial(datos)
            input("\nPresiona ENTER para continuar...")
        elif opcion == "3":
            configurar_proyecto(datos)
            storage.guardar_datos(datos)
            input("\nPresiona ENTER para continuar...")
        elif opcion == "4":
            ruta = input("Ruta destino (ej: /ruta/mi_export.json): ")
            try:
                destino = io.exportar_historial(ruta)
                print(f"\n✅ Exportado en: {destino}")
            except Exception as error:
                print(f"Error al exportar: {error}")
            input("\nPresiona ENTER para continuar...")
        elif opcion == "5":
            ruta = input("Ruta fuente a importar: ")
            modo_input = input(f"Modo ({constants.MODE_MERGE}/{constants.MODE_OVERWRITE}) [{constants.MODE_MERGE}]: ").strip().lower()
            modo = modo_input if modo_input else constants.MODE_MERGE
            try:
                resultado_importacion = io.importar_historial(ruta, modo=modo)
                print(f"\n✅ Importación completada. Entradas totales ahora: {len(resultado_importacion['registros'])}")
            except Exception as error:
                print(f"Error al importar: {error}")
            input("\nPresiona ENTER para continuar...")
        elif opcion == "6":
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

    argumentos = parser.parse_args()

    if argumentos.version:
        print(f"time-balance v{constants.VERSION}")
        return

    datos = storage.cargar_datos()

    if argumentos.status:
        saldo_total = core.calcular_saldo_total(datos["registros"])
        print(f"Proyecto: {datos['metadata']['project_name']}")
        print(f"Saldo acumulado: {core.formatear_tiempo(saldo_total)}")
        return

    if argumentos.list is not None:
        ver_historial(datos, limite=argumentos.list)
        return

    # Si no hay argumentos, lanzamos el menú interactivo
    menu_interactivo()
