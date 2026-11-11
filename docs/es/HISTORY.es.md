# Por qué existe time-balance y qué se probó

## El problema

La herramienta de control horario que se usaba en el trabajo no era transparente, y no era sencillo sacar un dato desde el lado del trabajador: si un día había sido más corto o más largo de lo que tocaba, y cómo se acumulaba eso a lo largo de las semanas.

## La respuesta sencilla

Una pequeña herramienta de terminal que hace solo eso:

1. Indicas cuánto debe durar tu jornada (la base diaria).
2. Al final de cada día escribes las horas y los minutos que has trabajado.
3. Te dice la diferencia de ese día y mantiene un saldo acumulado: cuántas horas llevas de más o de menos.

Sin cuentas, sin red, un único archivo SQLite. Varios proyectos, porque la misma persona puede tener más de una base. Todo lo demás del código (las traducciones, las capas tipadas, los tests) está para que esa idea siga siendo pequeña y clara.

## Un experimento que se dejó fuera: el temporizador en vivo

Entre el 26 y el 27 de abril de 2026, justo después de la versión 0.5.0, una rama llamada `live-tracking` probó otra forma de entrada: en lugar de escribir las horas al final del día, un temporizador corría en la terminal.

Lo que contenía (8 commits, unas 800 líneas añadidas, nunca fusionada):

- Una pantalla de temporizador en tiempo real con pausa y reanudación.
- El saldo se actualizaba mientras corría el temporizador, con la caché ajustada de forma atómica.
- Un guardado automático cada 60 segundos (solo minutos; los segundos no se guardaban).
- Una confirmación al cancelar y claves de traducción nuevas en los dos idiomas.

Se descartó porque no era realmente necesario. Escribir el día al final ya respondía a la pregunta. Lo que faltaba no era una terminal más lista, sino una herramienta que se instala y se usa cada día con una interfaz accesible. Eso es lo que acabó siendo time-tracker, desde junio de 2026.

## Dónde está el código

El trabajo se conserva para que quede constancia del intento:

- [`docs/experiments/live-tracking.patch`](../experiments/live-tracking.patch) contiene todo el código de la rama (los cambios de `time_balance/`, sin la documentación). Para verlo:

  ```bash
  git checkout 172562d          # versión 0.5.0, la base de la rama
  git apply docs/experiments/live-tracking.patch
  ```

- El último commit de la rama fue `3867dc0`.

## A qué llevó

time-balance fue el primer boceto de [time-tracker](https://time-tracker.jnfire.dev/), una aplicación web instalable con tareas, bloques de tiempo reales e historial auditable. Este repositorio se queda como la versión limpia y final de ese primer experimento.
