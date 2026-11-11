# Evolución

*Read this in [English](README.md).*

Cómo time-balance pasó de su primer commit a su versión final, por qué existe y qué se probó y se dejó fuera.

## La historia

La herramienta de control horario que se usaba en el trabajo no era transparente, y no era sencillo sacar un dato desde el lado del trabajador: si un día había sido más corto o más largo de lo que tocaba, y cómo se acumulaba eso a lo largo de las semanas.

La respuesta fue una pequeña herramienta de terminal que hace solo eso. Indicas cuánto debe durar tu jornada (la base diaria), al final de cada día escribes las horas y los minutos que has trabajado, y te dice la diferencia y mantiene un saldo acumulado. Sin cuentas, sin red, un único archivo SQLite. Varios proyectos, porque la misma persona puede tener más de una base.

Pasó de ser un script a un paquete con base de datos, traducciones y tests, pero la idea siguió siendo del mismo tamaño. Cuando la idea se quedó pequeña para la terminal, empezó de nuevo como [time-tracker](https://time-tracker.jnfire.dev/), una aplicación web instalable, y este repositorio se quedó como la versión limpia y final del primer experimento.

## Cronología

| Cuándo | Qué pasó |
| --- | --- |
| Enero de 2026 | Primer commit: un script para contar las horas de una jornada. |
| Abril de 2026 | Versión 0.5.0: almacenamiento en SQLite, varios proyectos, traducciones y una estructura modular. |
| Abril de 2026 | Se probó un temporizador en vivo en una rama aparte (`live-tracking`) y se dejó fuera. Ver abajo. |
| Junio de 2026 | La idea se quedó pequeña para la terminal y empezó de nuevo como time-tracker, una aplicación web. |
| Noviembre de 2026 | Limpieza y versión final, la 0.6.0: código tipado, tests de todos los flujos, pantallas traducidas y un formato de datos documentado. |

## Un experimento que se dejó fuera

Entre el 26 y el 27 de abril de 2026, justo después de la versión 0.5.0, una rama probó otra forma de entrada: en lugar de escribir las horas al final del día, un temporizador corría en la terminal. Tenía una pantalla de temporizador en tiempo real con pausa y reanudación, un saldo que se actualizaba mientras corría, un guardado automático cada 60 segundos (solo minutos) y una confirmación al cancelar. Fueron 8 commits y unas 800 líneas añadidas, y nunca se fusionó.

Se descartó porque no era realmente necesario. Escribir el día al final ya respondía a la pregunta. Lo que faltaba no era una terminal más lista, sino una herramienta que se instala y se usa cada día con una interfaz accesible. Eso es lo que acabó siendo time-tracker.

El código se conserva para que quede constancia del intento. [`docs/experiments/live-tracking.patch`](../experiments/live-tracking.patch) contiene los cambios de la rama en `time_balance/`, sin su documentación:

```bash
git checkout 172562d          # versión 0.5.0, la base de la rama
git apply docs/experiments/live-tracking.patch
```

El último commit de la rama fue `3867dc0`.

## En números

| | Versión 0.5.0 | Versión final (0.6.0) |
| --- | --- | --- |
| Tests automáticos | 51 | 144 |
| Cobertura de tests | 63 % | 96 % |
| Avisos de lint (ruff, con las reglas que usa ahora el proyecto) | 488 | 0 |
| Errores de tipos (mypy) | 16 | 0 |
| Versiones de Python en la CI | 1 (la última) | de 3.10 a 3.14 |

La columna "antes" es el estado del código justo antes de la limpieza descrita arriba.

## Imágenes

- [`dashboard-es.png`](../screenshots/dashboard-es.png): el panel principal
- [`history-es.png`](../screenshots/history-es.png): el historial
