# Arquitectura del Proyecto

## Visión General

`time-balance` es una aplicación de terminal para registrar jornadas laborales y gestionar el saldo horario acumulado. Está diseñada bajo principios de modularidad, integridad de datos y facilidad de uso.

## Estructura del Proyecto

```
time-balance/
├── time_balance/              # Paquete principal
│   ├── __init__.py           # Fachada (reexporta la API pública)
│   ├── __main__.py           # Punto de entrada para ejecución como módulo
│   ├── constants.py          # Configuración y constantes centralizadas
│   ├── core.py               # Lógica de negocio (formateo, cálculos)
│   ├── storage.py            # Persistencia y almacenamiento atómico
│   ├── io.py                 # Validación, importación y exportación
│   ├── cli.py                # Interfaz de usuario y argumentos
│   └── i18n.py               # Sistema de internacionalización
├── tests/                    # Suite de tests modular
│   ├── test_core.py
│   ├── test_storage.py
│   ├── test_io.py
│   └── test_cli.py
├── docs/                     # Documentación
├── README.md                 # Guía de usuario (Inglés)
└── CHANGELOG.md              # Historial de cambios
```

## Módulos y Componentes

### 1. **`core.py` (Lógica de Negocio)**
Contiene el "cerebro" matemático del sistema, independiente de la I/O.
- `format_time()`: Convierte minutos a formato legible +/- Xh Ym.
- `calculate_total_balance()`: Suma las diferencias de una lista de registros.

### 2. **`storage.py` (Capa de Persistencia)**
Gestiona el ciclo de vida del archivo de datos e integridad física.
- `load_data()`: Carga el JSON estructurado del historial.
- `save_data()`: Escritura **atómica** (crash-safe) mediante archivos temporales.
- `_create_backup()`: Genera respaldos versionados antes de operaciones críticas.

### 3. **`cli.py` (Capa de Presentación)**
Maneja la interacción con el usuario final.
- Soporta **argumentos de comando** (`--status`, `--list`, `--version`, `--lang`) para consultas rápidas.
- Proporciona un **menú interactivo** bilingüe para la gestión diaria.
- Permite la configuración dinámica del proyecto (nombre y jornada base).

### 4. **`io.py` (Intercambio de Datos)**
Lógica para importar y exportar historiales entre diferentes sistemas.
- Validación rigurosa de esquemas JSON.
- Soporte para mezcla de historiales (`merge`) o reemplazo total (`overwrite`).

### 5. **`i18n.py` (Internacionalización)**
Motor de traducción simple que permite que la aplicación hable varios idiomas (actualmente inglés y español). Detecta automáticamente el idioma del sistema.

## Esquema de Datos (JSON)

Cada proyecto se guarda con su propio contexto de configuración. Las claves se almacenan en inglés para consistencia técnica.

```json
{
    "metadata": {
        "project_name": "Mi Proyecto",
        "hours_base": 7,
        "minutes_base": 45,
        "version": "1.0",
        "language": "auto"
    },
    "records": {
        "2026-04-19": {
            "hours": 8,
            "minutes": 0,
            "difference": 15
        }
    }
}
```

## Confiabilidad y Seguridad

- **Integridad**: Todas las escrituras son atómicas. Si el programa se cierra inesperadamente, los datos no se corrompen.
- **Privacidad**: Almacenamiento 100% local en texto plano (JSON).

## Testing

La suite de tests está dividida para coincidir con la arquitectura del paquete:
- `test_core`: Valida algoritmos de cálculo.
- `test_storage`: Valida persistencia y backups.
- `test_io`: Valida la lógica de importación/exportación.
- `test_cli`: Valida la interfaz de usuario y los argumentos de comando.

## Extensibilidad Futura (Evolución Técnica)

El sistema está diseñado para evolucionar hacia una solución de gestión de tiempo profesional:

1. **Almacenamiento Relacional (SQLite)**:
   - Migrar la persistencia interna de JSON a SQLite.
   - El formato JSON se mantendrá exclusivamente para intercambio.

2. **Soporte Multiproyecto Centralizado**:
   - Implementar un registro global de proyectos para cambiar de contexto rápidamente.

3. **Sincronización en la Nube**:
   - Permitir la ubicación de la base de datos en servicios como Dropbox o Drive para sincronización automática.

4. **Interfaz Enriquecida (Rich UI)**:
   - Integrar librerías como `rich` para mejorar la presentación visual.
