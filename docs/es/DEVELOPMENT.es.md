# Guía de desarrollo

Notas técnicas de `time-balance` v0.6.x. El proyecto está terminado, así que esta guía es una referencia, no una invitación a contribuir. El diseño se describe en [ARCHITECTURE.es.md](ARCHITECTURE.es.md).

## Filosofía

- **Capas que solo dependen hacia abajo**: los flujos (`cli/`) usan la base de datos, la capa de terminal, las traducciones y funciones puras; nada por debajo conoce los flujos.
- **Lógica pura fuera de las pantallas**: interpretar, dar formato y calcular páginas son funciones simples con tests unitarios.
- **Código tipado**: las funciones públicas están anotadas y `mypy` pasa sin excepciones.
- **Sin efectos ocultos**: importar el paquete nunca toca el disco ni la terminal.
- **Nombres descriptivos**: sin variables de una letra fuera de las comprensiones.

## Preparación

El proyecto usa [uv](https://docs.astral.sh/uv/) (se instala con `brew install uv` o desde su web). Instala Python, crea el entorno y mantiene las dependencias bloqueadas en `uv.lock`, así que no hay que instalar nada más.

```bash
git clone https://github.com/jnfire/time-balance.git
cd time-balance
uv sync                    # crea .venv con el paquete y las herramientas de desarrollo
uv run time-balance        # ejecutar la aplicación
```

`uv run` crea y actualiza el entorno por sí mismo, así que `uv sync` solo hace falta una vez, o para refrescarlo. Se necesita Python 3.10 o superior; `.python-version` elige la 3.13 para desarrollar, y `uv run --python 3.10 ...` ejecuta un comando en otra versión.

## Comprobaciones

La CI ejecuta todo esto en cada push y pull request:

```bash
uv run ruff check .                                     # lint
uv run ruff format --check .                            # formato
uv run mypy time_balance                                # tipos
uv run python -m unittest discover                      # tests
uv run coverage run -m unittest discover && uv run coverage report --fail-under=90
uv lock --check                                         # el fichero de bloqueo está al día
```

`uv run ruff format .` y `uv run ruff check --fix .` corrigen solos la mayoría de los avisos.

## Dependencias

La única dependencia de ejecución es `rich`. Las herramientas de desarrollo (`ruff`, `mypy`, `coverage`) están en el grupo de dependencias `dev` de `pyproject.toml`. Tras cambiar una dependencia ejecuta `uv lock` y sube `uv.lock`; la CI falla si no está al día.

## Probar flujos

`tests/helpers.py` da a cada test una base de datos temporal y una terminal con respuestas guionizadas:

```python
class TestRegisterDay(DatabaseTestCase):
    def test_stores_the_day(self):
        with ScriptedTerminal(["2026-04-24", "8", "15"]).active() as terminal:
            register_day(self.ctx)
        record = self.db.get_record_by_date(self.project_id, "2026-04-24")
        self.assertEqual(record["difference"], 30)
        self.assertIn("+30m", terminal.output)
```

Cada pregunta del flujo consume la siguiente respuesta; una respuesta vacía toma el valor por defecto. Un flujo que pide más de lo guionizado, o un test que deja respuestas sin usar, falla.

## Añadir un flujo

1. Pon la lógica que no necesita terminal en `utils/` como función pura y pruébala.
2. Escribe el flujo en `cli/` como una función que recibe un `Context`. Usa `ctx.t(...)`, `ctx.pause()` y `ctx.confirm(...)`, y pasa por `ui.escape` todo lo que haya escrito el usuario antes de imprimirlo.
3. Añade las claves de traducción a **los dos** `en.json` y `es.json`. Un test comprueba que coinciden, marcadores incluidos.
4. Regístralo en el menú o en `build_parser()` de `cli/main.py`, y pruébalo con `ScriptedTerminal`.

## Base de datos

El esquema está en `database/manager.py`. La carpeta de datos es `~/.local/share/time-balance/` en Linux (o `$XDG_DATA_HOME`), `~/Library/Application Support/time-balance/` en macOS y `%APPDATA%\time-balance\` en Windows. Toda escritura pasa por `DatabaseManager`, que mantiene la caché del saldo coherente en la misma transacción.

## Publicar una versión

1. Actualiza `time_balance/VERSION` y añade una sección `## [x.y.z] - fecha` a `CHANGELOG.md`.
2. Fusiona en `main` y sube el tag `vx.y.z`.
3. El workflow Release (`scripts/release_notes.py`) comprueba que el tag coincide con `VERSION` y que el changelog tiene una sección para él, construye el wheel y la distribución de código fuente (`uv build`) y crea la release con esa sección como notas. Si creaste la release a mano desde la web, adjunta los archivos a esa release. La CI ejecuta la misma comprobación en cada push, así que una entrada que falte en el changelog nunca espera al día de la release. Para construir los archivos a mano: `uv build`, y aparecen en `dist/`.
