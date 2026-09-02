# Sistema de Bitácoras de Transporte - YLB

Sistema web institucional para la digitalización, control y supervisión operativa del parque vehicular, registro de bitácoras de viaje, control de conductores y asignación de rutas en Yacimientos de Litio Bolivianos (YLB).

---

### Flujo Operativo y de Despacho

```mermaid
flowchart TD
    subgraph Puntos de Control y Garitas
        K[Kiosko de Control Rápido] -->|Registro de Salida o Llegada| D[Despacho Vehicular]
        D --> V{Validación de Disponibilidad}
    end

    subgraph Núcleo de Aplicación Flask
        V -->|Vehículo Habilitado| REG[Creación de Bitácora de Viaje]
        REG --> DB[(Base de Datos PostgreSQL)]
        V -->|Vehículo en Ruta Activa| ERR[Alerta de Conflicto de Despacho]
    end

    subgraph Módulos del Sistema
        DB --> ADM[Dashboard Administrativo y Control de Flota]
        DB --> DRV[Portal del Conductor e Historial de Rutas]
        DB --> REP[Generación de Reportes PDF Oficiales]
    end
```

---

### Características Principales

| Módulo | Funcionalidad |
| :--- | :--- |
| **Formulario Kiosko Único** | Interfaz optimizada para pantallas táctiles y estaciones de garita para el registro rápido de salidas, kilometraje y retorno de unidades. |
| **Dashboard Administrativo** | Supervisión centralizada de vehículos en ruta, disponibilidad de conductores y estadísticas operativas de combustible y kilometraje. |
| **Portal del Conductor** | Vista personalizada para que cada chofer consulte sus viajes asignados, rutas activas y estados de entrega. |
| **Administración de Catálogos** | Gestión integral de vehículos (placas, modelos, capacidad), áreas institucionales y personal de conducción. |
| **Exportación de Reportes** | Generación de reportes PDF estructurados para auditorías institucionales y control interno. |
| **Seguridad de Acceso** | Control de autenticación con Flask-Login, protección CSRF y almacenamiento de contraseñas con hashing Bcrypt. |

---

### Stack Tecnológico

- **Backend:** Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, WTForms.
- **Base de Datos:** PostgreSQL con driver `psycopg2-binary`.
- **Seguridad:** Flask-Bcrypt, Werkzeug Security.
- **Generación de Reportes:** FPDF2 / ReportLab.
- **Frontend:** Plantillas Jinja2, HTML5, CSS3, JavaScript modular.
- **Servidor de Producción:** Gunicorn (`Procfile`).

---

### Instalación y Configuración Local

Requisitos: Python 3.10+ y servidor PostgreSQL.

```bash
# 1. Clonar el repositorio
git clone https://github.com/saolos12/sistema-bitacoras-ylb.git
cd sistema-bitacoras-ylb

# 2. Crear y activar entorno virtual
python -m venv venv
# Windows: .\venv\Scripts\activate | Linux: source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno (.env)
# DATABASE_URL=postgresql://usuario:password@localhost:5432/ylb_bitacoras
# SECRET_KEY=clave_secreta_de_produccion

# 5. Inicializar la base de datos y ejecutar el servidor
python app.py
```

El sistema estará accesible en `http://localhost:5000`.

---

### Licencia

Este proyecto está bajo la licencia MIT.