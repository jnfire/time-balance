# Guía de Uso: Interfaz CLI

`time-balance` ofrece una interfaz dual: un menú interactivo para el uso diario y comandos directos para consultas rápidas.

## Comandos Directos (Modo Rápido)

Puedes consultar información sin entrar al menú interactivo usando flags:

```bash
# Ver el saldo acumulado actual
time-balance --status

# Listar los últimos 10 registros
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

### Menú Principal

La interfaz detecta automáticamente el idioma de tu sistema, pero puedes cambiarlo en la configuración.

```
==================================================
   PROYECTO: NOMBRE DEL PROYECTO
   SALDO TOTAL ACUMULADO: +2h 15m
   (Base diaria: 7h 45m)
==================================================

Opciones:
1. Registrar jornada (o corregir día)
2. Ver últimos registros
3. Configurar proyecto (nombre/jornada)
4. Exportar historial a archivo
5. Importar historial desde archivo
6. Salir

Elige opción: _
```

## Opciones Detalladas

### 1. Registrar Jornada
Permite anotar las horas trabajadas. Si el día ya existe, pedirá confirmación para sobrescribir. Calcula automáticamente la diferencia respecto a la jornada base configurada para **ese proyecto**.

### 2. Ver Últimos Registros
Muestra una tabla con los 5 registros más recientes, incluyendo las horas trabajadas y el impacto en el saldo (positivo o negativo).

### 3. Configurar Proyecto
Permite personalizar el nombre del proyecto y la jornada base (horas/minutos) para el archivo actual. Esto se guarda en los metadatos del JSON.

### 4. Exportar Historial
Crea una copia de seguridad en formato JSON estructurado en la ruta que elijas.

### 5. Importar Historial
- **Modo Merge**: Combina datos externos con los actuales. Los datos importados ganan en caso de conflicto de fecha.
- **Modo Overwrite**: Reemplaza todo el archivo (metadatos y registros) por el nuevo. Crea un backup automático antes de proceder.

## Configuración Mediante Variables de Entorno

Puedes centralizar tu historial definiendo la ruta en tu archivo de configuración de shell (`.bashrc` o `.zshrc`):

```bash
export HISTORIAL_PATH="~/.config/time-balance/main_history.json"
```

---

## Consejos de Uso
- Presiona **ENTER** en el campo de fecha para usar hoy rápidamente.
- Usa `--status` en tus scripts de automatización para ver tu saldo al iniciar la terminal.
- Exporta tus datos regularmente si no usas una carpeta sincronizada.
