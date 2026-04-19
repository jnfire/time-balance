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
│   ├── storage.py            # Persistencia y migración de esquemas
│   ├── io.py                 # Validación, importación y exportación
│   └── cli.py                # Interfaz de usuario y argumentos
├── tests/                    # Suite de tests modular
│   ├── test_core.py
│   ├── test_storage.py
│   ├── test_io.py
│   └── test_cli.py
├── docs/                     # Documentación
├── README.md                 # Guía de usuario
└── CHANGELOG.md              # Historial de cambios
```

## Módulos y Componentes

### 1. **`core.py` (Lógica de Negocio)**
Contiene el "cerebro" matemático del sistema, independiente de la I/O.
- `formatear_tiempo()`: Convierte minutos a formato legible +/- Xh Ym.
- `calcular_saldo_total()`: Suma las diferencias de una lista de registros.

### 2. **`storage.py` (Capa de Persistencia)**
Gestiona el ciclo de vida del archivo de datos y la integridad física.
- `cargar_datos()`: Carga el JSON y aplica **migración automática** al nuevo esquema estructurado.
- `guardar_datos()`: Escritura **atómica** (crash-safe) mediante archivos temporales y reemplazo.
- `_crear_backup()`: Genera respaldos versionados antes de operaciones críticas.

### 3. **`cli.py` (Capa de Presentación)**
Maneja la interacción con el usuario final.
- Soporta **argumentos de comando** (`--status`, `--list`, `--version`) para consultas rápidas.
- Proporciona un **menú interactivo** para la gestión diaria.
- Permite la configuración dinámica del proyecto (nombre y jornada base).

### 4. **`io.py` (Intercambio de Datos)**
Lógica para importar y exportar historiales entre diferentes sistemas.
- Validación rigurosa de esquemas JSON (soporta formatos legacy).
- Soporte para mezcla de historiales (`merge`) o reemplazo total (`overwrite`).

## Esquema de Datos (JSON)

Cada proyecto se guarda con su propio contexto de configuración para permitir el multiproyecto futuro.

```json
{
    "metadata": {
        "project_name": "Mi Proyecto",
        "horas_base": 7,
        "minutos_base": 45,
        "version": "1.0"
    },
    "registros": {
        "2026-04-19": {
            "horas": 8,
            "minutos": 0,
            "diferencia": 15
        }
    }
}
```

## Flujos Principales

### Registro de Jornada
1. Se carga el archivo usando `storage.cargar_datos()`.
2. Se extrae la jornada base desde `metadata`.
3. El usuario introduce las horas trabajadas.
4. Se calcula la diferencia: `trabajado - base`.
5. Se guarda el objeto completo (metadatos + registros).

### Importación de Historial
1. Se valida que el archivo fuente sea un JSON válido.
2. Se normaliza al nuevo esquema si es antiguo.
3. En modo `merge`, se actualizan solo los registros, respetando el nombre y jornada del proyecto local.
4. En modo `overwrite`, se reemplaza el archivo completo (incluyendo configuración).

## Confiabilidad y Seguridad

- **Integridad**: Todas las escrituras son atómicas. Si el programa se cierra inesperadamente, los datos no se corrompen.
- **Resiliencia**: Migración transparente de formatos antiguos.
- **Privacidad**: Almacenamiento 100% local en texto plano (JSON).

## Testing

La suite de tests está dividida para coincidir con la arquitectura del paquete:
- `test_core`: Valida algoritmos de cálculo.
- `test_storage`: Valida persistencia, backups y migración de esquemas.
- `test_io`: Valida importación/exportación y compatibilidad legacy.
- `test_cli`: Valida la interfaz de usuario y los argumentos de comando.

## Extensibilidad Futura (Evolución Técnica)

El sistema está diseñado para evolucionar hacia una solución de gestión de tiempo profesional:

1. **Almacenamiento Relacional (SQLite)**:
   - Migrar la persistencia interna de JSON a SQLite.
   - Ventajas: Consultas complejas (estadísticas mensuales/anuales), integridad de datos y soporte concurrente.
   - El formato JSON se mantendrá exclusivamente para flujos de importación y exportación (portabilidad).

2. **Soporte Multiproyecto Centralizado**:
   - Implementar un registro global de proyectos que permita cambiar de contexto sin cambiar de directorio.
   - Ejemplo: `time-balance --project work` vs `time-balance --project freelance`.

3. **Independencia del Directorio de Ejecución**:
   - Adoptar estándares como XDG Base Directory para almacenar datos en rutas globales configurables.
   - Permitir la ubicación de la base de datos en servicios de almacenamiento en la nube (Dropbox, Drive) para sincronización automática.

4. **Modernización de la Interfaz (Rich UI)**:
   - Integrar librerías como `rich` o `click` para mejorar la presentación de tablas, barras de progreso y colores.
   - Mejorar la usabilidad del menú interactivo.

5. **API de Estadísticas**:
   - Desarrollar un motor de reportes para generar resúmenes automáticos por periodos de tiempo.
