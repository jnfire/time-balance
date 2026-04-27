# Guía para Desarrolladores

Esta guía proporciona detalles técnicos para desarrolladores que deseen contribuir a `time-balance` v0.5.x.

## Filosofía del Proyecto

- **Modularización Basada en Dominios**: La aplicación está dividida en dominios funcionales para asegurar la escalabilidad y mantenibilidad.
- **Abstracción de UI**: La lógica de negocio está desacoplada de las librerías de renderizado de terminal.
- **Estándares de Naming Estrictos**: No se permiten variables de una sola letra (excepto en list comprehensions obvias). Mínimo 3 caracteres.

## Estructura de Capas

### 1. Dominio de Persistencia (`database/`)
- `DatabaseManager`: Centraliza todas las operaciones SQLite. Gestiona transacciones, actualizaciones atómicas de saldo e importaciones masivas.
- Métodos clave para la integración del contador:
  - `get_or_create_today_record(project_id)`: Crea o recupera el registro de hoy; inicializa el caché de `total_balance`.
  - `update_record_time(record_id, hours, minutes)`: Actualiza el registro e incrementa el caché de `total_balance` del proyecto de forma atómica.
- Instancia global `db`: Utilizada como un singleton en toda la aplicación.

### 2. Dominio de Presentación (`cli/`)
- Orquestado por `cli/main.py`.
- Dividido en módulos temáticos: `registration.py`, `timer.py`, `history.py`, `projects.py`, etc.
- `timer.py` demuestra el flujo completo: **menú** → **contador activo** → **pausa** → **guardar**.
  - `show_timer_menu()`: Bucle principal mostrando el display del contador y opciones del menú.
  - `_timer_loop()`: Ejecuta el contador activo, auto-guarda cada 60 segundos, espera ENTER para detener.
  - Ambas funciones llaman a la capa de UI para renderizado.
- Utiliza `ui/interface.py` para toda la E/S de consola.

### 3. Capa de Abstracción de UI (`ui/`)
- `ui/interface.py`: El único módulo autorizado para importar librerías visuales (como `Rich`).
- Componentes específicos del contador:
  - `render_timer_running(hours, minutes, seconds, project_name, base_time, balance, lang)`: Muestra el contador activo con colores y etiquetas.
  - `render_timer_menu_with_display(hours, minutes, seconds, project_name, base_time, balance, lang)`: Muestra el contador pausado con el mismo formato visual.
  - Ambas funciones usan `clear_screen()` para evitar scrolling de terminal y aplican coloreado dinámico (verde/rojo para el saldo).
- Proporciona componentes genéricos: `render_header`, `render_table`, `render_navigation_help`.

### 4. Dominio de Localización (`i18n/`)
- `i18n/translator.py`: Motor de traducción con sistema de caché.
- `i18n/locales/*.json`: Cadenas de texto externalizadas.
- Claves de traducción del contador (nuevas en v0.6.0):
  - `timer_label_elapsed`: Etiqueta descriptiva para tiempo transcurrido.
  - `timer_label_status`: Etiqueta descriptiva para estado del contador.
  - `timer_label_balance`: Etiqueta descriptiva para la visualización del saldo.

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

## Atomicidad del Caché de Saldo

A partir de v0.6.0, el caché de saldo (`projects.total_balance`) se actualiza de forma atómica durante operaciones en tiempo real:

- **Integración del Contador**: Cuando el contador actualiza un registro (cada 60 segundos o al presionar ENTER), `update_record_time()` actualiza inmediatamente el caché de `total_balance` del proyecto usando `COALESCE` para inicialización segura con NULL.
- **Creación de Registros**: Cuando se crea un nuevo registro diario vía `get_or_create_today_record()`, el caché del proyecto se inicializa si es NULL.
- **Actualizaciones Incrementales**: El caché usa aritmética delta: `saldo = COALESCE(saldo, 0) - diferencia_vieja + diferencia_nueva`, asegurando acceso O(1) sin recálculo completo.
- **Seguridad**: Todas las actualizaciones usan el gestor de contexto `_get_connection()` para integridad transaccional con COMMIT automático en caso de éxito.

## Cómo añadir un nuevo comando CLI

1. Si es un flujo nuevo, crea un archivo en `time_balance/cli/`.
2. Registra el comando en la función `main()` en `time_balance/cli/main.py`.
3. Utiliza `ui.interface` para cualquier interacción con el usuario.
4. Asegúrate de que la nueva lógica siga los estándares de naming y DRY.

## Gestión de la Base de Datos

La base de datos sigue los estándares XDG. El esquema se define en `DatabaseManager._initialize_database()`.
- macOS: `~/Library/Application Support/time-balance/`
- Linux: `~/.local/share/time-balance/`
