# models.py
from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

# --- User (Sin cambios) ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='admin')

# --- Vehiculo (Sin cambios) ---
class Vehiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    codigo_interno = db.Column(db.String(50), unique=True, nullable=False)
    nr_chasis = db.Column(db.String(100), unique=True, nullable=False)
    placa = db.Column(db.String(10), unique=True, nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    disponible = db.Column(db.Boolean, nullable=False, default=True)
    bitacoras = db.relationship('Bitacora', backref='vehiculo_usado', lazy=True)

    def __repr__(self):
        return f"Vehiculo('{self.placa}', '{self.marca}', '{self.modelo}')"

# --- Area (Sin cambios) ---
class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    bitacoras = db.relationship('Bitacora', backref='area_asignada', lazy=True)

    def __repr__(self):
        return f"Area('{self.nombre}')"

# -----------------------------------------------------------------
# ¡¡CLASE BITACORA ACTUALIZADA!!
# -----------------------------------------------------------------
class Bitacora(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_conductor = db.Column(db.String(100), nullable=False)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculo.id'), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    
    fecha_salida = db.Column(db.DateTime, nullable=False)
    kilometraje_salida = db.Column(db.Float, nullable=False)
    fecha_entrada = db.Column(db.DateTime, nullable=True) 
    kilometraje_entrada = db.Column(db.Float, nullable=True) 
    
    descripcion_trabajo = db.Column(db.Text, nullable=False) # (Actividad / Observaciones)
    litros_combustible = db.Column(db.Float, nullable=True, default=0)
    
    # ¡¡CAMPO 'observaciones' ELIMINADO!!
    
    def __repr__(self):
        return f"Bitacora('{self.nombre_conductor}', '{self.vehiculo_usado.placa}')"