# Guía de Uso: Interfaz CLI Interactiva

`time-balance` proporciona una interfaz interactiva de línea de comandos basada en menús. No hay argumentos de línea de comandos ni subcomandos.

## Inicio de la Aplicación

```bash
time-balance
```

## Menú Principal

Al ejecutar `time-balance`, verás el menú principal:

```
==================================================
   SALDO TOTAL ACUMULADO: [balance acumulado]
   (Base diaria: 7h 45m)
==================================================

Opciones:
1. Registrar jornada (o corregir día)
2. Ver últimos registros
3. Exportar historial a archivo
4. Importar historial desde archivo
5. Salir

Elige opción: _
```

## Opciones Detalladas

### 1. Registrar Jornada

Permite registrar las horas trabajadas en un día o corregir un registro anterior.

**Flujo de interacción:**

```
Elige opción: 1

Ingresa fecha (YYYY-MM-DD) o presiona Enter para hoy [2026-04-16]: 
Ingresa horas trabajadas: 8
Ingresa minutos trabajados: 30
```

**Comportamiento:**
- Si la fecha ya existe, solicita confirmación antes de sobrescribir
- Calcula automáticamente la diferencia respecto a la jornada base (7h 45m)
- Guarda los cambios en el archivo de historial
- Retorna al menú principal

**Ejemplo de sobrescritura:**

```
¿El día 2026-04-16 ya existe (8h 30m, diferencia: +0h 45m). 
¿Deseas sobrescribir? (s/n): s
✓ Jornada registrada/actualizada
```

### 2. Ver Últimos Registros

Muestra los 5 registros más recientes del historial.

**Flujo de interacción:**

```
Elige opción: 2

Últimos registros:
2026-04-16: 8h 30m (diferencia: +0h 45m)
2026-04-15: 7h 45m (diferencia: 0h 0m)
2026-04-14: 6h 30m (diferencia: -1h 15m)
2026-04-13: 9h 0m (diferencia: +1h 15m)
2026-04-12: 8h 15m (diferencia: +0h 30m)
```

**Información mostrada:**
- Fecha en formato YYYY-MM-DD
- Horas y minutos trabajados
- Diferencia respecto a la jornada base (positiva/negativa)

### 3. Exportar Historial

Crea una copia de tu historial completo en un archivo JSON externo.

**Flujo de interacción:**

```
Elige opción: 3

Ingresa ruta de destino para exportar: /path/a/mi_export.json
✓ Historial exportado a: /path/a/mi_export.json
```

**Características:**
- El archivo se crea con formato JSON
- Si el archivo ya existe, se sobrescribe sin advertencia
- Las rutas se pueden expresar con `~` (home directory)
- Retorna la ruta absoluta del archivo creado

**Formato del archivo exportado:**

```json
{
    "2026-04-16": {
        "horas": 8,
        "minutos": 30,
        "diferencia": 0.75
    },
    "2026-04-15": {
        "horas": 7,
        "minutos": 45,
        "diferencia": 0.0
    }
}
```

### 4. Importar Historial

Incorpora datos desde un archivo JSON externo.

**Flujo de interacción:**

```
Elige opción: 4

Ingresa ruta de origen para importar: /path/a/mi_export.json
Elige modo de importación (merge/overwrite) [merge]: 
✓ Historial importado: 5 entradas procesadas
```

**Modos de Importación:**

#### Modo `merge` (predeterminado)
```
merge
```
- Combina el historial importado con el existente
- **Los datos importados tienen preferencia** en caso de conflicto
- Si una fecha existe en ambos, la versión importada sobrescribe la local
- Recomendado para: restaurar datos sin perder registros locales recientes

**Ejemplo:**
```
Local: {"2026-04-16": {...}, "2026-04-15": {...}}
Importado: {"2026-04-16": {...}, "2026-04-14": {...}}
Resultado: {"2026-04-16": {...(importado)}, "2026-04-15": {...}, "2026-04-14": {...}}
```

#### Modo `overwrite`
```
overwrite
```
- Reemplaza todo el historial con los datos importados
- **Crea un backup automático** antes de la operación:
  - `historial_horas.json.bak` (siempre actualizado)
  - `historial_horas.json.bak.20260416T111320` (versión con timestamp)
- El backup se puede usar para restaurar datos en caso de error
- Recomendado para: migración completa de datos o restauración de backup

### 5. Salir

Cierra la aplicación y regresa al símbolo del sistema.

```
Elige opción: 5
¡Hasta mañana!
```

## Resolución de Rutas

Cuando se solicita una ruta (en exportar/importar):

1. **Prioridad de búsqueda del archivo de datos** (usado internamente):
   1. Argumento `archivo_path` en funciones de API
   2. Variable de entorno `HISTORIAL_PATH`
   3. `historial_horas.json` en el directorio actual (predeterminado)

2. **Expansión de rutas:**
   - Se expande `~` a tu directorio de inicio
   - Soporta rutas relativas y absolutas

**Ejemplo con variable de entorno:**

```bash
# Usa una ubicación personalizada para el historial
export HISTORIAL_PATH=~/.local/share/time-balance/historial_horas.json
time-balance
```

## Manejo de Errores

- **Fecha inválida:** Se pide reintentar con formato YYYY-MM-DD
- **Entrada numérica inválida:** Se pide reintentar (solo números)
- **Archivo JSON corrupto:** Se retorna un error específico
- **Ruta de exportación no existente:** Se crea el archivo nuevo
- **Ruta de importación no encontrada:** Se muestra error y se regresa al menú

## Ejemplos Comunes

### Workflow típico del día

```bash
$ time-balance

# Opción 1: registrar horas del día
Elige opción: 1
Ingresa fecha (YYYY-MM-DD) o presiona Enter para hoy [2026-04-16]: 
Ingresa horas trabajadas: 8
Ingresa minutos trabajados: 15

# Opción 2: ver el saldo actual
Elige opción: 2
# Muestra los últimos registros

# Opción 5: salir
Elige opción: 5
```

### Backup y Restauración

```bash
# Exportar (backup manual)
$ time-balance
Elige opción: 3
Ingresa ruta de destino para exportar: ~/backups/historial_backup.json

# ... más tarde, si es necesario ...

# Restaurar completo
$ time-balance
Elige opción: 4
Ingresa ruta de origen para importar: ~/backups/historial_backup.json
Elige modo de importación (merge/overwrite) [merge]: overwrite
# Se crea backup automático antes de restaurar
```

## Consejos

- **Usa Enter** en el campo de fecha para registrar el día actual (más rápido)
- **Exporta regularmente** para tener backups de seguridad externos
- **Utiliza overwrite** solo cuando estés restaurando, usa **merge** para combinar datos
- El **modo interactivo** previene sobrescrituras accidentales pidiendo confirmación
