# routes.py
from flask import render_template, url_for, flash, redirect, request, abort, make_response
from app import app, db, bcrypt
from forms import (LoginForm, VehiculoForm, BitacoraForm, 
                   ReportForm, AreaForm) 
from models import User, Vehiculo, Bitacora, Area
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps
from datetime import datetime, time
from fpdf import FPDF
import io
import os

# -----------------------------------------------------------------
# CLASE PDF ESTILIZADA
# -----------------------------------------------------------------
class PDF(FPDF):
    def safe_str(self, text):
        return str(text or '').encode('latin-1', 'replace').decode('latin-1')

    def header(self):
        # 1. Fondo del Encabezado (Azul Oscuro)
        self.set_fill_color(28, 40, 51)
        # Altura 25mm para que quepa el logo
        self.rect(0, 0, 297, 25, 'F') 
        
        # 2. LOGO DE LA INSTITUCIÓN
        logo_path = os.path.join(app.root_path, 'static', 'img', 'logo.png')
        if os.path.exists(logo_path):
            try:
                # Logo a la izquierda
                self.image(logo_path, x=10, y=2.5, h=20)
            except:
                pass
        
        # 3. Título (CENTRADO PERFECTO)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(255, 255, 255)
        
        # Movemos el cursor verticalmente para centrar el texto en la barra azul
        self.set_y(8) 
        
        # width=0 significa "todo el ancho de la página"
        # align='C' significa Centrado
        self.cell(0, 10, self.safe_str('REPORTE DE BITACORAS VEHICULARES - YLB'), 0, 1, 'C')
        
        # Salto de línea para salir del header azul
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Pagina {self.page_no()}/{{nb}}', 0, 0, 'C')

# --- Decorador de Admin ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# --- RUTAS PÚBLICAS (KIOSKO) ---
@app.route("/")
def registrar_bitacora():
    form = BitacoraForm()
    return render_template('kiosko_formulario_unico.html', title='Registrar Bitácora', form=form, legend='Registro de Bitácora')

@app.route("/procesar_bitacora", methods=['POST'])
def procesar_bitacora():
    form = BitacoraForm()
    if form.validate_on_submit():
        fecha_salida_dt = datetime.combine(form.fecha_viaje.data, time.min) 
        fecha_entrada_dt = datetime.combine(form.fecha_viaje.data, time.max) 
        bitacora = Bitacora(
            nombre_conductor=form.nombre_conductor.data,
            vehiculo_id=form.vehiculo.data.id,
            area_id=form.area.data.id,
            fecha_salida=fecha_salida_dt,
            kilometraje_salida=form.kilometraje_salida.data,
            fecha_entrada=fecha_entrada_dt,
            kilometraje_entrada=form.kilometraje_entrada.data,
            descripcion_trabajo=form.descripcion_trabajo.data,
            litros_combustible=form.litros_combustible.data
        )
        db.session.add(bitacora)
        db.session.commit()
        flash(f'¡Bitácora para {bitacora.nombre_conductor} registrada exitosamente! Gracias.', 'success')
        return redirect(url_for('registrar_bitacora'))
    return render_template('kiosko_formulario_unico.html', title='Registrar Bitácora', form=form, legend='Registro de Bitácora')

# --- RUTAS DE ADMIN ---
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login fallido. Revisa tu email y contraseña.', 'danger')
    return render_template('login.html', title='Iniciar Sesión', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
@admin_required
def dashboard():
    stats = {
        'total_bitacoras': Bitacora.query.count(),
        'bitacoras_hoy': Bitacora.query.filter(Bitacora.fecha_salida >= datetime.combine(datetime.utcnow().date(), time.min)).count(),
        'total_vehiculos': Vehiculo.query.count(),
        'total_areas': Area.query.count()
    }
    return render_template('dashboard_admin.html', title='Panel de Admin', stats=stats)

# --- CRUD VEHÍCULOS ---
@app.route("/vehiculos")
@login_required
@admin_required
def listar_vehiculos():
    vehiculos = Vehiculo.query.all()
    return render_template('vehiculos.html', vehiculos=vehiculos, title='Gestión de Vehículos')
@app.route("/vehiculo/nuevo", methods=['GET', 'POST'])
@login_required
@admin_required
def crear_vehiculo():
    form = VehiculoForm()
    if form.validate_on_submit():
        if Vehiculo.query.filter_by(codigo=form.codigo.data).first():
            flash('Ese Código ya existe.', 'danger')
        elif Vehiculo.query.filter_by(codigo_interno=form.codigo_interno.data).first():
            flash('Ese Código Interno ya existe.', 'danger')
        elif Vehiculo.query.filter_by(placa=form.placa.data).first():
            flash('Esa Placa ya existe.', 'danger')
        elif Vehiculo.query.filter_by(nr_chasis=form.nr_chasis.data).first():
            flash('Ese Nro. de Chasis ya existe.', 'danger')
        else:
            vehiculo = Vehiculo(codigo=form.codigo.data, codigo_interno=form.codigo_interno.data, nr_chasis=form.nr_chasis.data,
                                placa=form.placa.data, marca=form.marca.data, modelo=form.modelo.data, 
                                disponible=True)
            db.session.add(vehiculo)
            db.session.commit()
            flash(f'¡Vehículo {vehiculo.placa} creado exitosamente!', 'success')
            return redirect(url_for('listar_vehiculos'))
    return render_template('vehiculo_form.html', title='Nuevo Vehículo', form=form, legend='Registrar Nuevo Vehículo')
@app.route("/vehiculo/<int:vehiculo_id>/editar", methods=['GET', 'POST'])
@login_required
@admin_required
def editar_vehiculo(vehiculo_id):
    vehiculo = Vehiculo.query.get_or_404(vehiculo_id)
    form = VehiculoForm()
    if form.validate_on_submit():
        if vehiculo.codigo != form.codigo.data and Vehiculo.query.filter_by(codigo=form.codigo.data).first():
            flash('Ese Código ya existe.', 'danger')
        elif Vehiculo.codigo_interno != form.codigo_interno.data and Vehiculo.query.filter_by(codigo_interno=form.codigo_interno.data).first():
            flash('Ese Código Interno ya existe.', 'danger')
        elif Vehiculo.placa != form.placa.data and Vehiculo.query.filter_by(placa=form.placa.data).first():
            flash('Esa Placa ya existe.', 'danger')
        elif Vehiculo.nr_chasis != form.nr_chasis.data and Vehiculo.query.filter_by(nr_chasis=form.nr_chasis.data).first():
            flash('Ese Nro. de Chasis ya existe.', 'danger')
        else:
            vehiculo.codigo = form.codigo.data
            vehiculo.codigo_interno = form.codigo_interno.data
            vehiculo.nr_chasis = form.nr_chasis.data
            vehiculo.placa = form.placa.data
            vehiculo.marca = form.marca.data
            vehiculo.modelo = form.modelo.data
            db.session.commit()
            flash(f'¡Vehiculo {vehiculo.placa} actualizado!', 'success')
            return redirect(url_for('listar_vehiculos'))
    elif request.method == 'GET':
        form.codigo.data = vehiculo.codigo
        form.codigo_interno.data = vehiculo.codigo_interno
        form.nr_chasis.data = vehiculo.nr_chasis
        form.placa.data = vehiculo.placa
        form.marca.data = vehiculo.marca
        form.modelo.data = vehiculo.modelo
    return render_template('vehiculo_form.html', title='Editar Vehículo', form=form, legend=f'Editar Vehículo: {vehiculo.placa}')
@app.route("/vehiculo/<int:vehiculo_id>/eliminar", methods=['POST'])
@login_required
@admin_required
def eliminar_vehiculo(vehiculo_id):
    vehiculo = Vehiculo.query.get_or_404(vehiculo_id)
    if vehiculo.bitacoras:
        flash(f'No se puede eliminar el vehículo {vehiculo.placa} porque tiene bitácoras asociadas.', 'danger')
        return redirect(url_for('listar_vehiculos'))
    flash(f'Vehículo {vehiculo.placa} eliminado.', 'warning')
    db.session.delete(vehiculo)
    db.session.commit()
    return redirect(url_for('listar_vehiculos'))

# --- CRUD AREAS ---
@app.route("/areas")
@login_required
@admin_required
def listar_areas():
    areas = Area.query.all()
    return render_template('areas.html', areas=areas, title='Gestión de Áreas')
@app.route("/area/nueva", methods=['GET', 'POST'])
@login_required
@admin_required
def crear_area():
    form = AreaForm()
    if form.validate_on_submit():
        area = Area(nombre=form.nombre.data)
        db.session.add(area)
        db.session.commit()
        flash(f'Área "{area.nombre}" creada exitosamente.', 'success')
        return redirect(url_for('listar_areas'))
    return render_template('area_form.html', title='Nueva Área', form=form, legend='Crear Nueva Área')
@app.route("/area/<int:area_id>/editar", methods=['GET', 'POST'])
@login_required
@admin_required
def editar_area(area_id):
    area = Area.query.get_or_404(area_id)
    form = AreaForm(obj=area) 
    if form.validate_on_submit():
        if area.nombre != form.nombre.data and Area.query.filter_by(nombre=form.nombre.data).first():
            flash('Ese nombre de área ya está en uso.', 'danger')
        else:
            area.nombre = form.nombre.data
            db.session.commit()
            flash('Área actualizada exitosamente.', 'success')
            return redirect(url_for('listar_areas'))
    return render_template('area_form.html', title='Editar Área', form=form, legend='Editar Área')
@app.route("/area/<int:area_id>/eliminar", methods=['POST'])
@login_required
@admin_required
def eliminar_area(area_id):
    area = Area.query.get_or_404(area_id)
    if area.bitacoras:
        flash(f'No se puede eliminar el área "{area.nombre}" porque está siendo usada por bitácoras.', 'danger')
        return redirect(url_for('listar_areas'))
    db.session.delete(area)
    db.session.commit()
    flash(f'Área "{area.nombre}" eliminada.', 'warning')
    return redirect(url_for('listar_areas'))

# --- REPORTES ---
@app.route("/reportes", methods=['GET', 'POST'])
@login_required
@admin_required
def reportes():
    form = ReportForm()
    form.vehiculo.choices = [('', 'Todos')] + [(v.id, v.placa) for v in Vehiculo.query.order_by(Vehiculo.placa)]
    form.area.choices = [('', 'Todos')] + [(a.id, a.nombre) for a in Area.query.order_by(Area.nombre)]
    query = Bitacora.query
    filters = {
        'fecha_inicio': request.form.get('fecha_inicio', ''),
        'fecha_fin': request.form.get('fecha_fin', ''),
        'vehiculo_id': request.form.get('vehiculo', ''),
        'area_id': request.form.get('area', '')
    }
    if form.validate_on_submit():
        if form.fecha_inicio.data:
            start_datetime = datetime.combine(form.fecha_inicio.data, time.min)
            query = query.filter(Bitacora.fecha_salida >= start_datetime)
        if form.fecha_fin.data:
            end_datetime = datetime.combine(form.fecha_fin.data, time.max)
            query = query.filter(Bitacora.fecha_salida <= end_datetime)
        if form.vehiculo.data:
            query = query.filter(Bitacora.vehiculo_id == form.vehiculo.data.id)
            filters['vehiculo_id'] = form.vehiculo.data.id
        if form.area.data:
            query = query.filter(Bitacora.area_id == form.area.data.id)
            filters['area_id'] = form.area.data.id
        flash(f'Reporte filtrado. Se encontraron {query.count()} registros.', 'success')
    bitacoras = query.order_by(Bitacora.fecha_salida.desc()).all()
    return render_template('reportes.html', title='Generar Reportes', form=form, bitacoras=bitacoras, filters=filters)

@app.route("/bitacora/<int:bitacora_id>/editar", methods=['GET', 'POST'])
@login_required
@admin_required
def editar_bitacora(bitacora_id):
    bitacora = Bitacora.query.get_or_404(bitacora_id)
    form = BitacoraForm()
    if form.validate_on_submit():
        bitacora.nombre_conductor = form.nombre_conductor.data
        bitacora.vehiculo_id = form.vehiculo.data.id
        bitacora.area_id = form.area.data.id
        bitacora.fecha_salida = datetime.combine(form.fecha_viaje.data, time.min)
        bitacora.fecha_entrada = datetime.combine(form.fecha_viaje.data, time.max)
        bitacora.kilometraje_salida = form.kilometraje_salida.data
        bitacora.kilometraje_entrada = form.kilometraje_entrada.data
        bitacora.descripcion_trabajo = form.descripcion_trabajo.data
        bitacora.litros_combustible = form.litros_combustible.data
        db.session.commit()
        flash('¡Bitácora actualizada exitosamente!', 'success')
        return redirect(url_for('reportes'))
    elif request.method == 'GET':
        form.nombre_conductor.data = bitacora.nombre_conductor
        form.vehiculo.data = bitacora.vehiculo_usado
        form.area.data = bitacora.area_asignada
        form.fecha_viaje.data = bitacora.fecha_salida.date()
        form.kilometraje_salida.data = bitacora.kilometraje_salida
        form.kilometraje_entrada.data = bitacora.kilometraje_entrada
        form.descripcion_trabajo.data = bitacora.descripcion_trabajo
        form.litros_combustible.data = bitacora.litros_combustible
    return render_template('editar_bitacora.html', title='Editar Bitácora', form=form, legend='Editar Bitácora')

@app.route("/bitacora/<int:bitacora_id>/eliminar", methods=['POST'])
@login_required
@admin_required
def eliminar_bitacora(bitacora_id):
    bitacora = Bitacora.query.get_or_404(bitacora_id)
    db.session.delete(bitacora)
    db.session.commit()
    flash('La bitácora ha sido eliminada.', 'warning')
    return redirect(url_for('reportes'))

# -----------------------------------------------------------------
# RUTA PDF CON HEADER CENTRADO (Y Safe Strings)
# -----------------------------------------------------------------
@app.route("/reporte/pdf")
@login_required
@admin_required
def reporte_pdf():
    fecha_inicio_str = request.args.get('fecha_inicio')
    fecha_fin_str = request.args.get('fecha_fin')
    vehiculo_id = request.args.get('vehiculo_id')
    area_id = request.args.get('area_id')

    query = Bitacora.query
    try:
        if fecha_inicio_str:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            query = query.filter(Bitacora.fecha_salida >= datetime.combine(fecha_inicio, time.min))
        if fecha_fin_str:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            query = query.filter(Bitacora.fecha_salida <= datetime.combine(fecha_fin, time.max))
        if vehiculo_id:
            query = query.filter(Bitacora.vehiculo_id == int(vehiculo_id))
        if area_id:
            query = query.filter(Bitacora.area_id == int(area_id))
    except ValueError:
        flash('Error en los parámetros del filtro.', 'danger')
        return redirect(url_for('reportes'))

    bitacoras = query.order_by(Bitacora.fecha_salida.asc()).all()
    fecha_hoy = datetime.utcnow().strftime('%Y-%m-%d')

    pdf = PDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font('Arial', '', 8)
    
    col_width = {
        "fecha": 18, "nombre": 40, "km_inicial": 15, "km_final": 15,
        "km_recorridos": 15, "litros": 15, "actividad": 105, 
        "sector": 34, "firma": 20
    }

    def safe_str(text):
        return str(text or '').encode('latin-1', 'replace').decode('latin-1')

    pdf.set_fill_color(220, 220, 220)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(col_width["fecha"], 8, safe_str('FECHA'), 1, 0, 'C', fill=True)
    pdf.cell(col_width["nombre"], 8, safe_str('RESPONSABLE DE USO'), 1, 0, 'C', fill=True)
    pdf.cell(col_width["km_inicial"], 8, safe_str('KM. INI'), 1, 0, 'C', fill=True)
    pdf.cell(col_width["km_final"], 8, safe_str('KM. FIN'), 1, 0, 'C', fill=True)
    pdf.cell(col_width["km_recorridos"], 8, safe_str('KM. REC'), 1, 0, 'C', fill=True)
    pdf.cell(col_width["litros"], 8, safe_str('LITROS'), 1, 0, 'C', fill=True)
    pdf.cell(col_width["actividad"], 8, safe_str('ACTIVIDAD / OBSERVACIONES'), 1, 0, 'C', fill=True)
    pdf.cell(col_width["sector"], 8, safe_str('SECTOR'), 1, 0, 'C', fill=True)
    pdf.cell(col_width["firma"], 8, safe_str('FIRMA'), 1, 1, 'C', fill=True)
    
    pdf.set_font('Arial', '', 8)
    fill = False 
    
    for bitacora in bitacoras:
        km_recorrido = bitacora.kilometraje_entrada - bitacora.kilometraje_salida
        nombre = safe_str(bitacora.nombre_conductor)
        placa = safe_str(bitacora.vehiculo_usado.placa)
        area = safe_str(bitacora.area_asignada.nombre)
        actividad = safe_str(bitacora.descripcion_trabajo)

        if fill: pdf.set_fill_color(245, 245, 245)
        else: pdf.set_fill_color(255, 255, 255)

        y_inicial = pdf.get_y()
        pdf.multi_cell(col_width["fecha"], 8, bitacora.fecha_salida.strftime('%Y-%m-%d'), 1, 'C', fill=True)
        y_despues_fecha = pdf.get_y()
        pdf.set_y(y_inicial); pdf.set_x(pdf.get_x() + col_width["fecha"])
        
        pdf.multi_cell(col_width["nombre"], 8, nombre, 1, 'L', fill=True)
        y_despues_nombre = pdf.get_y()
        pdf.set_y(y_inicial); pdf.set_x(pdf.get_x() + col_width["fecha"] + col_width["nombre"])
        
        pdf.multi_cell(col_width["km_inicial"], 8, str(bitacora.kilometraje_salida), 1, 'R', fill=True)
        y_despues_km_i = pdf.get_y()
        pdf.set_y(y_inicial); pdf.set_x(pdf.get_x() + col_width["fecha"] + col_width["nombre"] + col_width["km_inicial"])

        pdf.multi_cell(col_width["km_final"], 8, str(bitacora.kilometraje_entrada), 1, 'R', fill=True)
        y_despues_km_f = pdf.get_y()
        pdf.set_y(y_inicial); pdf.set_x(pdf.get_x() + col_width["fecha"] + col_width["nombre"] + col_width["km_inicial"] + col_width["km_final"])

        pdf.multi_cell(col_width["km_recorridos"], 8, str(round(km_recorrido, 2)), 1, 'R', fill=True)
        y_despues_km_r = pdf.get_y()
        pdf.set_y(y_inicial); pdf.set_x(pdf.get_x() + col_width["fecha"] + col_width["nombre"] + col_width["km_inicial"] + col_width["km_final"] + col_width["km_recorridos"])
        
        pdf.multi_cell(col_width["litros"], 8, str(bitacora.litros_combustible or 0), 1, 'R', fill=True)
        y_despues_litros = pdf.get_y()
        pdf.set_y(y_inicial); pdf.set_x(pdf.get_x() + col_width["fecha"] + col_width["nombre"] + col_width["km_inicial"] + col_width["km_final"] + col_width["km_recorridos"] + col_width["litros"])
        
        pdf.multi_cell(col_width["actividad"], 8, actividad, 1, 'L', fill=True)
        y_despues_actividad = pdf.get_y()
        pdf.set_y(y_inicial); pdf.set_x(pdf.get_x() + col_width["fecha"] + col_width["nombre"] + col_width["km_inicial"] + col_width["km_final"] + col_width["km_recorridos"] + col_width["litros"] + col_width["actividad"])
        
        pdf.multi_cell(col_width["sector"], 8, area, 1, 'L', fill=True)
        y_despues_sector = pdf.get_y()
        pdf.set_y(y_inicial); pdf.set_x(pdf.get_x() + col_width["fecha"] + col_width["nombre"] + col_width["km_inicial"] + col_width["km_final"] + col_width["km_recorridos"] + col_width["litros"] + col_width["actividad"] + col_width["sector"])
        
        pdf.multi_cell(col_width["firma"], 8, '', 1, 'C', fill=True)
        y_despues_firma = pdf.get_y()

        max_y = max(y_despues_fecha, y_despues_nombre, y_despues_km_i, y_despues_km_f, y_despues_km_r, y_despues_litros, y_despues_actividad, y_despues_sector, y_despues_firma)
        
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, max_y, 287, max_y)
        pdf.set_y(max_y)
        
        fill = not fill

    pdf_output = bytes(pdf.output()) 
    response = make_response(pdf_output)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_bitacoras_{fecha_hoy}.pdf'
    return response

# --- RUTA MÁGICA DE INSTALACIÓN ---
@app.route("/instalar_sistema_ahora")
def instalar_sistema_ahora():
    try:
        db.create_all()
        email = "admin@ylb.gob.bo"
        if not User.query.filter_by(email=email).first():
            password = "admin"
            hashed = bcrypt.generate_password_hash(password).decode('utf-8')
            u = User(username="Admin", email=email, password=hashed, role='admin')
            db.session.add(u)
            db.session.commit()
            return f"<h1 style='color:green'>¡ÉXITO TOTAL! Admin creado: {email} / {password}</h1><br><a href='/login'>Ir al Login</a>"
        else:
            return "<h1 style='color:blue'>El sistema ya estaba instalado.</h1><br><a href='/login'>Ir al Login</a>"
    except Exception as e:
        return f"<h1 style='color:red'>ERROR: {str(e)}</h1>"
