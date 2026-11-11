# Formato de los datos

`time-balance` exporta el historial del proyecto activo en un archivo JSON e importa ese mismo formato. El archivo es texto plano y se puede editar a mano.

## Ejemplo

```json
{
    "metadata": {
        "project_name": "Proyecto de ejemplo",
        "hours_base": 7,
        "minutes_base": 45,
        "version": "1.0",
        "language": "es"
    },
    "records": {
        "2026-04-15": { "hours": 8, "minutes": 0, "difference": 15 },
        "2026-04-16": { "hours": 7, "minutes": 45, "difference": 0 },
        "2026-04-17": { "hours": 6, "minutes": 30, "difference": -75 }
    }
}
```

Hay un archivo completo en [`examples/history_example.json`](../../examples/history_example.json).

## Campos

| Campo | Tipo | Significado |
| --- | --- | --- |
| `metadata.project_name` | texto | Nombre del proyecto. Obligatorio. |
| `metadata.hours_base` | entero, 0 o más | Horas de la base diaria. Obligatorio. |
| `metadata.minutes_base` | entero, de 0 a 59 | Minutos de la base diaria. Obligatorio. |
| `metadata.version`, `metadata.language` | texto | Informativos. |
| `records` | objeto | Una entrada por día, con la fecha como clave en formato `AAAA-MM-DD`. Obligatorio. |
| `records.<fecha>.hours` | entero | Horas trabajadas ese día. |
| `records.<fecha>.minutes` | entero | Minutos trabajados ese día. |
| `records.<fecha>.difference` | entero | Minutos por encima (positivo) o por debajo (negativo) de la base diaria: `hours * 60 + minutes - base`. |

Todos los valores de un registro son obligatorios y deben ser enteros. Un archivo que no cumpla esto se rechaza y el mensaje indica el problema.

## Reglas de importación

- Los registros entran en el **proyecto activo**. El nombre y la base diaria del archivo no se aplican a él: se quedan como están.
- Dos modos: **fusionar** (el predeterminado) sustituye los días que ya existen y conserva el resto, y **sobrescribir** borra antes todos los registros del proyecto.
- `difference` se guarda tal como viene en el archivo. No se recalcula contra la base del proyecto, así que revísalo si la base es distinta.
- El saldo acumulado se reconstruye a partir de los registros después de importar.
