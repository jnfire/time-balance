# 🕐 Real-Time Timer Feature

## Descripción General
Modalidad de registro de jornada en tiempo real sin necesidad de introducir horas manualmente al final del día. Coexiste con el registro manual tradicional.

### Flujo Principal
1. **Iniciar timer** → Crea/recupera registro para hoy en modo timer activo
2. **Pausar/Reanudar** → Dentro de la misma sesión (menú bloqueante)
3. **Persistencia automática** → Guarda elapsed cada 5 segundos
4. **Auto-finaliza a medianoche** → Cierra registro y genera uno nuevo automáticamente
5. **Manejo de conflictos** → Si existe registro manual previo: preguntar (merge/replace/cancel)

---

## 🏗️ Diseño de Arquitectura

### Base de Datos

**❌ Sin cambios en `records`** — Tabla mantiene estructura actual:
```
id, project_id, date, hours, minutes, difference, created_at
```

**Persistencia Timer:**
- Al entrar al timer: recuperar `hours` y `minutes` del record de hoy (si existe)
- Durante sesión: contador en memoria (segundos acumulados desde inicio)
- Cada 5 seg: convertir (previous_hours + previous_minutes + session_seconds) → nuevas horas/minutos, guardar en BD
- Al finalizar: transacción atómica con `difference` y `total_balance`

---

### Nuevos Métodos en `DatabaseManager`

#### Operaciones Timer

```python
def get_or_create_today_record(self, project_id: int) -> Dict:
    """
    Obtiene el record de hoy para el proyecto, o lo crea vacío (0h 0m).
    
    Returns:
        {
            'record_id': int,
            'hours': int,
            'minutes': int,
            'date': str (YYYY-MM-DD)
        }
    """

def update_record_time(self, record_id: int, total_hours: float, total_minutes: float):
    """
    Actualiza horas/minutos del record (llamado cada 5 seg durante timer).
    Calcula difference respecto a base_hours.
    NO actualiza total_balance (eso es solo al finalizar).
    """

def finalize_timer(self, record_id: int, total_hours: float, total_minutes: float):
    """
    Finaliza el timer:
    - Establece hours/minutes finales
    - Calcula difference respecto a base_hours
    - Actualiza total_balance del proyecto (caché incremental)
    - Una transacción atómica
    """
```

---

### Nuevo Módulo: `cli/timer.py`

#### Estructura de Datos (En Memoria)

```python
class TimerSession:
    """Estado del timer, completamente en memoria durante la sesión."""
    def __init__(self, record_id: int, project_id: int, base_hours: int, base_minutes: int,
                 initial_hours: int = 0, initial_minutes: int = 0):
        self.record_id = record_id
        self.project_id = project_id
        self.base_hours = base_hours
        self.base_minutes = base_minutes
        
        # Estado inicial (recuperado de BD)
        self.initial_hours = initial_hours
        self.initial_minutes = initial_minutes
        
        # Estado del timer (en RAM)
        self.session_elapsed_seconds = 0    # Segundos sumados desde que inició ESTA sesión
        self.paused_at = None               # Timestamp unix (None = activo)
        self.start_time = None              # Timestamp de inicio de sesión
        self.last_persist = time.time()     # Última persistencia a BD
    
    def get_total_hours_minutes(self) -> (int, int):
        """Retorna: horas/minutos totales (inicial + sesión actual)."""
        total_seconds = (self.initial_hours * 3600 + self.initial_minutes * 60) + self.session_elapsed_seconds
        total_hours = total_seconds // 3600
        total_minutes = (total_seconds % 3600) // 60
        return total_hours, total_minutes
```

#### Funciones Principales

```python
def show_timer_menu(active_project_id: int):
    """
    Menú interactivo bloqueante del timer.
    
    Flujo:
    1. Obtiene/crea record para hoy
    2. Pregunta si merging (si existe manual)
    3. Inicia TimerSession en memoria
    4. Loop: actualiza visual cada 1 seg
    5. Maneja inputs: P(ausa), R(eanudar), F(inalizar), C(ancelar)
    6. Al finalizar: guarda hours/minutes EN BD, vuelve a menú principal
    """

def _render_timer_screen(timer_session: TimerSession, project_name: str, paused: bool):
    """
    Renderiza pantalla bloqueante del timer.
    Muestra: contador, estado (paused/active), balance estimado, controles.
    """

def _timer_loop(timer_session: TimerSession, project_name: str, base_hours: int, base_minutes: int):
    """
    Loop principal del timer (en memoria):
    - Captura input sin bloquear
    - Actualiza elapsed_seconds cada frame
    - Renderiza visual cada 1 seg
    - Verifica si llegó medianoche (auto-finaliza)
    - Retorna: 'finalized' | 'paused' | 'cancelled'
    """

def _convert_seconds_to_hours_minutes(elapsed_sec: int) -> (int, int):
    """Helper para conversión."""
```

---

### Nuevos Componentes UI: `ui/interface.py`

```python
def render_timer_display(total_hours: int, total_minutes: int, total_seconds: int, 
                         is_paused: bool, project_name: str, base_time_str: str, 
                         estimated_balance: str):
    """
    Renderiza el display bloqueante del timer.
    - Contador grande y visible (total)
    - Estado (ACTIVE / PAUSED)
    - Balance estimado actual vs base
    - Controles: [P]ause | [R]esume | [F]inish | [C]ancel
    """

def render_timer_finalized_summary(total_hours: float, total_minutes: float, 
                                    balance_delta: int):
    """
    Resumen final al terminar timer.
    Muestra: tiempo total, diferencia con base, nuevo balance.
    """
```

---

### Localización: `i18n/locales/*.json`

**En `en.json` y `es.json`:**

```json
{
  "timer.title": "Real-Time Timer",
  "timer.menu_option": "4. Real-Time Timer",
  "timer.start_message": "Starting timer for {project_name}...",
  "timer.elapsed": "{hours}h {minutes}m {seconds}s",
  "timer.status_active": "● ACTIVE",
  "timer.status_paused": "⏸ PAUSED",
  "timer.estimated_balance": "Estimated balance: {balance}",
  "timer.controls": "[P]ause | [R]esume | [F]inish | [C]ancel",
  "timer.finalized": "✓ Timer saved successfully",
  "timer.finalized_summary": "Total: {hours}h {minutes}m | Balance: {balance}",
  "timer.auto_finalized": "ℹ Timer auto-finalized at midnight",
  "timer.cancelled": "Timer cancelled (no record saved)",
  "timer.error_create": "Error creating timer session"
}
```

---

## 📋 Plan de Implementación

| # | Tarea | Descripción | Dependencias |
|----|-------|-------------|--------------|
| 1 | `db-timer-methods` | Implementar 3 métodos en DatabaseManager (get_or_create_today_record, update_record_time, finalize_timer) | — |
| 2 | `ui-timer-components` | Componentes visuales en `ui/interface.py` (render_timer_display, render_timer_finalized_summary) | — |
| 3 | `cli-timer-module` | Crear `cli/timer.py` con TimerSession y lógica interactiva | 1, 2 |
| 4 | `cli-main-integration` | Integrar opción "4. Real-Time Timer" en menú | 3 |
| 5 | `i18n-timer-strings` | Agregar keys a `en.json` y `es.json` | — |
| 6 | `test-timer-suite` | Tests unitarios e integración (persistencia, recuperación, todos flujos) | 1, 3 |
| 7 | `validation-full` | Ejecutar tests 100%, validar funcionalidad | 5, 6 |

---

## ⚙️ Detalles de Implementación

## ⚙️ Detalles de Implementación

## ⚙️ Detalles de Implementación

### 1️⃣ Timer con Persistencia en horas/minutos

**Entrada al timer:**
```python
record = db.get_or_create_today_record(project_id)
# Si es nuevo: record = {'hours': 0, 'minutes': 0, ...}
# Si existe: record = {'hours': 8, 'minutes': 30, ...}

timer_session = TimerSession(
    record_id=record['record_id'],
    initial_hours=record['hours'],
    initial_minutes=record['minutes']
)
```

**Durante sesión:**
- `session_elapsed_seconds`: contador en RAM que se suma
- `get_total_hours_minutes()`: retorna (initial + session) convertido a horas/minutos

**Persistencia cada 5 seg:**
```python
total_h, total_m = timer_session.get_total_hours_minutes()
db.update_record_time(record_id, total_h, total_m)  # Guardar en BD
# El siguiente ciclo, si se apaga, recuperará estos valores
```

### 2️⃣ Loop del Timer
```python
timer_session = TimerSession(..., initial_hours=record['hours'], initial_minutes=record['minutes'])
start_time = time.time()
last_render = time.time()
last_persist = time.time()

while timer_running:
    now = time.time()
    
    # Calcular elapsed de ESTA sesión (sin persistir)
    if timer_session.paused_at:
        session_elapsed = timer_session.session_elapsed_seconds
    else:
        session_elapsed = timer_session.session_elapsed_seconds + int(now - start_time)
    
    # Total para mostrar
    total_h, total_m = timer_session.get_total_hours_minutes()
    
    # Renderizar cada 1 seg
    if now - last_render >= 1:
        _render_timer_screen(total_h, total_m, paused=timer_session.paused_at is not None)
        last_render = now
    
    # PERSISTIR CADA 5 SEG (EN HORAS/MINUTOS)
    if now - last_persist >= 5 and not timer_session.paused_at:
        db.update_record_time(record_id, total_h, total_m)
        timer_session.initial_hours = total_h
        timer_session.initial_minutes = total_m
        timer_session.session_elapsed_seconds = 0  # Reset sesión
        start_time = time.time()
        last_persist = now
    
    # Capturar input
    command = _get_nonblocking_input()
    if command == 'p': 
        timer_session.paused_at = time.time()
    elif command == 'r': 
        timer_session.paused_at = None
        start_time = time.time()
    elif command == 'f': 
        finalize(timer_session, total_h, total_m); break
    
    # Verificar medianoche
    if _has_crossed_midnight():
        db.update_record_time(record_id, total_h, total_m)  # Guardar antes de cerrar
        break
```

### 3️⃣ Recuperación al Reabrir
```python
record = db.get_or_create_today_record(project_id)
if record['hours'] > 0 or record['minutes'] > 0:
    ui.show_resume_prompt(record['hours'], record['minutes'])
    # Si sí → crear TimerSession(initial_hours=record['hours'], initial_minutes=record['minutes'])
```

### 4️⃣ Finalizar
```python
# Total calculado
total_h, total_m = timer_session.get_total_hours_minutes()

# Guardar en BD (transacción atómica con difference y balance)
db.finalize_timer(record_id, total_h, total_m)
```

### 3️⃣ Nombres (Convención ≥3 caracteres)
- ✅ `session_elapsed_seconds` (no `ses_elp`)
- ✅ `initial_hours`, `initial_minutes`
- ✅ `project_name` (no `proj`, `pnm`)
- ✅ `paused_at` (no `psd`)

### 4️⃣ UI Desacoplada
- ❌ NO: `import Rich` en `cli/timer.py`
- ✅ SÍ: `from ..ui.interface import render_timer_display`

---

## ✅ Criterios de Aceptación

- [ ] **Sin cambios en BD**: tabla `records` mantiene estructura original (solo usa `hours`, `minutes`)
- [ ] Obtener/crear record para hoy: recupera `hours` y `minutes` correctamente
- [ ] Timer en memoria: `session_elapsed_seconds` se suma a `initial_hours/minutes`
- [ ] Persistencia cada 5 seg: guardas total (initial + session) en `hours/minutes` de BD
- [ ] Pausar/reanudar: sin perder tiempo acumulado
- [ ] Renderización: visual actualiza cada 1 seg (mostrando total_hours, total_minutes)
- [ ] **Sin conflictos**: tiempo siempre es incremental (suma automática)
- [ ] Auto-finaliza a medianoche: persiste sesión actual y cierra
- [ ] Finalizar: guarda transacción atómica (hours, minutes, difference, actualiza balance)
- [ ] Textos localizados en es/en
- [ ] Tests: 100% cobertura (persistencia cada 5 seg, todos flujos)
- [ ] Sin imports de `Rich` fuera de `ui/interface.py`
- [ ] Todos los tests pasan: `python3 -m unittest discover -v tests`

---

## 📝 Notas
- La fecha se guarda en formato ISO (YYYY-MM-DD, UTC)
- El timer siempre es para el día actual (no permite cambiar fecha)
- **En BD**: siempre persiste `hours` y `minutes` totales (recuperables, no hay estado separado)
- **En memoria**: solo `session_elapsed_seconds` (segundos de esta sesión)
- **Sin conflictos**: tiempo siempre es incremental (manual + timer suma automáticamente)
- Si usuario cancela: se pierde lo de esta sesión, pero BD tiene lo anterior
- Auto-finaliza a medianoche: persiste y cierra automáticamente
