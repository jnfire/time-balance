# Guía de API: Uso Programático

La librería `time-balance` está diseñada siguiendo una arquitectura modular que separa la lógica de negocio (Core) de los servicios de infraestructura (Storage/IO) y la interfaz de usuario (CLI).

## Instalación para Desarrollo

```bash
# En la carpeta del proyecto
python3 -m pip install -e .
```

## Estructura de Importación

Aunque todas las funciones principales están disponibles en el espacio de nombres principal, la API se organiza lógicamente en cuatro pilares:

```python
import time_balance as ch

# 1. Lógica de Negocio (Core)
# ch.formatear_tiempo, ch.calcular_saldo_total

# 2. Persistencia (Storage)
# ch.cargar_datos, ch.guardar_datos

# 3. Intercambio de Datos (IO)
# ch.exportar_historial, ch.importar_historial

# 4. Constantes de Configuración
# ch.HORAS_BASE, ch.MODE_MERGE, etc.
```

---

## 1. Core API (Lógica de Negocio)

Representa el corazón del sistema. Estas funciones son puras y se encargan de las reglas de cálculo y representación.

### `formatear_tiempo(minutos_totales)`
Convierte minutos a formato legible (ej: "2h 5m").

**Ejemplo:**
```python
from time_balance import formatear_tiempo
print(formatear_tiempo(125))  # "2h 5m"
print(formatear_tiempo(-75))  # "-1h 15m"
```

### `calcular_saldo_total(datos)`
Suma todas las diferencias diarias para obtener el saldo acumulado.

**Ejemplo:**
```python
from time_balance import calcular_saldo_total
saldo = calcular_saldo_total(datos)
print(f"Saldo total: {saldo} minutos")
```

---

## 2. Persistence API (Almacenamiento)

Gestiona la lectura y escritura del historial en disco garantizando la integridad de los datos.

### `cargar_datos(archivo_path=None)`
Carga el historial de horas desde un archivo JSON.
- **`archivo_path`**: Opcional. Si es `None`, usa la resolución de prioridades (ENV > Default).

### `guardar_datos(datos, archivo_path=None)`
Guarda el historial de forma segura mediante **escritura atómica** (crash-safe).

**Ejemplo de flujo de persistencia:**
```python
from time_balance import cargar_datos, guardar_datos

datos = cargar_datos()
# ... modificar datos ...
guardar_datos(datos)
```

---

## 3. Data Exchange API (Import/Export)

Funciones para mover datos entre el sistema y archivos externos con validación rigurosa.

### `exportar_historial(ruta_destino, archivo_path=None)`
Exporta el historial completo a un JSON externo.

### `importar_historial(ruta_fuente, modo=MODE_MERGE, archivo_path=None)`
Importa historial validando su estructura.
- **Modos**: `MODE_MERGE` (combina) o `MODE_OVERWRITE` (reemplaza con backup).

**Ejemplo de Importación:**
```python
from time_balance import importar_historial, MODE_MERGE

try:
    datos = importar_historial("~/backup.json", modo=MODE_MERGE)
    print("✓ Datos sincronizados")
except ValueError as e:
    print(f"Error de validación: {e}")
```

---

## 4. Interactive API (CLI)

Estas funciones están diseñadas para su uso en scripts interactivos, ya que solicitan entrada o imprimen en pantalla.

- `registrar_jornada(datos, archivo_path=None)`: Inicia el flujo de entrada de horas por consola.
- `ver_historial(datos)`: Imprime una tabla con los últimos 5 registros.
- `solicitar_fecha()`: Función interactiva para validar fechas introducidas por el usuario.

---

## Constantes y Configuración

Centraliza la configuración del sistema para evitar "magic strings".

| Constante | Valor por defecto | Descripción |
|-----------|-------------------|-------------|
| `HORAS_BASE` | `7` | Horas de la jornada base |
| `MINUTOS_BASE` | `45` | Minutos de la jornada base |
| `ARCHIVO_DATOS` | `"historial_horas.json"` | Archivo por defecto |
| `MODE_MERGE` | `"merge"` | Modo de importación por mezcla |
| `MODE_OVERWRITE` | `"overwrite"` | Modo de importación por reemplazo |

---

## Estructura de Datos (Esquema JSON)

El historial se representa como un diccionario donde la clave es la fecha (`YYYY-MM-DD`) y el valor es un objeto con la jornada:

```python
{
    "2026-04-19": {
        "horas": 8,           # int: horas reales
        "minutos": 0,         # int: minutos reales
        "diferencia": 15      # int: balance vs jornada base (465m)
    }
}
```
