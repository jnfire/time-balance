# Guía de Uso: Interfaz CLI

`time-balance` ofrece una interfaz dual: un menú interactivo para el uso diario y comandos directos para consultas rápidas. En la versión 0.3.0, la aplicación es **global** y soporta **múltiples proyectos**.

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

### Menú Principal

La interfaz detecta automáticamente el idioma de tu sistema. Muestra el estado del **proyecto activo**.

```
==================================================
   PROYECTO: MI PROYECTO DE TRABAJO
   SALDO TOTAL ACUMULADO: +2h 15m
   (Base diaria: 7h 45m)
==================================================

Opciones:
1. Registrar jornada (o corregir día)
2. Ver últimos registros
3. Gestionar proyectos (cambiar/crear/editar)
4. Exportar historial a archivo
5. Importar historial desde archivo
6. Salir

Elige opción: _
```

## Opciones Detalladas

### 1. Registrar Jornada
Permite anotar las horas trabajadas para una fecha (por defecto hoy). Calcula la diferencia respecto a la jornada base del **proyecto activo actual**.

### 2. Ver Últimos Registros
Muestra los últimos 5 registros (o los que especifiques) para el proyecto activo.

### 3. Gestionar Proyectos
Abre un submenú para:
- **Cambiar de proyecto**: Cambiar cuál es el proyecto activo a nivel global.
- **Crear nuevo proyecto**: Inicializar un nuevo contexto de trabajo con su propia jornada base.
- **Editar proyecto**: Cambiar el nombre o la jornada base del proyecto actual.

### 4. Exportar Historial
Exporta los datos del proyecto activo a un archivo JSON estructurado.

### 5. Importar Historial
Importa datos desde un archivo JSON hacia el **proyecto activo actual**.
- **Modo Merge**: Añade nuevos registros y actualiza los existentes.
- **Modo Overwrite**: Borra todos los registros actuales antes de importar.

---

## Persistencia de Datos
Los datos se guardan en una base de datos SQLite centralizada. Ya no necesitas preocuparte por archivos `historial_hours.json` en las carpetas de tus proyectos, a menos que quieras exportarlos o migrarlos.

### Rutas por Defecto
- **macOS**: `~/Library/Application Support/time-balance/`
- **Linux**: `~/.local/share/time-balance/`
- **Windows**: `%APPDATA%/time-balance/`
