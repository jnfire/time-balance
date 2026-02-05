# time-balance

Descripción
-----------
`time-balance` es una pequeña herramienta de consola en Python para registrar jornadas laborales diarias y calcular el saldo acumulado respecto a una jornada base. Guarda un historial simple en formato JSON (`historial_horas.json`) y muestra los últimos registros y el saldo acumulado.

Características principales
-------------------------
- Registro interactivo de horas y minutos por día.
- Prevención de sobrescritura con confirmación del usuario (en la UI interactiva).
- Cálculo de la diferencia diaria respecto a una jornada base configurable.
- Visualización de los últimos registros y del saldo total.
- Funcionalidades de import/export para respaldar o restaurar datos fuera del equipo.

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

4. Instala el paquete localmente (recomendado para tener el comando global):

```bash
# En la raíz del proyecto
python3 -m pip install -e .
```

Esto instalará el console script `time-balance` en el entorno y también respeta el archivo `pyproject.toml` / `setup.py` si quieres construir el paquete.

Uso (recomendado)
------------------
Tras la instalación lo recomendado es usar el comando `time-balance` desde la terminal.

- Modo interactivo (menu):

```bash
# ejecuta la UI interactiva
time-balance
```

- Exportar historial:

```bash
# Exporta el historial actual al archivo indicado
time-balance export /ruta/a/mi_export.json
```

- Importar historial:

```bash
# Importa desde un JSON; default: merge (la entrada importada sobrescribe en caso de conflicto)
# IMPORTANTE: la entrada importada tiene preferencia sobre lo que ya estaba guardado
time-balance import /ruta/mi_historial.json --mode merge

# Importar y reemplazar totalmente el historial (se crea backup antes)
time-balance import /ruta/mi_historial.json --mode overwrite
```

Compatibilidad con el script original
-------------------------------------
El repositorio mantiene `control_horas.py` como un shim/compatibilidad que reexporta la API del paquete `time_balance`. Si prefieres ejecutar el script directamente sin instalar, todavía puedes hacerlo:

```bash
python3 control_horas.py
```

pero la forma recomendada tras empaquetar es usar `time-balance`.

Archivos y configuración
------------------------
- `historial_horas.json`: archivo JSON por defecto en el directorio de trabajo.
- Resolución de la ruta del archivo de datos (prioridad):
  1. Argumento `archivo_path` en las funciones de la API
  2. Variable de entorno `HISTORIAL_PATH`
  3. `historial_horas.json` en el directorio actual (comportamiento por defecto)

- Backups: en operaciones destructivas (`overwrite` o `merge`) se crea un backup con timestamp `historial_horas.json.bak.YYYYMMDDTHHMMSS` y se actualiza `historial_horas.json.bak` con la última versión previa.
- Escrituras seguras: todas las escrituras son atómicas (se escribe a un archivo temporal y se realiza `os.replace`).

Uso programático (API)
----------------------
Las funciones públicas más relevantes (importables desde `time_balance` o desde `control_horas` por compatibilidad) son:

- `cargar_datos(archivo_path=None)`
- `guardar_datos(datos, archivo_path=None)`
- `exportar_historial(ruta_destino, archivo_path=None)`
- `importar_historial(ruta_fuente, modo='merge'|'overwrite', archivo_path=None)`
- `main()` — entry point CLI/UI

Nota sobre import: en modo `merge` la entrada importada sobrescribe los registros en conflicto (la importación tiene preferencia sobre lo guardado localmente).

Compatibilidad removida:
- Ya no se incluye el shim `control_horas.py`. Importa directamente desde el paquete `time_balance` si necesitas usar la API desde scripts o tests. Por ejemplo:

```py
import time_balance as tb
# usar tb.cargar_datos(), tb.guardar_datos(), tb.main(), etc.
```


Tests
-----
La suite de tests se puede ejecutar con:

```bash
python3 -m unittest discover -v
```

Los tests actuales han sido diseñados para no tocar el `historial_horas.json` del repositorio: cada test se ejecuta en un directorio temporal y los tests de import/export comprueban la creación de backups, el comportamiento `merge` (importado gana) y `overwrite`.

Contribuciones y mejoras propuestas
----------------------------------
- Añadir `examples/historial_horas.json` con datos de ejemplo.
- Reconocer una ubicación por defecto XDG para instalaciones globales (p. ej. `~/.local/share/time-balance/`) como opción futura.
- Añadir CI que ejecute los tests en Linux/macOS/Windows.

Licencia
--------
Añade la licencia que prefieras (por ejemplo MIT). Si quieres, puedo preparar un archivo `LICENSE` con texto MIT.

Contacto
--------
Incluye tu nombre o correo si quieres recibir contribuciones o reportes de errores.
