# Sistema de Bitácoras de Transporte - YLB

Sistema web para la administración y registro digital de bitácoras de transporte, control de conductores, vehículos y rutas institucionales para Yacimientos de Litio Bolivianos (YLB).

## 📋 Descripción

Plataforma diseñada para digitalizar y automatizar el control vehicular y la asignación de viajes:
- **Formulario Kiosko Único:** Registro ágil de salidas y llegadas de vehículos en puntos de control.
- **Dashboard Administrativo:** Supervisión en tiempo real de flota, conductores activos y bitácoras registradas.
- **Portal del Conductor:** Vista personalizada para que cada conductor consulte sus asignaciones.
- **Mantenimiento y Catálogos:** Gestión de vehículos, áreas y conductores.
- **Generación de Reportes:** Exportación de reportes PDF estructurados.

## 🛠️ Tecnologías

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, WTForms
- **Base de Datos:** PostgreSQL
- **Seguridad:** Flask-Bcrypt
- **Reportes PDF:** fpdf2 / pdfkit
- **Frontend:** Jinja2, HTML5, CSS3, JavaScript

## ⚙️ Instalación Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/saolos12/sistema-bitacoras-ylb.git
   cd sistema-bitacoras-ylb
   ```

2. **Crear y activar entorno virtual:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación:**
   ```bash
   python app.py
   ```
