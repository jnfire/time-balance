# Guía de Contribución

Gracias por tu interés en contribuir a `time-balance`. Este documento describe cómo colaborar con el proyecto.

## Filosofía del Proyecto

- **Minimalismo**: Mantener la complejidad baja, usar solo biblioteca estándar de Python
- **Confiabilidad**: Operaciones seguras, backups automáticos, validación rigurosa
- **Simplicidad**: Interfaz clara, documentación accesible
- **Portabilidad**: macOS, Linux, Windows (sin dependencias externas)

## Antes de Contribuir

1. Lee el [README.md](/../../README.md) para entender el proyecto
2. Revisa [ARCHITECTURE.md](ARCHITECTURE.md) para entender el diseño
3. Revisa el [CHANGELOG.md](/../../CHANGELOG.md) para ver el historial

## Configuración del Entorno de Desarrollo

### 1. Clonar el Repositorio

```bash
git clone <url-del-repo>
cd time-balance
```

### 2. Crear Entorno Virtual

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows
```

### 3. Instalar en Modo Desarrollo

```bash
python3 -m pip install -e .
```

Esto instala el paquete en modo editable, permitiendo ver cambios inmediatamente.

### 4. Ejecutar Tests

```bash
python3 -m unittest discover -v
```

Todos los tests deben pasar antes de hacer commit.

## Haciendo Cambios

### 1. Crea una Rama

```bash
git checkout -b feature/mi-caracteristica
# o
git checkout -b fix/correccion-bug
```

### 2. Implementa tu Cambio

- Haz cambios pequeños y enfocados
- Mantén el estilo consistente con el código existente
- Usa nombres descriptivos (variables, funciones)
- Comenta solo lo que necesita aclaración

### 3. Escribe o Actualiza Tests

Para cada cambio en funcionalidad:

- Agrega tests nuevos en `tests/` si necesario
- Actualiza tests existentes si cambias comportamiento
- Todos los tests deben pasar: `python3 -m unittest discover -v`
- Usa `tempfile.TemporaryDirectory()` para tests (no toques archivos reales)

**Ejemplo de test:**

```python
import unittest
import tempfile
import os
from time_balance import guardar_datos, cargar_datos

class TestMiCambio(unittest.TestCase):
    def test_mi_funcionalidad(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            archivo = os.path.join(tmpdir, "test.json")
            datos = {"2026-04-16": {"horas": 8, "minutos": 0, "diferencia": 15}}
            
            guardar_datos(datos, archivo_path=archivo)
            resultado = cargar_datos(archivo_path=archivo)
            
            self.assertEqual(resultado, datos)
```

### 4. Verifica el Estilo

- No hay linter configurado, pero sigue PEP 8
- Máximo 100 caracteres por línea (preferible)
- Usa type hints donde sea posible (funciones nuevas)
- Documenta con docstrings

### 5. Actualiza Documentación

Si tu cambio afecta comportamiento visible:

- Actualiza [CLI-GUIDE.md](CLI-GUIDE.md) (cambios en menú o opciones)
- Actualiza [API-GUIDE.md](API-GUIDE.md) (cambios en funciones públicas)
- Actualiza [ARCHITECTURE.md](ARCHITECTURE.md) (cambios de diseño)
- Actualiza [README.md](/../../README.md) (resumen o características)

### 6. Commit y Push

```bash
git add .
git commit -m "feature: descripción clara del cambio"
git push origin feature/mi-caracteristica
```

**Formato de commit message:**
- `feature: ...` para características nuevas
- `fix: ...` para correcciones
- `docs: ...` para cambios de documentación
- `test: ...` para tests
- `refactor: ...` para reorganización sin cambio funcional

## Pull Request

### 1. Crea el PR

- Título claro: "Add export to CSV" o "Fix date parsing bug"
- Descripción: Explica qué hace, por qué, y cómo testear

### 2. Template de PR

```markdown
## Descripción
Breve descripción del cambio

## Tipo
- [ ] Característica nueva
- [ ] Corrección de bug
- [ ] Cambio de documentación
- [ ] Refactoring

## Testing
- [ ] Agregué tests nuevos
- [ ] Todos los tests pasan
- [ ] Probé manualmente los cambios

## Checklist
- [ ] Mi código sigue el estilo del proyecto
- [ ] Actualicé la documentación
- [ ] No tengo conflictos sin resolver
```

### 3. Revisión

El mantenedor revisará tu PR:
- Cambios pequeños: merge rápido
- Cambios mayores: discusión y sugerencias
- Tests fallando: se rechaza hasta que pasen

## Tipos de Contribución Bienvenidos

### 🟢 Muy Bienvenidas

1. **Correcciones de Bugs**
   - Reporta primero en issue
   - Incluye pasos para reproducir
   - Agrega test que valide la corrección

2. **Mejoras de Documentación**
   - Ejemplos más claros
   - Explicaciones mejoradas
   - Corrección de typos

3. **Tests Adicionales**
   - Cobertura de casos edge
   - Tests de rendimiento
   - Validación de manejo de errores

### 🟡 Requiere Discusión

1. **Características Nuevas**
   - Abre issue primero para discutir
   - Debe mantenerse el minimalismo
   - Evitar dependencias externas

2. **Cambios de API**
   - Discussión sobre impacto
   - Backwards compatibility
   - Migración para usuarios

3. **Cambios de Almacenamiento**
   - Alternativas a JSON
   - Impacto en portabilidad
   - Compatibilidad hacia atrás

### 🔴 Probablemente No

1. **GUI o aplicación web** (fuera de scope)
2. **Dependencias externas** (contradice filosofía)
3. **Autenticación/sincronización** (complejidad innecesaria)
4. **Múltiples idiomas** (complicidad extra, mantener en English+Español)

## Código de Conducta

Por favor sé respetuoso con otros contribuidores. Esperamos:

- Comunicación honrada y constructiva
- Reconocimiento del trabajo de otros
- Apertura a diferentes perspectivas
- Paciencia con nuevos contribuidores

## Licencia

Al contribuir, aceptas que tu código se distribuye bajo [GPL-3.0](../LICENSE).

## Preguntas

- Revisa el [README.md](/../../README.md) para overview
- Revisa [ARCHITECTURE.md](ARCHITECTURE.md) para entender el diseño
- Abre una issue si tienes dudas

## Agradecimientos

¡Gracias por contribuir! Los contribuidores hacen que los proyectos de código abierto sean increíbles.
