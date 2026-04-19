# Contribuyendo a time-balance

En primer lugar, ¡gracias por considerar contribuir a `time-balance`! Personas como tú hacen que la comunidad de código abierto sea un lugar increíble para aprender, inspirar y crear.

## ¿Cómo puedo contribuir?

### Reportando Bugs

- Comprueba si el error ya ha sido reportado en la sección de Issues.
- Si no, abre un nuevo issue. Incluye un título claro, una descripción del problema y los pasos para reproducirlo.

### Sugiriendo Mejoras

- Abre un issue de mejora para discutir tu idea antes de escribir el código.
- Explica por qué esta característica sería útil y cómo debería funcionar.

### Añadiendo Nuevos Idiomas (i18n)

Queremos que `time-balance` sea accesible para todos. Para añadir un nuevo idioma:

1. Localiza `time_balance/i18n.py`.
2. Busca el diccionario `STRINGS`.
3. Copia el diccionario `"en"` como plantilla.
4. Añade tu código de idioma (ej. `"it"`, `"pt"`, `"de"`) y traduce los valores.
5. Envía un Pull Request con el título `feat(i18n): add [Language] support`.

### Mejorando la Documentación

- Corrige erratas o errores gramaticales.
- Aclara secciones confusas.
- Traduce los archivos de documentación a otros idiomas.

## Proceso de Desarrollo

1. **Haz un fork del repo** y crea tu rama desde `main`.
2. **Configura tu entorno** (se recomienda Python 3.8+).
3. **Escribe tu código** siguiendo el estilo del proyecto (Clean Code, naming descriptivo).
4. **Añade tests** para cualquier nueva funcionalidad.
5. **Asegúrate de que todos los tests pasan** con `python3 -m unittest discover tests`.
6. **Envía un Pull Request**.

## Guía de Estilo

- El código interno (funciones, variables, comentarios) DEBE estar en **Inglés**.
- Usa 4 espacios para la sangría.
- Sigue las guías de PEP 8.
- Nunca uses nombres de variables de una sola letra (excepto en list comprehensions muy obvias).

---

Al contribuir, aceptas que tus contribuciones estarán bajo la licencia **GPL-3.0**.
