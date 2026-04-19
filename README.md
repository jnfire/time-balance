# time-balance 🕒

> Una herramienta de terminal ligera y profesional para registrar tus jornadas laborales y controlar tu saldo acumulado de horas.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Descripción

`time-balance` es una aplicación de consola diseñada para personas que necesitan llevar un control riguroso de su tiempo trabajado. Calcula automáticamente la diferencia diaria respecto a una jornada base (7h 45m por defecto) y mantiene un saldo acumulado para que siempre sepas si "debes" horas o tienes saldo a favor.

---

## Instalación rápida

```bash
# Clonar y entrar al directorio
git clone <url-del-repo>
cd time-balance

# Instalar la aplicación
python3 -m pip install .
```

---

## Uso de la aplicación

### 1. Menú Interactivo (Recomendado)
Simplemente ejecuta el comando para abrir el centro de control:

```bash
time-balance
```

Desde aquí puedes registrar nuevas jornadas, ver tu historial reciente o importar/exportar tus datos.

### 2. Comandos Rápidos (Modo Directo)
Si tienes prisa, puedes consultar tu estado sin entrar al menú:

```bash
# Ver solo tu saldo acumulado actual
time-balance --status

# Listar los últimos 10 días registrados
time-balance --list 10

# Consultar la versión instalada
time-balance --version
```

---

## Características Principales

- ✅ **Registro ágil**: Introduce horas y minutos de forma sencilla.
- ✅ **Seguridad ante todo**: Escritura atómica de datos y backups automáticos en operaciones críticas.
- ✅ **Importación flexible**: Combina historiales de diferentes dispositivos (merge) o restaura copias completas.
- ✅ **Sin dependencias**: 100% Python estándar. Funciona en Windows, macOS y Linux.
- ✅ **Respetuoso con tus datos**: Todo se guarda localmente en un archivo JSON legible.

---

## Configuración Avanzada

### Ubicación del historial
Por defecto, la aplicación crea `historial_horas.json` en la carpeta actual. Si prefieres centralizarlo, define la variable de entorno:

```bash
export HISTORIAL_PATH="~/.config/time-balance/mi_historial.json"
```

### Jornada Base
La aplicación usa por defecto **7h 45m**. Si tu jornada es diferente, puedes modificar las constantes en `time_balance/constants.py` y reinstalar.

---

## Próximos Pasos (Roadmap) 🚀

Estamos trabajando para llevar `time-balance` al siguiente nivel:

- 🗄️ **Migración a SQLite**: Evolucionar el almacenamiento interno a una base de datos robusta para mejorar la integridad y velocidad, manteniendo el formato JSON como estándar de importación/exportación.
- 📂 **Gestión Multiproyecto**: Permitir la creación y cambio rápido entre diferentes contextos de trabajo desde una instalación centralizada.
- ☁️ **Sincronización Inteligente**: Configuración simplificada de la ubicación de los datos para facilitar el uso en carpetas compartidas (Dropbox, iCloud, Drive) y copias de seguridad automáticas.
- 🎨 **Interfaz Enriquecida**: Mejora visual de la terminal usando librerías modernas para ofrecer tablas más claras, colores y mejor usabilidad.

*Se aceptan propuestas y contribuciones para seguir mejorando la herramienta.*

## Desarrollo y Contribuciones

Si quieres contribuir o entender cómo funciona internamente:
- [**ARCHITECTURE.md**](docs/ARCHITECTURE.md): Diseño y módulos del sistema.
- [**DEVELOPMENT.md**](docs/DEVELOPMENT.md): Guía técnica para desarrolladores.
- [**CONTRIBUTING.md**](docs/CONTRIBUTING.md): Cómo enviar mejoras.

## Licencia

Este proyecto es Open Source bajo la licencia [GPL-3.0](LICENSE).
