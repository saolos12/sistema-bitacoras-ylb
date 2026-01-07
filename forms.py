# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, SelectField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange, Optional
from models import User, Vehiculo, Area
from wtforms_sqlalchemy.fields import QuerySelectField

# --- Funciones helper ---
def todos_los_vehiculos():
    return Vehiculo.query.order_by(Vehiculo.placa)
def todas_las_areas():
    return Area.query.order_by(Area.nombre)

# --- LoginForm ---
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

# -----------------------------------------------------------------
# ¡¡ESTE ES EL QUE TE FALTA!! (UserForm)
# -----------------------------------------------------------------
class UserForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Guardar Admin')

    def validate_email(self, email):
        # Validamos si el email ya existe para no duplicar
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Ese email ya está registrado.')

# --- VehiculoForm ---
class VehiculoForm(FlaskForm):
    codigo = StringField('Código', validators=[DataRequired()])
    codigo_interno = StringField('Código Interno', validators=[DataRequired()])
    nr_chasis = StringField('Nro. de Chasis', validators=[DataRequired()])
    placa = StringField('Placa (Matrícula)', validators=[DataRequired()])
    marca = StringField('Marca', validators=[DataRequired()])
    modelo = StringField('Modelo', validators=[DataRequired()])
    submit = SubmitField('Guardar Vehículo')

# --- AreaForm ---
class AreaForm(FlaskForm):
    nombre = StringField('Nombre del Área', validators=[DataRequired()])
    submit = SubmitField('Guardar Área')
    def validate_nombre(self, nombre):
        area = Area.query.filter_by(nombre=nombre.data).first()
        if area:
            raise ValidationError('Esa área ya existe. Por favor, elige otro nombre.')

# --- BitacoraForm ---
class BitacoraForm(FlaskForm):
    nombre_conductor = StringField('Nombre Completo del Conductor', validators=[DataRequired()])
    vehiculo = QuerySelectField('Vehículo Asignado', 
                                query_factory=todos_los_vehiculos, 
                                get_label='placa', 
                                allow_blank=False, 
                                validators=[DataRequired()])
    area = QuerySelectField('Área (Sector o Zona de Trabajo)', 
                                query_factory=todas_las_areas, 
                                get_label='nombre', 
                                allow_blank=False, 
                                validators=[DataRequired()])
    
    fecha_viaje = DateField('Fecha', format='%Y-%m-%d', validators=[DataRequired()])

    kilometraje_salida = FloatField('Kilometraje Inicial', validators=[DataRequired()])
    kilometraje_entrada = FloatField('Kilometraje Final', validators=[DataRequired()])
    litros_combustible = FloatField('Litros Diesel/Gas Cargados', validators=[Optional()])
    
    descripcion_trabajo = TextAreaField('Actividad / Observaciones', validators=[DataRequired()])
    
    submit = SubmitField('Registrar Bitácora Completa')

    def validate_kilometraje_entrada(self, kilometraje_entrada):
        if kilometraje_entrada.data and self.kilometraje_salida.data:
            if kilometraje_entrada.data <= self.kilometraje_salida.data:
                raise ValidationError('El kilometraje final debe ser mayor al inicial.')

# --- ReportForm ---
class ReportForm(FlaskForm):
    fecha_inicio = DateField('Fecha de Inicio', format='%Y-%m-%d', validators=[Optional()])
    fecha_fin = DateField('Fecha de Fin', format='%Y-%m-%d', validators=[Optional()])
    vehiculo = QuerySelectField('Filtrar por Vehículo', 
                                query_factory=todos_los_vehiculos, 
                                get_label='placa', 
                                allow_blank=True, 
                                validators=[Optional()])
    area = QuerySelectField('Filtrar por Área', 
                            query_factory=todas_las_areas, 
                            get_label='nombre', 
                            allow_blank=True, 
                            validators=[Optional()])
    submit = SubmitField('Generar Reporte')
