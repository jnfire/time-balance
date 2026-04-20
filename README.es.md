# time-balance 🕒

> Una herramienta de terminal ligera y profesional para registrar tus jornadas laborales y controlar tu saldo acumulado de horas.

[Read in English 🇺🇸](README.md)

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

La interfaz detecta automáticamente el idioma de tu sistema (soporta inglés y español). Puedes registrar nuevas jornadas, ver tu historial reciente o importar/exportar tus datos.

### 2. Comandos Rápidos (Modo Directo)
Consulta tu estado sin entrar al menú:

```bash
# Ver solo tu saldo acumulado actual
time-balance --status

# Listar los últimos 10 días registrados
time-balance --list 10

# Forzar un idioma específico
time-balance --lang es

# Consultar la versión instalada
time-balance --version
```

---

## Características Principales

- ✅ **Registro ágil**: Introduce horas y minutos de forma sencilla.
- ✅ **Seguridad ante todo**: Escritura atómica de datos y backups automáticos en operaciones críticas.
- ✅ **Multi-idioma**: Cambia sin problemas entre inglés y español.
- ✅ **Importación flexible**: Combina historiales de diferentes dispositivos (merge) o restaura copias completas.
- ✅ **Sin dependencias**: 100% Python estándar. Funciona en Windows, macOS y Linux.
- ✅ **Privacidad absoluta**: Todo se guarda localmente en un archivo JSON legible.

---

## Configuración Avanzada

### Ubicación del historial
Por defecto, la aplicación crea `historial_hours.json` en la carpeta actual. Si prefieres centralizarlo, define la variable de entorno:

```bash
export HISTORIAL_PATH="~/.config/mi_historial.json"
```

### Jornada Base
La aplicación usa por defecto **7h 45m**. Puedes modificarla a través del menú interactivo en la configuración del proyecto.

---

## Próximos Pasos (Roadmap) 🚀

Estamos trabajando para llevar `time-balance` al siguiente nivel:

- 🗄️ **Migración a SQLite**: Evolucionar el almacenamiento interno a una base de datos robusta para mejorar la integridad y velocidad, manteniendo JSON como estándar de importación/exportación.
- 📂 **Gestión Multiproyecto**: Permitir el cambio rápido entre diferentes contextos de trabajo desde una instalación centralizada.
- ☁️ **Sincronización Inteligente**: Ubicación configurable para facilitar el uso en carpetas compartidas (Dropbox, Drive) y backups automáticos.

---

## Desarrollo y Contribuciones

Si quieres contribuir o entender cómo funciona internamente:
- [**ARCHITECTURE.es.md**](docs/es/ARCHITECTURE.es.md): Diseño y módulos del sistema.
- [**DEVELOPMENT.es.md**](docs/es/DEVELOPMENT.es.md): Guía técnica para desarrolladores.
- [**CONTRIBUTING.es.md**](docs/es/CONTRIBUTING.es.md): Cómo enviar mejoras y traducciones.

## Licencia

Este proyecto es Open Source bajo la licencia [GPL-3.0](LICENSE).
