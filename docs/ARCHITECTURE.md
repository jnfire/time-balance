# Arquitectura del Proyecto

## Visión General

`time-balance` es una aplicación Python simplificada para registrar jornadas laborales y calcular saldos acumulados. Utiliza un enfoque mínimalista con almacenamiento en JSON y una interfaz interactiva de menú.

## Estructura del Proyecto

```
time-balance/
├── time_balance/              # Paquete principal
│   └── __init__.py           # Módulo principal con toda la lógica
├── tests/                    # Suite de tests
│   ├── test_control_horas.py
│   └── test_import_export.py
├── docs/                     # Documentación (nuevo)
│   ├── CLI-GUIDE.md
│   ├── API-GUIDE.md
│   ├── ARCHITECTURE.md       # Este archivo
│   └── CONTRIBUTING.md
├── examples/                 # Archivos de ejemplo
│   └── historial_horas.json
├── README.md                 # Documentación principal
├── CHANGELOG.md              # Historial de cambios
├── pyproject.toml            # Metadatos y configuración
├── setup.py                  # Configuración setuptools
├── historial_horas.json      # Archivo de datos (generado en runtime)
└── .gitignore
```

## Módulos y Componentes

### `time_balance/__init__.py` (módulo principal)

Contiene toda la lógica de la aplicación:

#### 1. **Resolución de Rutas**
- `_resolver_archivo(archivo_path=None)`: Implementa la lógica de prioridades para encontrar el archivo de datos
  - Prioridad 1: Parámetro `archivo_path`
  - Prioridad 2: Variable de entorno `HISTORIAL_PATH`
  - Prioridad 3: `historial_horas.json` en directorio actual

#### 2. **I/O Segura**
- `cargar_datos(archivo_path=None)`: Carga JSON con manejo seguro de errores
- `guardar_datos(datos, archivo_path=None)`: Escritura atómica usando `tempfile` + `os.replace()`
- `_crear_backup(archivo_path)`: Crea backups con timestamp e histórico

#### 3. **Lógica de Negocio**
- `formatear_tiempo(minutos_totales)`: Convierte minutos a formato legible
- `calcular_saldo_total(datos)`: Suma diferencias diarias
- `registrar_jornada(datos, archivo_path=None)`: Interfaz interactiva para registrar horas
- `solicitar_fecha()`: Valida entrada de fecha con YYYY-MM-DD
- `ver_historial(datos)`: Muestra últimos 5 registros

#### 4. **Import/Export**
- `exportar_historial(ruta_destino, archivo_path=None)`: Copia a JSON externo
- `importar_historial(ruta_fuente, modo='merge', archivo_path=None)`: Importa y valida
- `_validar_historial(datos)`: Valida estructura JSON importada

#### 5. **Punto de Entrada**
- `main()`: Loop interactivo del menú principal

## Flujo de Datos

### Diagrama de Flujo General

```
┌─────────────────────────────────────────────────────────────┐
│                    main() - Loop Interactivo                │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
                    ▼         ▼         ▼
            ┌──────────┐ ┌────────┐ ┌──────────┐
            │ Registrar│ │  Ver   │ │Exportar/I│
            │ Jornada  │ │Histor. │ │ mportar  │
            └──────────┘ └────────┘ └──────────┘
                    │         │         │
                    └─────────┼─────────┘
                              │
                    ┌─────────▼──────────┐
                    │ cargar/guardar_datos│
                    │   (JSON I/O)       │
                    └────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │ historial_horas.json│
                    └────────────────────┘
```

### Flujo de Registrar Jornada

```
registrar_jornada()
    ├─ solicitar_fecha()           → Validar YYYY-MM-DD
    ├─ input horas/minutos         → Convertir a int
    ├─ Verificar si existe
    │  └─ Si existe → Pedir confirmación
    ├─ Calcular diferencia
    │  └─ diferencia = (horas*60 + minutos) - 465 (base)
    ├─ Guardar en memoria
    ├─ guardar_datos()
    │  ├─ Crear archivo temporal
    │  ├─ Escribir JSON
    │  ├─ os.replace() - operación atómica
    │  └─ Limpiar temporales
    └─ Retornar a menú
```

### Flujo de Importación

```
importar_historial(ruta_fuente, modo='merge'|'overwrite')
    ├─ Cargar JSON desde ruta_fuente
    ├─ _validar_historial() → Validar estructura
    │  └─ Si inválido → Lanzar ValueError
    │
    ├─ Si modo='merge'
    │  ├─ Combinar: datos_local.update(datos_importados)
    │  └─ Los importados ganan en conflictos
    │
    ├─ Si modo='overwrite'
    │  ├─ _crear_backup(archivo_actual)
    │  │  ├─ Copiar a archivo_path.bak
    │  │  └─ Copiar a archivo_path.bak.20260416T111320
    │  └─ Reemplazar completamente
    │
    ├─ guardar_datos(resultado)
    └─ Retornar datos actualizado
```

## Características de Confiabilidad

### 1. **Escritura Atómica**

```python
# Implementación en guardar_datos()
fd, tmp_path = tempfile.mkstemp()
with open(fd, 'w') as f:
    json.dump(datos, f)
os.replace(tmp_path, archivo_datos)  # Operación atómica
```

Beneficios:
- Si el proceso se interrumpe durante la escritura, el archivo original permanece intacto
- No hay riesgo de corrupción de datos
- Funciona entre filesystems

### 2. **Backups Automáticos**

```
historial_horas.json              (archivo principal)
historial_horas.json.bak          (último backup)
historial_horas.json.bak.20260416T111320  (backup versionado)
```

- Se crean antes de operaciones destructivas (overwrite)
- Timestamp ISO 8601 para orden cronológico
- El archivo `.bak` se actualiza siempre con el más reciente

### 3. **Validación de Datos**

```python
def _validar_historial(datos):
    # Validar tipo dict
    # Validar todas las claves YYYY-MM-DD
    # Validar estructura: horas, minutos, diferencia como int/float
    # Lanzar ValueError con mensaje específico si algo falla
```

### 4. **Manejo de Errores Resiliente**

- JSON corrupto: `cargar_datos()` retorna `{}` vacío
- Archivo faltante: Se crea uno nuevo en primera escritura
- Entrada inválida: Bucles de reintentos en entrada interactiva
- Rutas inválidas: Errores claros y permitir reintentar

## Configuración

### Constantes

```python
HORAS_BASE = 7          # Horas en jornada base
MINUTOS_BASE = 45       # Minutos adicionales en jornada base
ARCHIVO_DATOS = "historial_horas.json"  # Nombre por defecto
ENV_HISTORIAL = "HISTORIAL_PATH"        # Variable de entorno
```

La jornada base es: **7 horas 45 minutos = 465 minutos**

### Variables de Entorno

```bash
# Ubicación personalizada del historial
export HISTORIAL_PATH="/home/usuario/.local/share/time-balance/historial.json"
time-balance
```

## Testing

### Estrategia de Testing

- **Aislamiento**: Cada test usa `tempfile.TemporaryDirectory()`
- **No toca archivos reales**: El repositorio `historial_horas.json` nunca se modifica
- **Cobertura**: I/O, validación, cálculos, import/export, backups

### Test Files

- `tests/test_control_horas.py`: Tests de lógica principal (10 tests)
- `tests/test_import_export.py`: Tests de import/export (4 tests)

Ejecución:
```bash
python3 -m unittest discover -v
```

## Dependencias

### Dependencias Incluidas en Python Estándar

- `os`: Operaciones de filesystem, variables de entorno
- `json`: Serialización/deserialización JSON
- `datetime`: Manejo de fechas
- `tempfile`: Archivos temporales para escritura segura
- `shutil`: Copia de archivos con metadatos

### Dependencias de Desarrollo

- `unittest`: Testing (incorporado en Python)

**No hay dependencias externas**. `time-balance` es 100% pure Python con biblioteca estándar.

## Decisiones de Diseño

### 1. **Almacenamiento en JSON en vez de Database**

✅ Ventajas:
- Portable, human-readable, fácil de respaldar
- No requiere daemon o configuración extra
- Fácil de sincronizar entre máquinas

### 2. **Interfaz Interactiva (menú) en vez de Subcomandos**

✅ Ventajas:
- Previene errores de usuario (menú clara)
- No requiere memorizar comandos
- Más accesible para usuarios no técnicos

### 3. **Operaciones Atómicas en Escritura**

✅ Ventajas:
- Garantiza integridad de datos
- Resistente a fallos de energía
- Seguro para ejecución concurrente

### 4. **Validación Rigurosa en Import**

✅ Ventajas:
- Previene datos corrupto
- Errores específicos y claros
- Fácil depuración

## Extensibilidad Futura

Posibles mejoras sin romper compatibilidad:

1. **Soporte para XDG Base Directory** (`~/.local/share/time-balance/`)
2. **Exportación a formatos adicionales** (CSV, Excel)
3. **Estadísticas y reportes** (semanal, mensual)
4. **Sincronización en la nube**
5. **Integración con calendar/agenda**
6. **Notificaciones/reminders**

## Performance

- **Carga de datos**: O(1) - lectura simple de JSON
- **Guardar datos**: O(n) - serialización JSON lineal
- **Cálculo de saldo**: O(n) - suma de diferencias
- **Displayar historial**: O(1) - últimos 5 registros (constante)

Esperado para < 10,000 registros sin degradación perceptible.

## Seguridad

- **Datos locales**: Almacenados en archivo JSON accesible (usuario responsable de permisos)
- **Sin autenticación**: Diseño local-first
- **Sin networking**: No hay conexiones remotas por defecto
- **Validación estricta**: Rechaza JSON malformados

Se recomienda:
- Usar permisos de archivo restrictivos (`chmod 600`) si es crítico
- Hacer backups regulares
- Si es necesario sincronizar, usar herramientas seguras (rsync, Syncthing, etc.)
