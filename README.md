# time-balance

Descripción
-----------
`time-balance` es una pequeña herramienta de consola en Python para registrar jornadas laborales diarias y calcular el saldo acumulado respecto a una jornada base. Guarda un historial simple en formato JSON (`historial_horas.json`) y muestra los últimos registros y el saldo acumulado.

Características principales
-------------------------
- Registro interactivo de horas y minutos por día.
- Prevención de sobrescritura con confirmación del usuario.
- Cálculo de la diferencia diaria respecto a una jornada base configurable.
- Visualización de los últimos registros y del saldo total.

Requisitos
----------
- Python 3.8+ (solo usa módulos de la biblioteca estándar: `os`, `json`, `datetime`).
- Sistema operativo: macOS / Linux / Windows (con soporte para ejecutar scripts Python).

Instalación
-----------
1. Clona o descarga el repositorio:

   git clone <url-del-repo>

2. Entra en la carpeta del proyecto:

   cd time-balance

3. (Opcional) crea y activa un entorno virtual:

   python3 -m venv .venv
   source .venv/bin/activate   # macOS / Linux (zsh / bash)
   .venv\Scripts\activate    # Windows (cmd/PowerShell)

4. No hay dependencias externas requeridas; si más adelante se añaden, se listarán en `requirements.txt`.

Uso
---
Comandos habituales para iniciar la aplicación (desde la raíz del proyecto):

- macOS / Linux (zsh / bash):

  python3 control_horas.py

  o si tu sistema tiene `python` apuntando a Python 3:

  python control_horas.py

  También puedes ejecutar el script `iniciar.sh` si está disponible:

  ./iniciar.sh

- Windows (cmd / PowerShell):

  python control_horas.py

  o usar `iniciar.bat` haciendo doble clic o con:

  iniciar.bat

Interacción básica
------------------
1. Ejecuta el script.
2. Selecciona "1. Registrar jornada" para añadir o corregir un día.
3. Si el día ya existe, el script pide confirmación antes de sobrescribir:
   `¿Quieres SOBREESCRIBIRLO? (s/n):` — responde `s` para sobrescribir.

Explicación de archivos generados y datos
----------------------------------------
- `historial_horas.json`: archivo JSON en la raíz del proyecto que contiene el historial de registros. Estructura:

  {
      "YYYY-MM-DD": {
          "horas": <int>,
          "minutos": <int>,
          "diferencia": <int>  // diferencia en minutos respecto a la jornada base
      },
      ...
  }

- Ejemplo de entrada en `historial_horas.json`:

  {
      "2026-01-20": {
          "horas": 8,
          "minutos": 0,
          "diferencia": 15
      },
      "2026-01-19": {
          "horas": 7,
          "minutos": 30,
          "diferencia": -15
      }
  }

Notas para evitar sobrescribir datos
-----------------------------------
- El script ya detecta entradas duplicadas por fecha y solicita confirmación antes de sobrescribir. Aún así, para mayor seguridad:
  1. Realiza copias de seguridad regulares del archivo: por ejemplo, copiar `historial_horas.json` a `historial_horas.json.bak` antes de cambios masivos.
  2. Usa control de versiones (git) y no agregues `historial_horas.json` si prefieres mantener datos locales fuera del repositorio. Si quieres mantenerlo versionado, haz commits frecuentes.
  3. Si prefieres mantener varios historiales, puedes modificar la constante `ARCHIVO_DATOS` en `control_horas.py` o introducir una variable de entorno (por ejemplo, `HISTORIAL_PATH`) para apuntar a otra ubicación.
  4. Para automatizar backups, crea un script sencillo `scripts/backup.sh` o `scripts/backup.bat`.

Configuración rápida y parámetros
--------------------------------
- Jornada base por defecto:
  - horas: definidas por `HORAS_BASE` (valor por defecto: 7)
  - minutos: definidas por `MINUTOS_BASE` (valor por defecto: 45)
  Cambia estos valores editando `control_horas.py` en las constantes al inicio del archivo.

Ejemplos de uso
---------------
- Registrar la jornada de hoy con 8h 0m:
  1. Ejecuta `python3 control_horas.py`
  2. Selecciona opción `1`
  3. Presiona Enter para aceptar la fecha por defecto (hoy)
  4. Introduce `8` para horas y `0` para minutos
  5. Verás el mensaje de confirmación y la diferencia diaria

- Ver últimos registros:
  1. Ejecuta `python3 control_horas.py`
  2. Selecciona opción `2`

Buenas prácticas
----------------
- Mantén `historial_horas.json` fuera del control de versiones si contiene datos personales o locales (añádelo al `.gitignore`) o añade una muestra de ejemplo en `examples/` en lugar del archivo real.
- Haz backups antes de realizar cambios masivos o limpieza del historial.
- Considera añadir argumentos de línea de comandos y/o soporte para variables de entorno para mayor flexibilidad.

Preguntas frecuentes (FAQ)
--------------------------
P: ¿Puedo cambiar la ubicación del archivo de historial?
R: Sí. Modifica la constante `ARCHIVO_DATOS` en `control_horas.py` o extiende el script para leer una variable de entorno `HISTORIAL_PATH`.

P: ¿El script usa librerías externas?
R: No, actualmente usa solo la biblioteca estándar de Python.

P: ¿Qué versión de Python necesito?
R: Python 3.8 o superior es recomendado.

Contribuciones y mejoras propuestas
----------------------------------
- Añadir `examples/historial_horas.json` con datos de ejemplo.
- Añadir un pequeño `requirements.txt` vacío o con notas si en el futuro hay dependencias.
- Añadir una opción CLI para exportar/importar CSV y para cambiar la ruta del archivo de datos vía argumento o variable de entorno.
- Añadir pruebas unitarias básicas para las funciones de cálculo (p. ej. `formatear_tiempo`, `calcular_saldo_total`).

Licencia
--------
Añade la licencia que prefieras (por ejemplo MIT). Si quieres, puedo preparar un archivo `LICENSE` con texto MIT.

Contacto
--------
Incluye tu nombre o correo si quieres recibir contribuciones o reportes de errores.
