# config.py
import os

class Config:
    # Busca la clave en el sistema, si no hay, usa una por defecto
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave_super_secreta_por_defecto'
    
    # Busca la URL de la base de datos en el sistema
    # IMPORTANTE: Render a veces da la URL empezando con "postgres://", 
    # pero SQLAlchemy necesita "postgresql://". Este código lo arregla automáticamente.
    uri = os.environ.get('DATABASE_URL')
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = uri or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False