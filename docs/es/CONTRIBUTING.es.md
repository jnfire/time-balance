# Contribuyendo a time-balance

En primer lugar, ¡gracias por considerar contribuir a `time-balance`!

## ¿Cómo puedo contribuir?

### Reportando Bugs
- Comprueba si el error ya ha sido reportado en la sección de Issues.
- Si no, abre un nuevo issue con un título claro y pasos para reproducirlo.

### Sugiriendo Mejoras
- Abre un issue de mejora para discutir tu idea antes de escribir el código.

### Añadiendo Nuevos Idiomas (i18n)
Queremos que `time-balance` sea accesible para todos. Añadir un nuevo idioma es ahora más fácil que nunca:

1. Navega a `time_balance/i18n/locales/`.
2. Copia `en.json` a un nuevo archivo nombrado con el código de tu idioma (ej. `fr.json`, `de.json`).
3. Traduce los valores en el archivo JSON.
4. Envía un Pull Request.

### Mejorando la Documentación
- Corrige erratas o errores gramaticales.
- Traduce los archivos de documentación a otros idiomas.

## Proceso de Desarrollo

1. **Haz un fork del repo** y crea tu rama desde `main`.
2. **Configura tu entorno** (Python 3.8+).
3. **Ejecuta en modo desarrollo** usando `./main.py`.
4. **Sigue los Estándares de Estilo**:
   - El código interno DEBE estar en **Inglés**.
   - Prohibidas las variables de una sola letra (mínimo 3 caracteres).
   - Usa `ui.interface` para cualquier entrada/salida por consola.
5. **Asegúrate de que los tests pasen**: `python3 -m unittest discover tests`.
6. **Envía un Pull Request**.

## Guía de Estilo
- **Naming Descriptivo**: Usa nombres que expliquen la intención (ej. `active_project_id` en lugar de `id`).
- **Lógica DRY**: Centraliza las operaciones de datos en el dominio `database`.
- **Independencia de UI**: Nunca importes `Rich` fuera del directorio `ui/`.

---

Al contribuir, aceptas que tus contribuciones estarán bajo la licencia **GPL-3.0**.
