# time-balance 🕒

> Una herramienta de terminal profesional y global para gestionar múltiples proyectos, registrar jornadas laborales y controlar tu saldo de horas.

[Read in English 🇺🇸](README.md)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Descripción

`time-balance` es ahora una aplicación de consola **global**. Ya no depende de dónde la ejecutes; tus proyectos y registros se almacenan en una base de datos SQLite centralizada en tu sistema. Calcula automáticamente la diferencia diaria respecto a una jornada base y mantiene un saldo acumulado por cada proyecto de forma independiente.

---

## Instalación Global

Para instalar la aplicación de forma que esté disponible en cualquier terminal:

```bash
# Clonar y entrar al directorio
git clone <url-del-repo>
cd time-balance

# Instalar de forma global en tu usuario
pip install .
```

---

## Uso de la aplicación

### 1. Centro de Control (Menú Interactivo)
Ejecuta el comando desde cualquier carpeta para abrir el gestor:

```bash
time-balance
```

### 2. Gestión de Proyectos
Dentro del menú, la **opción 3** te permite crear nuevos proyectos (ej: "Cliente A", "Proyecto Personal") y cambiar entre ellos. La aplicación recordará cuál fue el último proyecto que usaste la próxima vez que la abras.

### 3. Migración de datos antiguos (v0.2.x)
Si tienes archivos `historial_hours.json` de versiones anteriores, puedes importarlos fácilmente a un nuevo proyecto en la base de datos global:

```bash
time-balance --migrate ./ruta/al/historial_hours.json
```

### 4. Consultas Rápidas
Consulta tu estado sin entrar al menú:

```bash
# Ver el saldo del proyecto activo
time-balance --status

# Listar los últimos 10 registros del proyecto activo
time-balance --list 10

# Forzar un idioma (es/en)
time-balance --lang es
```

---

## Características de la Versión 0.3.0

- ✅ **Almacenamiento SQLite**: Persistencia robusta y profesional en rutas estándar (XDG).
- ✅ **Multi-proyecto**: Gestiona diferentes contextos de trabajo desde una única instalación.
- ✅ **Instalación Global**: Accede a tus datos desde cualquier ubicación en la terminal.
- ✅ **Migración Automática**: Comando dedicado para traer tus datos de la era JSON.
- ✅ **Privacidad**: Todo sigue siendo 100% local en tu equipo.

---

## Ubicación de los datos
La base de datos se guarda automáticamente en:
- **macOS**: `~/Library/Application Support/time-balance/time_balance.db`
- **Linux**: `~/.local/share/time-balance/time_balance.db`
- **Windows**: `%APPDATA%/time-balance/time_balance.db`

---

## Desarrollo y Contribuciones

Si quieres contribuir o entender cómo funciona internamente:
- [**ARCHITECTURE.es.md**](docs/es/ARCHITECTURE.es.md): Diseño y módulos del sistema.
- [**DEVELOPMENT.es.md**](docs/es/DEVELOPMENT.es.md): Guía técnica para desarrolladores.
- [**CONTRIBUTING.es.md**](docs/es/CONTRIBUTING.es.md): Cómo enviar mejoras y traducciones.

## Licencia

Este proyecto es Open Source bajo la licencia [GPL-3.0](LICENSE).
