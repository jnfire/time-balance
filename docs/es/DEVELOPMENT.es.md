# Guía de desarrollo

Notas técnicas de `time-balance` v0.6.x. El proyecto está terminado, así que esta guía es una referencia, no una invitación a contribuir. El diseño se describe en [ARCHITECTURE.es.md](ARCHITECTURE.es.md).

## Filosofía

- **Capas que solo dependen hacia abajo**: los flujos (`cli/`) usan la base de datos, la capa de terminal, las traducciones y funciones puras; nada por debajo conoce los flujos.
- **Lógica pura fuera de las pantallas**: interpretar, dar formato y calcular páginas son funciones simples con tests unitarios.
- **Código tipado**: las funciones públicas están anotadas y `mypy` pasa sin excepciones.
- **Sin efectos ocultos**: importar el paquete nunca toca el disco ni la terminal.
- **Nombres descriptivos**: sin variables de una letra fuera de las comprensiones.

## Preparación

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
./main.py          # o: time-balance
```

## Comprobaciones

La CI ejecuta todo esto en cada push y pull request:

```bash
ruff check .                  # lint
ruff format --check .         # formato
mypy time_balance             # tipos
python -m unittest discover   # tests
coverage run -m unittest discover && coverage report --fail-under=90
```

`ruff format .` y `ruff check --fix .` corrigen solos la mayoría de los avisos.

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
3. El workflow Release comprueba que el tag coincide con `VERSION`, construye el wheel y la distribución de código fuente y crea la release con la sección del changelog como notas.
