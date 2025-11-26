# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# 1. Inicialización de la App
app = Flask(__name__)
# 2. Carga de la configuración desde config.py
app.config.from_object('config.Config') 

# 3. Inicialización de las extensiones de Flask
#    Se definen aquí para que otros archivos (como models.py y routes.py)
#    puedan importarlos desde 'app'.
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

# 4. Configuración de Flask-Login
login_manager.login_view = 'login' # La ruta (función) a la que redirige si no estás logueado.
login_manager.login_message_category = 'info' # Categoría de Bootstrap para los mensajes flash.

# 5. IMPORTACIÓN CLAVE (¡La solución al error!)
#    Importamos las rutas (routes.py) al final y DESPUÉS de haber definido 'app' y 'db'.
#    Esto evita la importación circular, ya que 'routes.py' necesita importar 'app' y 'db'.
#    Y 'models.py' (que es usado por 'routes.py') también necesita 'db'.
from routes import *

# 6. Punto de entrada para correr la aplicación
if __name__ == '__main__':
    app.run(debug=True)