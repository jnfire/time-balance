Checklist (resumen rápido)
- [ ] Revisar y mapear funciones actuales en `time_balance/__init__.py`.
- [ ] Diseñar módulos objetivos y asignar funciones a cada uno.
- [ ] Crear nuevos archivos en `time_balance/` y actualizar `__init__.py` para reexportar API.
- [ ] Ejecutar tests y ajustar imports/documentación si es necesario.
- [ ] Iterar según feedback.

## Plan adaptado: Reorganizar `__init__.py` en módulos (con referencia)

Objetivo: dividir `time_balance/__init__.py` (actualmente ~414 líneas) en módulos cohesivos para mejorar la mantenibilidad, facilitar pruebas y mantener una fachada estable para consumidores del paquete.

Estrategia general
- Mantener compatibilidad hacia atrás exportando las funciones públicas desde `time_balance/__init__.py` (estrategia de transición).
- Implementar refactor por pasos, commits atómicos y ejecución de la suite de tests tras cada paso.

Módulos propuestos y asignación de funciones
- `time_balance/storage.py`
  - Responsabilidad: resolución de rutas, lectura/escritura atómica y backups.
  - Contenido: `_resolver_archivo`, `cargar_datos`, `guardar_datos`, `_crear_backup`.

- `time_balance/io.py`
  - Responsabilidad: import/export de historiales y validación de formato.
  - Contenido: `_validar_historial`, `exportar_historial`, `importar_historial`.

- `time_balance/utils.py`
  - Responsabilidad: utilidades puras y constantes.
  - Contenido: `formatear_tiempo`, `calcular_saldo_total`, constantes `HORAS_BASE`, `MINUTOS_BASE`, `ARCHIVO_DATOS`, `ENV_HISTORIAL` (si se desea centralizar aquí).

- `time_balance/cli.py`
  - Responsabilidad: interfaz de usuario (stdin/stdout), `main`.
  - Contenido: `solicitar_fecha`, `registrar_jornada`, `ver_historial`, `main`.

- `time_balance/__init__.py` (fachada)
  - Reexportar API pública: `cargar_datos`, `guardar_datos`, `exportar_historial`, `importar_historial`, `formatear_tiempo`, `calcular_saldo_total`, `main`, etc.
  - Definir `__all__` para controlar la API pública.

Opcional: `time_balance/__main__.py` para permitir `python -m time_balance` (delegará a `cli.main`).

Orden de trabajo (commits atómicos)
1) Preparación
   - Crear rama: `git checkout -b refactor/split-init`.
   - Asegurarse tests pasan antes de empezar.

2) Commit A — Extraer `storage`
   - Crear `time_balance/storage.py` con las funciones correspondientes.
   - Reemplazar en `__init__.py` la implementación por `from .storage import ...` (reexport).
   - Ejecutar tests: `python3 -m unittest discover -v` y arreglar fallos.
   - Commit: `refactor(storage): extraer lógica de persistencia a time_balance/storage.py`

3) Commit B — Extraer `io`
   - Crear `time_balance/io.py` con `_validar_historial`, `exportar_historial`, `importar_historial`.
   - `io` puede importar `storage._resolver_archivo` o `utils` según convenga.
   - Actualizar `__init__.py` para reexportar.
   - Ejecutar tests y corregir.
   - Commit: `refactor(io): extraer import/export y validación`

4) Commit C — Extraer `utils`
   - Crear `time_balance/utils.py` y mover utilidades/constantes.
   - Ajustar `storage`, `io`, `cli` para importar desde `utils`.
   - Ejecutar tests.
   - Commit: `refactor(utils): extraer utilidades y constantes`

5) Commit D — Extraer `cli` y `__main__`
   - Crear `time_balance/cli.py` con la UI y `main`.
   - Añadir `time_balance/__main__.py` con `from .cli import main; main()`.
   - Reexportar `main` en `__init__`.
   - Ejecutar tests y probar `python -m time_balance`.
   - Commit: `refactor(cli): extraer interfaz de usuario y main`

6) Commit E — Limpieza
   - Añadir `__all__` en `__init__.py`.
   - Actualizar documentación si hace falta.
   - Ejecutar tests finales.
   - Commit: `chore(refactor): reexports en __init__ y actualizar docs`

Pruebas y validación
- Ejecutar tras cada commit:
  - `python3 -m unittest discover -v`
  - Probar `python -m time_balance` si `__main__` añadido.

Buenas prácticas y riesgos
- Evitar ciclos de import (diseñar dependencia utils <- storage/io <- cli).
- Reexportar en `__init__` para mantener compatibilidad de imports existentes.
- Añadir tests que cubran `_validar_historial()` con claves inválidas (p. ej. `"foo"`) para prevenir regresiones.

Comandos útiles
```bash
git checkout -b refactor/split-init
# editar archivos...
python3 -m unittest discover -v
git add <archivos>
git commit -m "refactor(<módulo>): ..."
```

¿Quieres que empiece aplicando el primer paso (extraer `storage`) ahora? Si confirmas lo hago, ejecuto tests y te paso el diff/commits para revisión.

