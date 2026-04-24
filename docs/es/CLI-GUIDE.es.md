# Guía de Uso: Interfaz CLI

`time-balance` ofrece una interfaz dual: un menú interactivo para el uso diario y comandos directos para consultas rápidas. En la versión actual, la aplicación es **global** y soporta **múltiples proyectos** con una navegación optimizada.

## Comandos Directos (Modo Rápido)

Puedes consultar información o realizar acciones sin entrar al menú interactivo usando flags:

```bash
# Ver el saldo acumulado del proyecto activo
time-balance --status

# Listar los últimos 10 registros del proyecto activo
time-balance --list 10

# Migrar un archivo JSON de legado a un nuevo proyecto global
time-balance --migrate ./ruta/al/historial.json

# Forzar idioma (en/es)
time-balance --lang en

# Ver versión
time-balance --version
```

## Interfaz Interactiva

Para iniciar el centro de control completo:

```bash
time-balance
```

### Navegación Estándar
Para una experiencia fluida, `time-balance` utiliza un sistema híbrido:
- **Números (1-5)**: Para seleccionar acciones y opciones de configuración.
- **Letras**: Para navegación y movimiento.
  - `V`: Volver al menú anterior.
  - `N`: Página siguiente (en historial).
  - `P`: Página anterior (en historial).

---

### Menú Principal

El menú principal es sobrio y directo, mostrando siempre el **Dashboard** del proyecto activo en la parte superior.

```
1. Registrar jornada
2. Ver registros
3. Configuración
4. Cambiar proyecto
5. Salir
```

## Secciones Detalladas

### 1. Registrar Jornada
Permite anotar las horas trabajadas para una fecha (por defecto hoy). Calcula la diferencia respecto a la jornada base del proyecto activo.

### 2. Ver Registros (Paginado)
Muestra el historial completo del proyecto en tablas de 10 registros.
- Usa `N` y `P` para navegar entre páginas.
- Usa `V` para volver al menú principal.

### 3. Configuración
Submenú dividido en secciones para una gestión clara:
- **Ajustes del Proyecto**: Editar nombre, ajustar jornada base (horas/minutos) e idioma.
- **Gestión de Datos**: Opciones de Importación y Exportación de archivos JSON.
- Usa `V` para volver.

### 4. Cambiar Proyecto
Sección dedicada a la gestión de multi-tenencia.
- Permite seleccionar un proyecto existente de la lista.
- Permite crear un nuevo proyecto desde cero.
- Usa `V` para volver.

---

## Persistencia de Datos
Los datos se guardan en una base de datos SQLite centralizada. Ya no necesitas preocuparte por archivos locales en las carpetas de tus proyectos.

### Rutas por Defecto
- **macOS**: `~/Library/Application Support/time-balance/`
- **Linux**: `~/.local/share/time-balance/`
- **Windows**: `%APPDATA%/time-balance/`
