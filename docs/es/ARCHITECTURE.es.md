# Arquitectura del proyecto

## Visión general

`time-balance` registra jornadas y lleva un saldo de horas desde la terminal. El código se divide en capas que solo dependen hacia abajo, de modo que cada capa se puede probar sin las de encima.

```
cli ──► database, ui, i18n, utils
 ui ──► Rich (y nada más)
database ──► SQLite
```

## Estructura del proyecto

```
time-balance/
├── main.py                   # Ejecutar desde el código, sin instalar
├── pyproject.toml            # Empaquetado y configuración de ruff y mypy
├── time_balance/
│   ├── cli/                  # Los flujos que ve el usuario
│   │   ├── main.py           # Parser de argumentos, panel y bucle del centro de control
│   │   ├── context.py        # Context: base de datos + idioma, que recibe cada flujo
│   │   ├── registration.py   # Registrar un día
│   │   ├── history.py        # Listar, recorrer y borrar días
│   │   ├── projects.py       # Cambiar, crear y borrar proyectos
│   │   └── config_menu.py    # Ajustes del proyecto, idioma, importar y exportar
│   ├── database/
│   │   ├── manager.py        # DatabaseManager: todo el SQL
│   │   ├── models.py         # Project, Record y RecordData (filas tipadas)
│   │   └── __init__.py       # get_database(): abre la base de datos al primer uso
│   ├── ui/interface.py       # El único módulo que habla con Rich
│   ├── i18n/                 # Traductor y los JSON en/es
│   ├── utils/
│   │   ├── calculations.py   # Diferencias, formato y colores del saldo (puro)
│   │   ├── validation.py     # Interpretar lo que escribe el usuario (puro)
│   │   ├── pagination.py     # Aritmética de páginas (puro)
│   │   └── files.py          # El archivo de historial: validación y exportación atómica
│   ├── config.py             # Versión, carpeta de datos, valores por defecto
│   └── VERSION               # Única fuente de la versión
├── tests/
└── docs/
```

## Principios

### Los flujos reciben un contexto
Cada flujo interactivo recibe un `Context` (la base de datos y el idioma) en lugar de usar globales. `ctx.t("clave")` traduce, `ctx.pause()` espera a Enter y `ctx.confirm(...)` pregunta sí o no con las letras del idioma de la sesión. Así un flujo se prueba con una base de datos temporal y una terminal guionizada, sin parchear nada.

### La base de datos se abre cuando hace falta
`get_database()` crea el archivo SQLite la primera vez que alguien lo pide. Importar el paquete, o ejecutar `time-balance --version`, nunca toca el disco. Los tests instalan su propia instancia con `set_database()`.

### La lógica vive fuera de las pantallas
Interpretar fechas y duraciones (`validation.py`), la aritmética de páginas (`pagination.py`) y las reglas para borrar un proyecto (`projects.find_deletable_project`) son funciones simples. Los flujos solo preguntan, las llaman e imprimen.

### Un solo módulo habla con la biblioteca de terminal
`ui/interface.py` es el único sitio que importa Rich. El texto que escribe el usuario (nombres de proyecto, rutas) pasa por `ui.escape` antes de ir dentro de un mensaje, porque Rich lee los corchetes como marcado.

### Filas tipadas
La base de datos devuelve diccionarios tipados `Project` y `Record`. `get_active_project()` siempre devuelve un proyecto: si el id guardado ya no existe, el primer proyecto pasa a ser el activo.

## Caché del saldo

`projects.total_balance` guarda la suma de las diferencias de un proyecto.
- Una escritura que cambia un registro ajusta la caché en la misma transacción.
- Una caché NULL significa "desconocido" y se reconstruye desde los registros la próxima vez que se lee.
- `import_records` y la opción de reparar la reconstruyen desde los registros.

## Pruebas

- `tests/helpers.py` ofrece `DatabaseTestCase` (una base de datos temporal y un contexto) y `ScriptedTerminal`, que responde a las preguntas desde una lista y registra lo que se imprime. Un flujo que pide más entrada de la prevista hace fallar el test.
- Los flujos se prueban de principio a fin con esa terminal; las funciones puras con tests unitarios; `test_translator.py` comprueba que los dos idiomas definen las mismas claves y los mismos marcadores.
- `tests/test_main.py` ejecuta el programa en un subproceso para comprobar que importarlo o pedir la versión no crea nada en disco.

## Distribución

El proyecto es un paquete de Python definido por completo en `pyproject.toml`. Las traducciones y el archivo `VERSION` son datos del paquete, y la CI comprueba que acaban dentro del wheel. Un tag `v*` construye el wheel y la distribución de código fuente y los adjunta a una release de GitHub.
