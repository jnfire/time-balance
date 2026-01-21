import os
import json
from datetime import datetime, date

# --- CONFIGURACIÓN ---
HORAS_BASE = 7
MINUTOS_BASE = 45
ARCHIVO_DATOS = "historial_horas.json"

def cargar_datos():
    """Carga el historial de días desde el archivo JSON."""
    if not os.path.exists(ARCHIVO_DATOS):
        return {} # Retorna un diccionario vacío si no hay archivo
    try:
        with open(ARCHIVO_DATOS, "r") as f:
            return json.load(f)
    except (ValueError, json.JSONDecodeError):
        return {}

def guardar_datos(datos):
    """Guarda el historial completo en el archivo."""
    with open(ARCHIVO_DATOS, "w") as f:
        json.dump(datos, f, indent=4)

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

def registrar_jornada(datos):
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

    guardar_datos(datos)
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
        if info['diferencia'] > 0: diff_fmt = "+" + diff_fmt

        print(f"{fecha} | Trab: {info['horas']}h {info['minutos']}m | Saldo: {diff_fmt}")

def main():
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
        print("3. Salir")

        opcion = input("\nElige opción: ")

        if opcion == "1":
            registrar_jornada(datos)
            input("\nPresiona ENTER para continuar...")
        elif opcion == "2":
            ver_historial(datos)
            input("\nPresiona ENTER para continuar...")
        elif opcion == "3":
            print("¡Hasta mañana!")
            break

if __name__ == "__main__":
    main()
