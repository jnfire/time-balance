# time-balance

> Una pequeña herramienta de consola en Python para registrar jornadas laborales y calcular saldos acumulados.

## Tabla de Contenidos

- [Descripción](#descripción)
- [Características](#características-principales)
- [Instalación](#instalación)
- [Uso](#uso)
- [Documentación](#documentación)
- [Requisitos](#requisitos)
- [Licencia](#licencia)

## Descripción

`time-balance` es una herramienta de consola minimalista para registrar jornadas laborales diarias y calcular el saldo acumulado respecto a una jornada base (7h 45m por defecto). 

Guarda un historial simple en formato JSON (`historial_horas.json`), es **100% Python con biblioteca estándar** (sin dependencias externas), y proporciona tanto una interfaz interactiva como una API programática.

## Características Principales

- ✅ **Registro interactivo** de horas y minutos por día
- ✅ **Prevención de sobrescritura** con confirmación del usuario
- ✅ **Cálculo automático** de la diferencia diaria respecto a jornada base
- ✅ **Visualización clara** de últimos registros y saldo total
- ✅ **Import/Export** para respaldar o restaurar datos
- ✅ **Escritura segura** (operaciones atómicas, crash-safe)
- ✅ **Backups automáticos** con versionamiento por timestamp
- ✅ **Validación rigurosa** de datos importados
- ✅ **100% portátil** - macOS, Linux, Windows

## Requisitos

- **Python 3.8+** (solo usa módulos de la biblioteca estándar: `os`, `json`, `datetime`, `tempfile`, `shutil`)
- **Sistema operativo**: macOS / Linux / Windows

## Instalación

### 1. Clonar el Repositorio

```bash
git clone <url-del-repo>
cd time-balance
```

### 2. Crear Entorno Virtual (Opcional)

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS / Linux (zsh / bash)
.venv\Scripts\activate      # Windows (cmd/PowerShell)
```

### 3. Instalar el Paquete

```bash
# En la raíz del proyecto
python3 -m pip install -e .
```

Esto instalará el console script `time-balance` en el entorno. Si `pyproject.toml` / `setup.py` especifican requisitos, también se instalarán.

## Uso

### Interfaz Interactiva (Recomendado)

Tras la instalación, ejecuta desde la terminal:

```bash
time-balance
```

Se mostrará un menú interactivo:

```
==================================================
   SALDO TOTAL ACUMULADO: 0h 15m
   (Base diaria: 7h 45m)
==================================================

Opciones:
1. Registrar jornada (o corregir día)
2. Ver últimos registros
3. Exportar historial a archivo
4. Importar historial desde archivo
5. Salir

Elige opción: _
```

**Opción 1: Registrar Jornada**

```
Ingresa fecha (YYYY-MM-DD) o presiona Enter para hoy [2026-04-16]: 
Ingresa horas trabajadas: 8
Ingresa minutos trabajados: 30
✓ Jornada registrada
```

**Opción 2: Ver Últimos Registros**

Muestra los 5 registros más recientes con saldo diario.

**Opción 3: Exportar Historial**

```
Ingresa ruta de destino para exportar: ~/backup/mi_export.json
✓ Historial exportado a: /Users/usuario/backup/mi_export.json
```

**Opción 4: Importar Historial**

```
Ingresa ruta de origen para importar: ~/backup/mi_export.json
Elige modo de importación (merge/overwrite) [merge]: merge
✓ Historial importado: 5 entradas procesadas
```

- **`merge`** (predeterminado): Combina datos; importados ganan en conflictos
- **`overwrite`**: Reemplaza completamente (crea backup antes)

**Opción 5: Salir**

```
¡Hasta mañana!
```

Para más detalles sobre el CLI interactivo, consulta la [Guía de CLI](docs/CLI-GUIDE.md).

## Documentación

La documentación completa está organizada en la carpeta `docs/`:

| Documento | Propósito |
|-----------|-----------|
| [**CLI-GUIDE.md**](docs/CLI-GUIDE.md) | Guía detallada de la interfaz interactiva |
| [**API-GUIDE.md**](docs/API-GUIDE.md) | Referencia de API para uso programático en Python |
| [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) | Diseño interno, flujos de datos, decisiones de arquitectura |
| [**CONTRIBUTING.md**](docs/CONTRIBUTING.md) | Guía para contribuidores |

### Acceso Rápido

- ¿Cómo uso la herramienta? → [CLI-GUIDE.md](docs/CLI-GUIDE.md)
- ¿Cómo integro en mi código Python? → [API-GUIDE.md](docs/API-GUIDE.md)
- ¿Cómo está organizado internamente? → [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- ¿Cómo contribuyo? → [CONTRIBUTING.md](docs/CONTRIBUTING.md)

## Archivos y Configuración

### Archivo de Datos

El historial se guarda en **`historial_horas.json`** en el directorio actual (por defecto).

Ejemplo de contenido:

```json
{
    "2026-04-16": {
        "horas": 8,
        "minutos": 30,
        "diferencia": 45
    },
    "2026-04-15": {
        "horas": 7,
        "minutos": 45,
        "diferencia": 0
    }
}
```

### Resolución de Rutas

La ubicación del archivo se resuelve con **3 niveles de prioridad**:

1. **Argumento `archivo_path`** en funciones de la API (cuando se usan programáticamente)
2. **Variable de entorno `HISTORIAL_PATH`** (si está definida)
3. **`historial_horas.json`** en el directorio actual (comportamiento por defecto)

**Ejemplo con variable de entorno:**

```bash
export HISTORIAL_PATH=~/.local/share/time-balance/historial_horas.json
time-balance
```

### Backups Automáticos

Las operaciones destructivas crean backups automáticos:

- **`historial_horas.json.bak`** — Último backup (siempre actualizado)
- **`historial_horas.json.bak.20260416T111320`** — Backup versionado con timestamp ISO

Se generan durante operaciones `overwrite` para permitir recuperación en caso de error.

### Escrituras Seguras

Todas las escrituras son **atómicas** (crash-safe):
- Se escribe a archivo temporal primero
- Se realiza reemplazo atómico (`os.replace()`)
- Si se interrumpe el proceso, el archivo original permanece intacto

## Uso Programático (API)

Para integrar `time-balance` en tu código Python:

```python
from time_balance import cargar_datos, guardar_datos, formatear_tiempo, calcular_saldo_total

# Cargar historial
datos = cargar_datos()

# Acceder a datos
saldo = calcular_saldo_total(datos)
print(f"Saldo acumulado: {formatear_tiempo(saldo)}")

# Registrar nuevo día
from datetime import date
hoy = str(date.today())
datos[hoy] = {'horas': 8, 'minutos': 30, 'diferencia': 45}

# Guardar cambios
guardar_datos(datos)
```

### Funciones Disponibles

| Función | Propósito |
|---------|-----------|
| `cargar_datos(archivo_path=None)` | Carga historial desde JSON |
| `guardar_datos(datos, archivo_path=None)` | Guarda historial (atómico) |
| `exportar_historial(ruta_destino, archivo_path=None)` | Exporta a archivo externo |
| `importar_historial(ruta_fuente, modo='merge', archivo_path=None)` | Importa con validación |
| `formatear_tiempo(minutos_totales)` | Convierte minutos a formato legible |
| `calcular_saldo_total(datos)` | Suma diferencias diarias |

Para documentación completa, consulta [API-GUIDE.md](docs/API-GUIDE.md).

## Tests

La suite de tests se ejecuta con:

```bash
python3 -m unittest discover -v
```

**Cobertura:**

- **10 tests** de lógica principal (`tests/test_control_horas.py`)
  - Formateo de tiempo, cálculo de saldo, I/O, detección de duplicados
  
- **4 tests** de import/export (`tests/test_import_export.py`)
  - Exportación, modo merge, modo overwrite, backups, validación

**Características de los tests:**

- ✅ Cada test usa directorio temporal aislado (no toca archivos reales)
- ✅ Validan correctitud de datos, operaciones atómicas, backups
- ✅ Se ejecutan rapidamente (~0.015s)

## Mejoras Propuestas

Posibles extensiones futuras (sin romper compatibilidad):

- Soporte para XDG Base Directory (`~/.local/share/time-balance/`)
- Exportación a CSV / Excel
- Estadísticas y reportes (semanal, mensual, anual)
- Sincronización con servicios en la nube
- Integración con calendarios/agenda
- Notificaciones y recordatorios

## Contribuciones

Si encuentras bugs o tienes ideas de mejora, consulta [CONTRIBUTING.md](docs/CONTRIBUTING.md) para aprender cómo contribuir.

## Licencia

Este proyecto está bajo la licencia [GNU General Public License v3.0 (GPL-3.0)](LICENSE).

El objetivo es fomentar el crecimiento colaborativo y garantizar que todas las mejoras derivadas sigan siendo de código abierto y beneficien a toda la comunidad. No se incentiva la creación de forks privativos.
