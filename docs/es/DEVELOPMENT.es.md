# Guía para Desarrolladores

Esta guía proporciona detalles técnicos para desarrolladores que deseen contribuir a la versión 0.3.x de `time-balance`.

## Filosofía del Proyecto

- **Solo Biblioteca Estándar**: El core y la persistencia deben depender únicamente de librerías nativas de Python (como `sqlite3`).
- **Clean Code**: Naming descriptivo (mínimo 3 caracteres), modularidad y alta cobertura de tests.
- **Transaccionalidad**: Todas las escrituras en la base de datos deben ser consistentes y seguras.

## Estructura de Capas

### 1. Lógica de Persistencia (`storage.py`)
Gestiona la base de datos SQLite global.
- `DatabaseManager`: Clase central para CRUD de proyectos y registros.
- `db`: Instancia global utilizada por el resto de la aplicación.

### 2. Capa de Presentación (`cli.py`)
Controla el flujo de menús e interacción con el usuario.
- `manage_projects()`: Lógica para el submenú de gestión multiproyecto.
- `register_day()`: Interactúa con `db` para guardar jornadas en el proyecto activo.

### 3. Intercambio de Datos (`io.py`)
Funciones para leer JSON de legado y exportar volcados.
- `read_history_file(path)`: Lee un JSON y valida que cumpla con el esquema antiguo.

## Ejecución de Tests

Es fundamental mantener los tests actualizados. Se utiliza una base de datos temporal para evitar ensuciar los datos reales del desarrollador.

```bash
# Ejecutar todos los tests
python3 -m unittest discover -v tests
```

## Gestión de la Base de Datos

La base de datos se inicializa automáticamente en la primera ejecución. El esquema se define en el método `_initialize_database()` de `DatabaseManager`.

### Rutas de Datos (XDG)
- macOS: `~/Library/Application Support/time-balance/`
- Linux: `~/.local/share/time-balance/`

## Cómo añadir un comando CLI

1. Modifica la función `main()` en `cli.py`.
2. Añade el nuevo flag en `argparse`.
3. Implementa la lógica correspondiente, utilizando `db` si requiere acceso a datos o `translate()` para la salida.

## Referencia del Esquema de Registros
Las jornadas se guardan como minutos de diferencia (`worked_minutes - base_minutes`).
- Ejemplo: Si la base es 7h 45m (465 min) y se trabajan 8h (480 min), la diferencia guardada es `+15`.
