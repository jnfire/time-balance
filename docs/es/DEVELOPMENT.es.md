# Guía para Desarrolladores

Esta guía proporciona detalles técnicos para desarrolladores que deseen contribuir a `time-balance` v0.5.x.

## Filosofía del Proyecto

- **Modularización Basada en Dominios**: La aplicación está dividida en dominios funcionales para asegurar la escalabilidad y mantenibilidad.
- **Abstracción de UI**: La lógica de negocio está desacoplada de las librerías de renderizado de terminal.
- **Estándares de Naming Estrictos**: No se permiten variables de una sola letra (excepto en list comprehensions obvias). Mínimo 3 caracteres.

## Estructura de Capas

### 1. Dominio de Persistencia (`database/`)
- `DatabaseManager`: Centraliza todas las operaciones SQLite. Gestiona transacciones, actualizaciones atómicas de saldo e importaciones masivas.
- Instancia global `db`: Utilizada como un singleton en toda la aplicación.

### 2. Dominio de Presentación (`cli/`)
- Orquestado por `cli/main.py`.
- Dividido en módulos temáticos: `registration.py`, `history.py`, `projects.py`, etc.
- Utiliza `ui/interface.py` para toda la E/S de consola.

### 3. Capa de Abstracción de UI (`ui/`)
- `ui/interface.py`: El único módulo autorizado para importar librerías visuales (como `Rich`).
- Proporciona componentes genéricos: `render_header`, `render_table`, `render_navigation_help`.

### 4. Dominio de Localización (`i18n/`)
- `i18n/translator.py`: Motor de traducción con sistema de caché.
- `i18n/locales/*.json`: Cadenas de texto externalizadas.

## Ejecución para Desarrollo

Durante el desarrollo, utiliza el punto de entrada directo en el directorio raíz:

```bash
chmod +x main.py
./main.py
```

## Ejecución de Tests

Utilizamos bases de datos SQLite temporales para las pruebas para asegurar el aislamiento del entorno.

```bash
# Ejecutar todos los tests
python3 -m unittest discover -v tests
```

## Cómo añadir un nuevo comando CLI

1. Si es un flujo nuevo, crea un archivo en `time_balance/cli/`.
2. Registra el comando en la función `main()` en `time_balance/cli/main.py`.
3. Utiliza `ui.interface` para cualquier interacción con el usuario.
4. Asegúrate de que la nueva lógica siga los estándares de naming y DRY.

## Gestión de la Base de Datos

La base de datos sigue los estándares XDG. El esquema se define en `DatabaseManager._initialize_database()`.
- macOS: `~/Library/Application Support/time-balance/`
- Linux: `~/.local/share/time-balance/`
