# Arquitectura del Proyecto

## Visión General

`time-balance` es una aplicación de terminal para registrar jornadas laborales y gestionar el saldo horario acumulado. En su versión 0.3.0, la aplicación ha evolucionado a una herramienta **global** y **multiproyecto**, utilizando **SQLite** como motor de persistencia siguiendo los estándares XDG para el almacenamiento de datos.

## Estructura del Proyecto

```
time-balance/
├── time_balance/              # Paquete principal
│   ├── __init__.py           # Fachada (reexporta la API pública)
│   ├── __main__.py           # Punto de entrada para ejecución como módulo
│   ├── constants.py          # Configuración de rutas globales y constantes
│   ├── core.py               # Lógica de negocio (formateo, cálculos)
│   ├── storage.py            # Persistencia (SQLite) y DatabaseManager
│   ├── io.py                 # Validación y lectura de archivos externos (JSON)
│   ├── cli.py                # Interfaz de usuario (Menú y Submenús)
│   └── i18n.py               # Sistema de internacionalización
├── tests/                    # Suite de tests modular
│   ├── test_core.py
│   ├── test_storage.py       # Valida transacciones SQLite
│   ├── test_io.py            # Valida lectura de esquemas JSON
│   └── test_cli.py           # Valida menús e interacción
├── docs/                     # Documentación
├── README.md                 # Guía de usuario (Inglés)
└── CHANGELOG.md              # Historial de cambios
```

## Módulos y Componentes

### 1. **`core.py` (Lógica de Negocio)**
Contiene las funciones matemáticas y de formateo independientes de la persistencia.
- `format_time()`: Convierte minutos a formato legible `+/- Xh Ym`.
- `calculate_total_balance()`: Utilizado principalmente en importaciones para validar saldos.

### 2. **`storage.py` (Capa de Persistencia SQLite)**
Implementa la clase `DatabaseManager` que centraliza todas las operaciones SQL.
- **Gestión de Proyectos**: CRUD para múltiples contextos de trabajo.
- **Registros**: Almacenamiento eficiente de jornadas por ID de proyecto.
- **Configuración Global**: Tabla `settings` para recordar el proyecto activo e idioma.
- **Ubicación Estándar**: Uso de `pathlib` para cumplir con XDG (Application Support en macOS, .local/share en Linux).

### 3. **`cli.py` (Capa de Presentación)**
Maneja la interacción con el usuario.
- **Menú Principal**: Operaciones de registro y visualización del proyecto activo.
- **Gestión de Proyectos**: Submenú para crear, cambiar y editar proyectos.
- **Comando de Migración**: Flag `--migrate` para importar datos desde JSON antiguos.

### 4. **`io.py` (Intercambio de Datos)**
Lógica para validar y leer archivos JSON externos.
- `read_history_file()`: Valida esquemas de versiones anteriores (v0.2.x).
- `export_history()`: Genera un volcado JSON del proyecto activo.

### 5. **`i18n.py` (Internacionalización)**
Motor de traducción simple que soporta inglés y español.

## Esquema de Base de Datos (SQLite)

### Tabla `projects`
| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| id | INTEGER PK | Identificador único |
| name | TEXT UNIQUE | Nombre del proyecto |
| base_hours | INTEGER | Jornada base (horas) |
| base_minutes | INTEGER | Jornada base (minutos) |

### Tabla `records`
| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| id | INTEGER PK | Identificador único |
| project_id | INTEGER FK | Referencia al proyecto |
| date | TEXT | Fecha (YYYY-MM-DD) |
| hours | INTEGER | Horas trabajadas |
| minutes | INTEGER | Minutos trabajados |
| difference | INTEGER | Balance en minutos |

## Confiabilidad y Seguridad

- **Transacciones**: Todas las operaciones críticas de base de datos están protegidas por transacciones SQLite.
- **Atomicidad en Exportación**: Los volcados JSON siguen utilizando escrituras atómicas.
- **Privacidad**: Todos los datos se almacenan localmente en el equipo del usuario.

## Testing

La suite de tests ha sido adaptada para utilizar bases de datos temporales:
- `test_storage`: Verifica el esquema y el comportamiento de `DatabaseManager`.
- `test_cli`: Utiliza parches (mocking) para simular la entrada del usuario sobre la lógica de base de datos.
