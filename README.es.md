# time-balance 🕒

> Una herramienta de terminal profesional y global para gestionar múltiples proyectos, registrar jornadas laborales y controlar tu saldo de horas.

[Read in English 🇺🇸](README.md)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Descripción

`time-balance` es una aplicación de terminal **global** diseñada para la productividad. Ya no depende de archivos locales; todos tus proyectos y registros se almacenan en una base de datos SQLite centralizada. Cuenta con una arquitectura modular basada en dominios, una capa de UI desacoplada y un sistema de localización robusto basado en JSON.

---

## Instalación

### Desde archivos de distribución (Release)
Si has descargado los archivos de la versión (ej: `time_balance-0.5.0-py3-none-any.whl`), puedes instalarlo directamente:

```bash
# Instalar el archivo Wheel
pip install time_balance-0.5.0-py3-none-any.whl
```

### Desde el código fuente
Para instalar la aplicación desde el código:

```bash
# Clonar y entrar al directorio
git clone <repo-url>
cd time-balance

# Instalar globalmente
pip install .
```


### Para Desarrolladores
Si deseas contribuir, recomendamos usar el punto de entrada directo:

```bash
# Ejecutar sin instalar
./main.py --version
```

---

## Uso

### 1. Centro de Control (Menú Interactivo)
Simplemente ejecuta el comando desde cualquier carpeta:

```bash
time-balance
```

### 2. Navegación Intuitiva
La interfaz utiliza un sistema de navegación estandarizado:
- **Números (1-5)** para seleccionar acciones principales.
- **Letras (V, N, P)** para navegación: `V` para volver, `N`/`P` para paginar el historial.

### 3. Comandos Rápidos
Consulta tu estado sin entrar al menú:

```bash
# Saldo del proyecto activo
time-balance --status

# Últimos 10 registros del proyecto activo
time-balance --list 10
```

---

## Características Principales

- ✅ **Arquitectura por Dominios**: Separación clara entre CLI, Base de Datos e interfaz.
- ✅ **Abstracción de UI**: Desacoplada de librerías visuales para máxima flexibilidad.
- ✅ **Localización en JSON**: Añade idiomas fácilmente mediante archivos externos.
- ✅ **Caché de Alto Rendimiento**: Actualizaciones de saldo atómicas e instantáneas.
- ✅ **Backend SQLite**: Persistencia robusta siguiendo estándares XDG.
- ✅ **Multiproyecto**: Gestiona diferentes contextos de trabajo de forma independiente.

---

## Desarrollo y Contribuciones

Si quieres contribuir o entender el funcionamiento interno:
- [**ARCHITECTURE.md**](docs/ARCHITECTURE.md): Diseño del sistema, módulos y dominios.
- [**DEVELOPMENT.md**](docs/DEVELOPMENT.md): Guía técnica para desarrolladores.
- [**CONTRIBUTING.md**](docs/CONTRIBUTING.md): Cómo enviar mejoras y traducciones.

## Licencia

Este proyecto es Open Source bajo la licencia [GPL-3.0](LICENSE).
