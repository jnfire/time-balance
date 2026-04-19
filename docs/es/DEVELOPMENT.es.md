# Guía para Desarrolladores

Esta guía proporciona detalles técnicos para desarrolladores que deseen integrar `time-balance` en sus flujos o contribuir a su desarrollo.

## Filosofía del Proyecto

- **Solo Biblioteca Estándar**: No se permiten dependencias externas para la funcionalidad principal.
- **Código Limpio (Clean Code)**: Naming descriptivo, modularidad y alta cobertura de tests.
- **Seguridad**: Escrituras atómicas y validación defensiva de datos.

## Estructura de Módulos

El proyecto está organizado en capas lógicas:

### 1. Lógica de Negocio (`core.py`)
Funciones puras para cálculos de tiempo.
- `format_time(minutes)`: Devuelve strings como `"-1h 30m"`.
- `calculate_total_balance(records)`: Suma diferencias del diccionario de datos.

### 2. Persistencia (`storage.py`)
Gestiona E/S de disco y migración de esquemas.
- `load_data(path)`: Devuelve un diccionario estructurado con `metadata` y `records`.
- `save_data(data, path)`: Escritura atómica mediante archivos temporales.

### 3. Intercambio de Datos (`io.py`)
Lógica para mover datos entre sistemas.
- `export_history(dest)`: Exporta el JSON estructurado completo.
- `import_history(src, mode)`: Valida y mezcla/sobreescribe datos.

### 4. Interfaz de Usuario (`cli.py`)
Capa de presentación que utiliza `argparse` y un menú interactivo.

### 5. Internacionalización (`i18n.py`)
Motor de traducción simple. Utiliza `translate(key, lang)` para obtener cadenas.

## Ejecución de Tests

Utilizamos el framework estándar `unittest`:

```bash
# Ejecutar todos los tests
python3 -m unittest discover -v tests
```

## Añadir un Nuevo Idioma

1. Abre `time_balance/i18n.py`.
2. Añade una nueva entrada al diccionario `STRINGS` con el código ISO 639-1 (ej. `"fr"` para francés).
3. Traduce todas las claves basándote en la plantilla `"en"`.
4. El sistema lo detectará automáticamente o mediante el flag `--lang`.

## Referencia del Esquema de Datos

```json
{
    "metadata": {
        "project_name": "string",
        "hours_base": "int",
        "minutos_base": "int",
        "version": "string",
        "language": "string (en|es|auto)"
    },
    "records": {
        "YYYY-MM-DD": {
            "hours": "int",
            "minutes": "int",
            "difference": "int (worked_minutes - base_minutes)"
        }
    }
}
```
