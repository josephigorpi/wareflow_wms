# 📦 WareFlow WMS - Guía de Trabajo en Equipo

> Sistema de Gestión de Almacenes (Warehouse Management System) desarrollado con Streamlit, SQLite y Python.

## 📋 Tabla de Contenidos

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Núcleo Compartido](#núcleo-compartido)
4. [Archivos Modificables por Módulo](#archivos-modificables-por-módulo)
5. [Repartición Oficial de Módulos](#repartición-oficial-de-módulos)
6. [Flujo de Trabajo con Git](#flujo-de-trabajo-con-git)
7. [Ramas del Proyecto](#ramas-del-proyecto)
8. [Reglas de Desarrollo](#reglas-de-desarrollo)
9. [Proceso de Integración](#proceso-de-integración)
10. [Configuración Inicial](#configuración-inicial)

---

## 🎯 Descripción del Proyecto

**WareFlow WMS** es un Sistema de Gestión de Almacenes (WMS) modular y escalable diseñado para optimizar la gestión de inventario, recepción de mercancía, ubicación de productos y operaciones de picking/despacho.

### Objetivos Principales

- ✅ Centralizar la gestión de almacenes en una única plataforma
- ✅ Permitir trabajo colaborativo entre múltiples equipos
- ✅ Mantener data consistente en base de datos SQLite
- ✅ Proporcionar interfaz intuitiva con Streamlit
- ✅ Facilitar extensión sin comprometer el núcleo

### Tecnologías

- **Frontend**: Streamlit
- **Backend**: Python 3.x
- **Base de Datos**: SQLite
- **Autenticación**: PBKDF2-SHA256

---

## 🗂️ Estructura del Proyecto

```
wareflow_wms/
├── app.py                          # Punto de entrada principal
├── requirements.txt                # Dependencias del proyecto
├── generate_password_hash.py       # Utilidad: generar hashes
│
├── .streamlit/                     # Configuración de Streamlit
│
├── config/                         # NÚCLEO: Configuración global
│   ├── __init__.py
│   └── settings.py                 # Variables globales del sistema
│
├── core/                           # NÚCLEO: Funcionalidades críticas
│   ├── __init__.py
│   ├── auth.py                     # Autenticación y login
│   ├── permissions.py              # Control de permisos
│   └── session.py                  # Gestión de sesiones
│
├── database/                       # NÚCLEO: Acceso a datos
│   ├── __init__.py
│   ├── connection.py               # Conexión SQLite
│   ├── db_manager.py               # CRUD operations
│   ├── schema.sql                  # Estructura de tablas
│   ├── seed_data.sql               # Datos iniciales
│   └── migrations/                 # Futuras migraciones
│
├── components/                     # COMPARTIDO: Componentes UI reutilizables
│   ├── __init__.py
│   ├── alerts.py                   # Notificaciones
│   ├── forms.py                    # Formularios comunes
│   ├── kpi_card.py                 # Tarjetas KPI
│   ├── modals.py                   # Diálogos modales
│   ├── navbar.py                   # Barra de navegación
│   ├── sidebar.py                  # Sidebar con menú
│   ├── styles.py                   # Estilos globales
│   └── tables.py                   # Tablas de datos
│
├── services/                       # Lógica de negocio compartida
│   ├── __init__.py
│   ├── user_service.py             # Operaciones de usuarios
│   ├── product_service.py          # Operaciones de productos
│   ├── location_service.py         # Operaciones de ubicaciones
│   └── movement_service.py         # Operaciones de movimientos
│
├── utils/                          # Funciones auxiliares reutilizables
│   ├── __init__.py
│   ├── passwords.py                # Hash y verificación de contraseñas
│   ├── formatters.py               # Formateo de datos
│   ├── validators.py               # Validaciones
│   └── helpers.py                  # Funciones auxiliares
│
├── pages/                          # MODIFICABLE: Páginas del sistema
│   ├── __init__.py
│   ├── 0_login.py                  # Login (COMPARTIDO - No modificar)
│   ├── 1_dashboard.py              # Dashboard (Vil)
│   ├── 2_recepcion.py              # Recepción (Bus)
│   ├── 3_inventario.py             # Inventario (Mor)
│   ├── 4_ubicacion.py              # Ubicaciones (Par)
│   ├── 5_picking.py                # Picking (San)
│   └── 6_reportes.py               # Reportes (Vil)
│
└── assets/                         # Archivos estáticos (imágenes, etc)
```

---

## 🛡️ Núcleo Compartido

El **Núcleo Compartido** está compuesto por archivos críticos que afectan a todo el sistema. **No pueden ser modificados sin coordinación explícita del Tech Lead.**

### Archivos Protegidos

#### 1. `app.py` - Punto de entrada
- **Función**: Inicia la aplicación, inicializa la BD, carga estilos
- **Impacto**: Cualquier cambio afecta el startup de toda la app
- **Permiso**: Solo Tech Lead

#### 2. `core/auth.py` - Autenticación
- **Función**: Gestiona login, logout, y estado de sesión
- **Impacto**: Afecta la seguridad y acceso de todos los usuarios
- **Permiso**: Solo Tech Lead

#### 3. `core/permissions.py` - Control de permisos
- **Función**: Define qué puede hacer cada rol
- **Impacto**: Determina el acceso a funcionalidades por equipo
- **Permiso**: Cambios coordinados con Team Lead

#### 4. `core/session.py` - Gestión de sesiones
- **Función**: Inicializa y resetea el estado de sesión
- **Impacto**: Afecta la persistencia de datos entre páginas
- **Permiso**: Solo Tech Lead

#### 5. `config/settings.py` - Configuración global
- **Función**: Define variables globales (DB_PATH, timeouts, etc)
- **Impacto**: Afecta comportamiento del sistema completo
- **Permiso**: Solo Tech Lead

#### 6. `database/connection.py` - Conexión SQLite
- **Función**: Crea y gestiona conexiones a la BD
- **Impacto**: Crítico para acceso a datos
- **Permiso**: Solo Tech Lead

#### 7. `database/db_manager.py` - Gestor CRUD
- **Función**: Operaciones CRUD genéricas (insert, update, delete, fetch)
- **Impacto**: Base de todo acceso a datos
- **Permiso**: Extensión solo coordinada

#### 8. `database/schema.sql` - Esquema de BD
- **Función**: Define estructura de todas las tablas
- **Impacto**: Cambios rompen compatibilidad
- **Permiso**: Solo Tech Lead (migraciones coordinadas)

#### 9. `components/sidebar.py` - Menú lateral
- **Función**: Navegación principal del sistema
- **Impacto**: Afecta navegación global
- **Permiso**: Cambios coordinados

#### 10. `utils/passwords.py` - Hashing de contraseñas
- **Función**: Hash y verificación segura de contraseñas
- **Impacto**: Seguridad del sistema
- **Permiso**: Solo Tech Lead

### Cómo Solicitar Cambios al Núcleo

Si necesitas modificar algo del núcleo:

1. **Crear un Issue** explicando la razón
2. **Esperar aprobación** del Tech Lead
3. **Hacer un PR** con descripción detallada
4. **Pasar revisión** antes de merge

---

## 📝 Archivos Modificables por Módulo

Cada equipo puede crear y modificar **libremente** los siguientes tipos de archivos en su módulo:

### Estructura recomendada por módulo

```
pages/
├── {numero}_{modulo_principal}.py     # Página principal del módulo

components/
├── {modulo}_*.py                       # Componentes específicos del módulo

services/
├── {modulo}_service.py                # Lógica de negocio del módulo

repositories/  (crear si es necesario)
├── {modulo}_repository.py             # Acceso a datos específico
```

### Ejemplo: Módulo de Inventario (Mor)

```
# Crear estos archivos libremente:
pages/3_inventario.py                   # Página principal
components/inventario_form.py           # Formulario de inventario
components/inventario_table.py          # Tabla de productos
services/inventario_service.py          # Lógica de inventario
repositories/inventario_repository.py   # Acceso a datos (opcional)
```

### Buenas Prácticas

✅ **HACER**:
- Reutilizar componentes de `components/` 
- Usar servicios compartidos de `services/`
- Importar utilidades de `utils/`
- Crear componentes nuevos en `components/` si van a ser reutilizados
- Documentar funciones nuevas

❌ **NO HACER**:
- Modificar archivos del núcleo sin coordinación
- Duplicar lógica que ya existe en `services/`
- Crear componentes si ya existen similares
- Importar directamente de `database/` (usar `services/` o `db_manager.py`)
- Cambiar `core/auth.py`, `core/permissions.py`, etc.

---

## 👥 Repartición Oficial de Módulos

Cada integrante del equipo tiene **responsabilidad funcional** sobre módulos específicos:

### 1. **Bus** - Operaciones de Entrada
**Responsable**: [Nombre del desarrollador]

Módulos asignados:
- ✅ **Recepción** (`pages/2_recepcion.py`)
  - Registrar entrada de mercancía
  - Validar documentos de entrada
  - Asignar a zonas
  
- ✅ **Inspección** (crear `pages/7_inspeccion.py` si necesario)
  - Verificar calidad de productos
  - Registrar anomalías
  - Autorizar o rechazar entrada

**Servicios disponibles**:
- `services/product_service.py`
- `services/location_service.py`
- `services/movement_service.py`

**Componentes a usar**:
- `components/forms.py`
- `components/alerts.py`
- `components/tables.py`

---

### 2. **Mor** - Inventario
**Responsable**: [Nombre del desarrollador]

Módulos asignados:
- ✅ **Inventario** (`pages/3_inventario.py`)
  - Consultar stock en tiempo real
  - Ajustes de inventario
  - Control de lotes y vencimientos
  - Alertas de stock mínimo/máximo

**Servicios disponibles**:
- `services/product_service.py`
- `services/location_service.py`

**Componentes a usar**:
- `components/tables.py`
- `components/kpi_card.py`
- `components/alerts.py`

---

### 3. **Par** - Codificación y Ubicaciones
**Responsable**: [Nombre del desarrollador]

Módulos asignados:
- ✅ **Ubicaciones** (`pages/4_ubicacion.py`)
  - Crear y gestionar zonas
  - Crear y gestionar ubicaciones (pasillo-estante-nivel-posición)
  - Asignar productos a ubicaciones
  - Control de capacidad

**Servicios disponibles**:
- `services/location_service.py`
- `services/product_service.py`

**Componentes a usar**:
- `components/forms.py`
- `components/tables.py`
- `components/modals.py`

---

### 4. **San** - Operaciones de Salida
**Responsable**: [Nombre del desarrollador]

Módulos asignados:
- ✅ **Picking** (`pages/5_picking.py`)
  - Crear órdenes de picking
  - Guiar procesos de recolección
  - Validar códigos y cantidades
  - Generar etiquetas
  
- ✅ **Despacho** (crear `pages/8_despacho.py` si necesario)
  - Consolidar pedidos
  - Generar documentos de envío
  - Registrar salida de almacén
  - Tracking

**Servicios disponibles**:
- `services/movement_service.py`
- `services/product_service.py`
- `services/location_service.py`

**Componentes a usar**:
- `components/forms.py`
- `components/tables.py`
- `components/alerts.py`

---

### 5. **Vil** - Análisis y Reportes
**Responsable**: [Nombre del desarrollador]

Módulos asignados:
- ✅ **Dashboard** (`pages/1_dashboard.py`)
  - KPIs de almacén
  - Movimientos del día
  - Alertas críticas
  - Gráficos de actividad
  
- ✅ **Reportes** (`pages/6_reportes.py`)
  - Reportes de inventario
  - Reportes de movimientos
  - Análisis ABC
  - Trazabilidad

**Servicios disponibles**:
- Todos los servicios (lectura principalmente)
- `services/product_service.py`
- `services/movement_service.py`
- `services/location_service.py`

**Componentes a usar**:
- `components/kpi_card.py`
- `components/tables.py`
- `components/charts.py` (crear si no existe)

---

## 🌳 Flujo de Trabajo con Git

Todos los desarrolladores deben seguir este flujo para mantener código limpio y coordinado.

### Flujo General

```
main (Producción)
  ↑
develop (Integración)
  ↑
feature/{equipo}-{módulo} (Desarrollo)
```

### Pasos por Sesión de Trabajo

#### 1. Al empezar tu jornada:

```bash
# Actualizar la rama develop
git checkout develop
git pull origin develop

# Crear o actualizar tu rama de feature
git checkout feature/bus-recepcion
git merge develop  # Si hay cambios nuevos
```

#### 2. Durante el desarrollo:

```bash
# Hacer cambios en tus archivos
git add .
git commit -m "feat: descripción clara del cambio"
git commit -m "fix: corregir bug en validación"
git commit -m "refactor: mejorar estructura de código"
```

**Reglas de commits**:
- Usar prefijos: `feat:`, `fix:`, `refactor:`, `docs:`, `style:`, `test:`
- Mensajes en tiempo presente: "agregar validación" no "agregada validación"
- Commits frecuentes (no esperar a terminar todo)

#### 3. Al terminar un feature:

```bash
# Subir cambios al servidor
git push origin feature/bus-recepcion

# Crear Pull Request en GitHub
# Ir a https://github.com/josephigorpi/wareflow_wms/pulls
# Seleccionar tu rama como "compare" y "develop" como "base"
```

#### 4. Después de aprobación:

```bash
# Hacer merge desde GitHub (vía PR)
# O localmente:
git checkout develop
git pull origin develop
git merge feature/bus-recepcion
git push origin develop
```

### Comandos Útiles

```bash
# Ver ramas locales
git branch

# Ver ramas remotas
git branch -r

# Ver historial
git log --oneline -10

# Descartar cambios
git checkout -- archivo.py

# Revertir commit
git revert <commit-hash>
```

---

## 🔀 Ramas del Proyecto

### Rama `main`
- **Propósito**: Código de producción estable
- **Protección**: Solo merges desde `develop` via PR
- **Deploy**: Automático a producción
- **Quién**: Tech Lead

### Rama `develop`
- **Propósito**: Integración de features completados
- **Protección**: Solo merges desde `feature/*` via PR
- **Testing**: Ambiente de staging
- **Quién**: Team Leads validan PRs

### Ramas `feature/*`

#### `feature/bus-recepcion`
- **Equipo**: Bus
- **Alcance**: Módulos de Recepción e Inspección
- **Páginas**: `pages/2_recepcion.py`, `pages/7_inspeccion.py`
- **Responsable**: [Nombre]

#### `feature/mor-inventario`
- **Equipo**: Mor
- **Alcance**: Módulo de Inventario
- **Páginas**: `pages/3_inventario.py`
- **Responsable**: [Nombre]

#### `feature/par-ubicaciones`
- **Equipo**: Par
- **Alcance**: Módulo de Ubicaciones y Codificación
- **Páginas**: `pages/4_ubicacion.py`
- **Responsable**: [Nombre]

#### `feature/san-picking-despacho`
- **Equipo**: San
- **Alcance**: Módulos de Picking y Despacho
- **Páginas**: `pages/5_picking.py`, `pages/8_despacho.py`
- **Responsable**: [Nombre]

#### `feature/vil-dashboard-reportes`
- **Equipo**: Vil
- **Alcance**: Dashboard y Reportes
- **Páginas**: `pages/1_dashboard.py`, `pages/6_reportes.py`
- **Responsable**: [Nombre]

---

## ✅ Reglas de Desarrollo

### 1. Prohibiciones Explícitas

❌ **NUNCA modifiques estos archivos**:
```
app.py
core/auth.py
core/permissions.py
core/session.py
config/settings.py
database/connection.py
database/db_manager.py
database/schema.sql
components/sidebar.py
utils/passwords.py
```

❌ **NUNCA**:
- Hagas commits directos a `main` o `develop`
- Modifiques tablas de la BD sin coordinación
- Duplicues funcionalidad existente
- Importes directamente de `database/connection.py`
- Cambies estructura de carpetas

### 2. Buenas Prácticas Obligatorias

✅ **Usa servicios compartidos**:
```python
# ✅ BIEN
from services.product_service import get_product_by_sku
product = get_product_by_sku("SKU123")

# ❌ MAL
from database.db_manager import fetch_one
product = fetch_one("SELECT * FROM productos WHERE sku = ?", ("SKU123",))
```

✅ **Reutiliza componentes**:
```python
# ✅ BIEN
from components.alerts import alert_success, alert_error
from components.tables import render_table

# ❌ MAL
st.success("Producto creado")  # Inconsistente con estilos
```

✅ **Valida datos antes de guardar**:
```python
# ✅ BIEN
from utils.validators import validate_sku
if not validate_sku(sku):
    alert_error("SKU inválido")
    return

# ❌ MAL
db.insert("productos", {"sku": sku})  # Sin validar
```

✅ **Documenta tu código**:
```python
# ✅ BIEN
def procesar_recepcion(referencia: str, cantidad: int) -> bool:
    """Procesa una recepción de mercancía.
    
    Args:
        referencia: Número de recepción
        cantidad: Cantidad de unidades
        
    Returns:
        True si fue exitoso, False en caso contrario
    """
    pass

# ❌ MAL
def proc_rec(ref, cant):
    pass
```

✅ **Mantén consistencia de nombres**:
```python
# ✅ BIEN
get_product_by_id()
create_product()
update_product_stock()

# ❌ MAL
getProduct()      # camelCase
crear_prod()      # abreviaciones
actualizar_stock() # inconsistente
```

### 3. Estructura de Código

Cada página debe tener esta estructura:

```python
"""Módulo de [Descripción del módulo]."""

import streamlit as st
from core.auth import require_auth
from components.alerts import alert_success, alert_error
from components.forms import render_form
from services.product_service import get_products

# Autenticar
require_auth()

st.title("[Título del módulo]")

# Componentes aquí
if st.button("Acción"):
    # Lógica aquí
    pass
```

---

## 🔄 Proceso de Integración

El proceso desde desarrollo hasta producción:

### Fase 1: Desarrollo (1-3 días)
```
feature/bus-recepcion
├── Desarrollador escribe código
├── Commits frecuentes
└── Pruebas locales
```

### Fase 2: Pull Request (Revisión)
```
feature/bus-recepcion → develop (PR)
├── Tech Lead revisa código
├── Solicita cambios si es necesario
└── Aprueba cambios
```

### Fase 3: Integración (Merge)
```
develop
├── Merge automático a develop
├── CI/CD valida (si aplica)
└── Deploy a staging
```

### Fase 4: Testing (24-48 horas)
```
Staging (develop)
├── Testing funcional
├── Testing de integración
└── Aprobación de Product Owner
```

### Fase 5: Producción (Release)
```
develop → main
├── Tag de release
├── Deploy a producción
└── Monitoreo
```

### Checklist antes de PR

- [ ] Código sigue las reglas de desarrollo
- [ ] Sin cambios al núcleo compartido
- [ ] Componentes reutilizables se agregaron a `components/`
- [ ] Todos los servicios necesarios existen
- [ ] Funciones documentadas
- [ ] Pruebas locales exitosas
- [ ] Sin conflictos con `develop`
- [ ] Commits con mensajes claros

---

## 🚀 Configuración Inicial

### Para desarrolladores nuevos

#### 1. Clonar repositorio
```bash
git clone https://github.com/josephigorpi/wareflow_wms.git
cd wareflow_wms
```

#### 2. Crear rama personal
```bash
git checkout develop
git pull origin develop
git checkout -b feature/bus-recepcion
```

#### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 4. Ejecutar aplicación
```bash
streamlit run app.py
```

#### 5. Acceder a login
```
URL: http://localhost:8501
Usuario: admin
Contraseña: admin123
```

### Generar contraseñas
```bash
python generate_password_hash.py
```

---

## 📞 Comunicación y Coordinación

### Daily Standup
- **Cuándo**: Cada mañana
- **Duración**: 15 minutos
- **Qué reportar**:
  - ¿Qué hice ayer?
  - ¿Qué hago hoy?
  - ¿Bloqueos o problemas?

### Reunión de Integración (2 veces por semana)
- **Cuándo**: Martes y Viernes
- **Propósito**: Revisar PRs, resolver conflictos
- **Quién lidera**: Tech Lead

### Issues y Bugs
- **Crear un Issue** en GitHub antes de empezar
- **Asignar** al equipo responsable
- **Linkar** con tu PR cuando esté lista

---

## 📊 Métricas y Seguimiento

### Por Módulo
| Equipo | Módulo | Estado | PR Abiertos |
|--------|--------|--------|-------------|
| Bus | Recepción | En desarrollo | 0 |
| Mor | Inventario | No iniciado | 0 |
| Par | Ubicaciones | No iniciado | 0 |
| San | Picking | No iniciado | 0 |
| Vil | Dashboard | No iniciado | 0 |

---

## 🎓 Recursos Útiles

- **Streamlit Docs**: https://docs.streamlit.io
- **SQLite Tutorial**: https://www.sqlite.org/tutorial.html
- **Git Guide**: https://git-scm.com/doc
- **Python Style Guide**: https://pep8.org/

---

## 📝 Historial de Cambios

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2026-06-01 | Documento inicial |

---

## ❓ FAQ

**P: ¿Puedo modificar `database/schema.sql`?**
A: No, sin coordinación explícita. Si necesitas nuevas tablas, contacta al Tech Lead.

**P: ¿Cuándo hago push a main?**
A: Nunca directamente. Siempre a través de PRs a `develop`, y `develop` a `main` solo se hace en releases.

**P: ¿Qué pasa si tengo conflictos en Git?**
A: Contacta al Tech Lead. Resolveremos juntos durante reunión de integración.

**P: ¿Puedo crear un nuevo componente?**
A: Sí, pero ponlo en `components/` si es reutilizable, no en `pages/`.

**P: ¿Cómo agrego un nuevo usuario?**
A: Usa `generate_password_hash.py` para generar el hash, luego inserta en BD.

---

**Creado por**: Software Architecture Team  
**Última actualización**: 2026-06-01  
**Versión**: 1.0
