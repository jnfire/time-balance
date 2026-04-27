# Arquitectura del Proyecto

## Visión General

`time-balance` es una aplicación de terminal profesional diseñada para registrar jornadas laborales y gestionar saldos horarios acumulados. A partir de la versión 0.5.0, la aplicación cuenta con una **arquitectura modular basada en dominios**, una capa de UI desacoplada y un sistema de localización robusto basado en archivos JSON.

## Estructura del Proyecto

La aplicación ha sido reestructurada de un paquete monolítico a dominios funcionales especializados:

```
time-balance/
├── main.py                   # Punto de entrada directo para desarrollo
├── setup.py                  # Configuración de empaquetado y distribución
├── time_balance/             # Código fuente principal
│   ├── cli/                  # Dominio de presentación (Lógica de menús)
│   │   ├── main.py           # Orquestador CLI y punto de entrada
│   │   ├── registration.py   # Flujos de entrada de jornada
│   │   ├── timer.py          # Interfaz del contador en tiempo real
│   │   ├── history.py        # Visualización de registros y paginación
│   │   └── ...               # Submenús (proyectos, configuración, migración)
│   ├── database/             # Dominio de persistencia
│   │   └── manager.py        # DatabaseManager SQLite (lógica DRY)
│   ├── i18n/                 # Dominio de localización
│   │   ├── translator.py     # Motor de traducción con caché
│   │   └── locales/*.json    # Definiciones de cadenas externas
│   ├── ui/                   # Capa de abstracción de UI
│   │   └── interface.py      # Puente de desacoplamiento (implementación Rich)
│   ├── utils/                # Funcionalidades transversales
│   │   ├── calculations.py   # Cálculos y formateo
│   │   └── files.py          # Operaciones de E/S atómicas
│   ├── config.py             # Configuración global de la aplicación
│   └── VERSION               # Fuente única de verdad para la versión
├── tests/                    # Suite de tests adaptada a los dominios
└── docs/                     # Documentación técnica
```

## Principios Arquitectónicos

### 1. **Desacoplamiento de UI (Capa de Abstracción)**
La aplicación está desacoplada de la librería `Rich` mediante `ui/interface.py`. Todos los componentes visuales (cabeceras, tablas, prompts) se invocan a través de métodos genéricos. Esto permite futuras migraciones de frontend (ej. a Textual o una API web) sin tocar la lógica de negocio.

### 2. **Modularización Basada en Dominios**
- **`cli/`**: Maneja el flujo del usuario y la validación de entradas. Dividido en archivos pequeños y tematizados.
- **`database/`**: Centraliza toda la lógica de persistencia. El `DatabaseManager` maneja actualizaciones atómicas y caché de saldos.
- **`i18n/`**: Un dominio independiente para la localización. Soporta carga dinámica de JSON, caché y fallback automático al inglés.

### 3. **Código Limpio y Estándares de Naming**
- **Naming Descriptivo**: Todas las variables y funciones siguen una regla estricta de "No variables de una sola letra" (mínimo 3 caracteres).
- **DRY (Don't Repeat Yourself)**: Las operaciones masivas (como la importación de registros) están centralizadas en la capa de base de datos.

### 4. **Módulo del Contador en Tiempo Real**
El contador (`cli/timer.py`) demuestra la arquitectura basada en dominios en acción:
- **UI Desacoplada**: Toda la lógica de visualización está en `ui/interface.py` (dos funciones de render: `render_timer_running()` y `render_timer_menu_with_display()`).
- **Integración con BD**: Usa `update_record_time()` para actualizaciones incrementales del saldo y `get_or_create_today_record()` para la gestión de sesiones.
- **Actualizaciones Atómicas del Caché**: Cada ciclo del contador actualiza el caché de `total_balance` del proyecto de forma inmediata y atómica.
- **Localización**: Todos los strings (estado del contador, etiquetas, instrucciones) se traducen mediante claves en `i18n/locales/*.json` como `timer_label_elapsed`, `timer_label_status`, `timer_label_balance`.
- **Experiencia de Usuario**: Interfaz mínima — presiona `1` para iniciar, `ENTER` para detener. Auto-guarda cada 60 segundos (solo se guardan minutos; los segundos no se almacenan).

## Flujo de Datos y Rendimiento

La aplicación utiliza una **estrategia de caché incremental** para los saldos totales:
- **Acceso O(1)**: El saldo total se cachea en la tabla `projects`.
- **Actualizaciones Atómicas**: Cada operación de registro dispara una actualización delta del saldo del proyecto.
- **Persistencia**: Impulsada por SQLite con resolución de rutas estándar del sistema (cumplimiento XDG).

## Estrategia de Testing

La suite de pruebas sigue la arquitectura modular:
- **Tests Unitarios**: Lógica matemática en `test_core`.
- **Tests de Integración**: Transacciones de base de datos en `test_storage` y `test_balance_cache`.
- **Mocking de UI**: `test_cli` utiliza la capa de abstracción de UI para simular interacciones sin requerir una terminal real.

## Distribución

Como herramienta profesional, `time-balance` se distribuye como un paquete de Python pero funciona como un ejecutable independiente. El archivo `setup.py` y el `MANIFEST.in` aseguran que todos los recursos no-Python (JSON de idiomas, archivos de versión) se incluyan correctamente.
