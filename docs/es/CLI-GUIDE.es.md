# Guía de Uso: Interfaz CLI

`time-balance` ofrece una interfaz dual: un menú interactivo para el uso diario y comandos directos para consultas rápidas. En la versión actual, la aplicación es **global** y soporta **múltiples proyectos** con una navegación optimizada.

## Comandos Directos (Modo Rápido)

Puedes consultar información o realizar acciones sin entrar al menú interactivo usando flags:

```bash
# Ver el saldo acumulado del proyecto activo
time-balance --status

# Listar los últimos 10 registros del proyecto activo
time-balance --list 10

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

### 1. Contador en Tiempo Real
Una interfaz simplificada y mínima para registrar tu trabajo en tiempo real:
- **Activación**: Presiona `1` desde el menú principal para iniciar el contador.
- **Interfaz**: Muestra tiempo transcurrido, estado actual (ACTIVO/PAUSADO) y saldo estimado.
- **Colores**: Verde para saldo positivo, rojo para saldo negativo; fácil de leer en terminales claros y oscuros.
- **Flujo de Trabajo**:
  - Presiona `1` para activar e iniciar el contador.
  - El contador guarda automáticamente el progreso cada 60 segundos (solo se guardan minutos; los segundos no se almacenan).
  - Presiona `ENTER` para detener y guardar la sesión actual, volviendo al menú principal.
  - El contador persiste el registro de hoy en la base de datos automáticamente.
- **Diseño**: Diseño visual unificado entre estados activo y pausado con etiquetas explicativas.

### 2. Registrar Jornada
Permite anotar las horas trabajadas para una fecha (por defecto hoy). Calcula la diferencia respecto a la jornada base del proyecto activo.

### 3. Ver Registros (Paginado)
Muestra el historial completo del proyecto en tablas de 10 registros.
- Usa `N` y `P` para navegar entre páginas.
- Usa `V` para volver al menú principal.

### 4. Configuración
Submenú dividido en secciones para una gestión clara:
- **Ajustes del Proyecto**: Editar nombre, ajustar jornada base (horas/minutos) e idioma.
- **Gestión de Datos**: Opciones de Importación y Exportación de archivos JSON.
- Usa `V` para volver.

### 5. Cambiar Proyecto
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
