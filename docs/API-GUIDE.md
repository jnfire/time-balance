# Guía de API: Uso Programático

La librería `time-balance` expone una API pública para integrar la funcionalidad de registro de horas en tus propias aplicaciones Python.

## Instalación para Desarrollo

```bash
# En la carpeta del proyecto
python3 -m pip install -e .
```

## Importación

```python
from time_balance import (
    cargar_datos,
    guardar_datos,
    exportar_historial,
    importar_historial,
    registrar_jornada,
    ver_historial,
    formatear_tiempo,
    calcular_saldo_total,
)
```

## Funciones Principales

### 1. `cargar_datos(archivo_path=None)`

Carga el historial de horas desde un archivo JSON.

**Parámetros:**
- `archivo_path` (str, optional): Ruta al archivo JSON. Si es `None`, usa la resolución de prioridades (env var → archivo por defecto).

**Retorna:**
- `dict`: Diccionario con estructura `{fecha: {horas, minutos, diferencia}}`, o `{}` si el archivo no existe o está corrupto.

**Ejemplo:**

```python
datos = cargar_datos()
print(datos)
# {'2026-04-16': {'horas': 8, 'minutos': 30, 'diferencia': 45},
#  '2026-04-15': {'horas': 7, 'minutos': 45, 'diferencia': 0}}
```

### 2. `guardar_datos(datos, archivo_path=None)`

Guarda el historial en un archivo JSON de forma segura (operación atómica).

**Parámetros:**
- `datos` (dict): Diccionario del historial con estructura `{fecha: {horas, minutos, diferencia}}`.
- `archivo_path` (str, optional): Ruta donde guardar. Si es `None`, usa resolución de prioridades.

**Retorna:**
- `dict`: El mismo diccionario `datos` pasado como argumento.

**Características de seguridad:**
- Escribe a archivo temporal primero
- Usa `os.replace()` para reemplazo atómico (crash-safe)
- Si algo falla a mitad de la escritura, el archivo original permanece intacto

**Ejemplo:**

```python
datos = {
    '2026-04-16': {'horas': 8, 'minutos': 30, 'diferencia': 45},
    '2026-04-15': {'horas': 7, 'minutos': 45, 'diferencia': 0}
}
guardar_datos(datos)
print("✓ Datos guardados")
```

### 3. `formatear_tiempo(minutos_totales)`

Convierte minutos a formato legible (ej: "2h 5m").

**Parámetros:**
- `minutos_totales` (int): Cantidad de minutos (puede ser positivo o negativo).

**Retorna:**
- `str`: Formato legible; los valores negativos incluyen prefijo `-`, los positivos no incluyen `+`. Ej: `"2h 5m"`, `"-1h 15m"`, `"0h 0m"`.

**Ejemplo:**

```python
print(formatear_tiempo(125))      # "2h 5m"
print(formatear_tiempo(-75))      # "-1h 15m"
print(formatear_tiempo(0))        # "0h 0m"
print(formatear_tiempo(465))      # "7h 45m"
```

### 4. `calcular_saldo_total(datos)`

Suma todas las diferencias diarias para obtener el saldo acumulado.

**Parámetros:**
- `datos` (dict): Diccionario del historial con estructura `{fecha: {..., diferencia}}`.

**Retorna:**
- `int`: Saldo total en minutos (puede ser positivo o negativo).

**Ejemplo:**

```python
datos = {
    '2026-04-16': {'horas': 8, 'minutos': 30, 'diferencia': 45},
    '2026-04-15': {'horas': 7, 'minutos': 45, 'diferencia': 0},
    '2026-04-14': {'horas': 6, 'minutos': 30, 'diferencia': -75}
}
saldo = calcular_saldo_total(datos)
print(saldo)                      # -30 (minutos)
print(formatear_tiempo(saldo))   # "-0h 30m"
```

### 5. `exportar_historial(ruta_destino, archivo_path=None)`

Exporta el historial completo a un archivo JSON externo.

**Parámetros:**
- `ruta_destino` (str): Ruta donde crear el archivo de exportación. Soporta `~` (home directory).
- `archivo_path` (str, optional): Ruta del archivo de datos a exportar (usa resolución de prioridades si es `None`).

**Retorna:**
- `str`: Ruta absoluta del archivo creado.

**Excepciones:**
- Puede lanzar excepciones de I/O si la ruta de destino no es válida.

**Ejemplo:**

```python
try:
    ruta = exportar_historial("~/backups/mi_export.json")
    print(f"✓ Exportado a: {ruta}")
except Exception as e:
    print(f"Error: {e}")
```

### 6. `importar_historial(ruta_fuente, modo='merge', archivo_path=None)`

Importa historial desde un archivo JSON externo.

**Parámetros:**
- `ruta_fuente` (str): Ruta del archivo a importar. Soporta `~` (home directory).
- `modo` (str): Tipo de importación:
  - `'merge'` (predeterminado): Combina datos; los importados sobrescriben conflictos.
  - `'overwrite'`: Reemplaza todo el historial (crea backup antes).
- `archivo_path` (str, optional): Ruta del archivo de datos (usa resolución de prioridades si es `None`).

**Retorna:**
- `dict`: El historial actualizado con la estructura `{fecha: {horas, minutos, diferencia}}`.

**Backups en modo `overwrite`:**
- Se crea `historial_horas.json.bak` (último backup)
- Se crea `historial_horas.json.bak.20260416T111320` (versión con timestamp)

**Validación:**
- Valida que el JSON importado tenga estructura correcta
- Lanza `ValueError` si la estructura es inválida

**Ejemplo - Modo Merge:**

```python
# Importar y combinar
datos = importar_historial("~/export.json", modo="merge")
print(f"✓ Importados {len(datos)} registros")
```

**Ejemplo - Modo Overwrite:**

```python
# Importar y reemplazar (con backup automático)
try:
    datos = importar_historial("~/backup_completo.json", modo="overwrite")
    print("✓ Historial restaurado completamente")
except ValueError as e:
    print(f"Error de validación: {e}")
```

## Gestión de Archivos

### Resolución de Rutas

La mayoría de funciones usan un sistema de resolución de rutas con 3 niveles de prioridad:

1. **Argumento `archivo_path`** en la función
2. **Variable de entorno `HISTORIAL_PATH`**
3. **Archivo por defecto** `historial_horas.json` en el directorio actual

```python
import os

# Establecer ubicación personalizada para el historial
os.environ["HISTORIAL_PATH"] = "/home/usuario/.local/share/time-balance/historial.json"

# Ahora todas las funciones usan esta ubicación
datos = cargar_datos()
```

### Backups Automáticos

Los backups se crean automáticamente en modo `overwrite` durante importación:

- **Simple backup**: `historial_horas.json.bak` (siempre es el más reciente)
- **Versionado**: `historial_horas.json.bak.20260416T111320` (con timestamp ISO)

```python
# Después de un importar con overwrite, tienes ambos archivos
# En caso de error, puedes restaurar desde el backup
```

## Ejemplos Prácticos

### Ejemplo 1: Automatizar Registro Diario

```python
from datetime import date
from time_balance import cargar_datos, guardar_datos

# Cargar datos existentes
datos = cargar_datos()

# Registrar hoy
hoy = str(date.today())  # "2026-04-16"
datos[hoy] = {
    'horas': 8,
    'minutos': 15,
    'diferencia': 45  # minutos
}

# Guardar
guardar_datos(datos)
print(f"✓ Registrado {hoy}")
```

### Ejemplo 2: Generar Reporte

```python
from time_balance import (
    cargar_datos,
    calcular_saldo_total,
    formatear_tiempo,
)

datos = cargar_datos()
saldo = calcular_saldo_total(datos)

print("=== REPORTE DE HORAS ===")
print(f"Registros totales: {len(datos)}")
print(f"Saldo acumulado: {formatear_tiempo(saldo)}")

# Mostrar últimos 5
for fecha in sorted(datos.keys(), reverse=True)[:5]:
    h = datos[fecha]['horas']
    m = datos[fecha]['minutos']
    diff = datos[fecha]['diferencia']
    print(f"  {fecha}: {h}h {m}m (diff: {formatear_tiempo(diff)})")
```

### Ejemplo 3: Sincronización entre Máquinas

```python
import os
from time_balance import exportar_historial, importar_historial

# Máquina 1: Exportar
print("Exportando desde máquina 1...")
ruta = exportar_historial("~/Dropbox/time-balance-sync.json")
print(f"✓ Exportado a: {ruta}")

# Máquina 2: Importar y combinar
print("Importando en máquina 2...")
datos = importar_historial("~/Dropbox/time-balance-sync.json", modo="merge")
print(f"✓ Sincronizados {len(datos)} registros")
```

### Ejemplo 4: Integración con Script Cron

```bash
#!/bin/bash
# script: registrar_horas_cron.sh
# Ejecutar diariamente con cron para recordar registrar horas

python3 << 'EOF'
import os
from datetime import date
from time_balance import cargar_datos, guardar_datos

# Verificar si ya está registrado hoy
datos = cargar_datos()
hoy = str(date.today())

if hoy not in datos:
    print(f"Recordatorio: Falta registrar horas para {hoy}")
    # Podría enviar notificación, email, etc.
else:
    print(f"✓ {hoy} ya está registrado")
EOF
```

## Constantes de Configuración

Desde el módulo puedes acceder a estas constantes:

```python
from time_balance import HORAS_BASE, MINUTOS_BASE, ARCHIVO_DATOS, ENV_HISTORIAL

print(HORAS_BASE)         # 7
print(MINUTOS_BASE)       # 45
print(ARCHIVO_DATOS)      # "historial_horas.json"
print(ENV_HISTORIAL)      # "HISTORIAL_PATH"
```

## Estructura de Datos

### Formato del Historial

```python
{
    "2026-04-16": {
        "horas": 8,           # int: horas trabajadas
        "minutos": 30,        # int: minutos trabajados
        "diferencia": 45      # int: minutos respecto a base (7h 45m = 465 minutos)
    },
    "2026-04-15": {
        "horas": 7,
        "minutos": 45,
        "diferencia": 0
    }
}
```

- **horas**: Entero, rango típico 0-12
- **minutos**: Entero, rango 0-59
- **diferencia**: Float, diferencia en minutos respecto a jornada base (465 minutos)
  - Positivo: más horas que la base
  - Negativo: menos horas que la base
  - Cero: exactamente la jornada base

## Manejo de Errores

```python
from time_balance import importar_historial

try:
    datos = importar_historial("archivo_inexistente.json")
except FileNotFoundError:
    print("Archivo no encontrado")
except ValueError as e:
    print(f"JSON inválido: {e}")
except Exception as e:
    print(f"Error inesperado: {e}")
```

Errores comunes:
- `FileNotFoundError`: Archivo a importar no existe
- `ValueError`: JSON tiene estructura incorrecta
- `json.JSONDecodeError`: JSON malformado (se captura y retorna dict vacío en `cargar_datos`)

## Testing

Si deseas usar la API en tests:

```python
import tempfile
import os
from time_balance import cargar_datos, guardar_datos

# Usar directorio temporal para tests
with tempfile.TemporaryDirectory() as tmpdir:
    archivo_test = os.path.join(tmpdir, "test_historial.json")
    
    # Usar archivo de prueba específico
    datos_test = {"2026-04-16": {"horas": 8, "minutos": 0, "diferencia": 15}}
    guardar_datos(datos_test, archivo_path=archivo_test)
    
    # Verificar
    datos_cargados = cargar_datos(archivo_path=archivo_test)
    assert datos_cargados == datos_test
```
