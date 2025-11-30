from flask import Flask, render_template, redirect, url_for, request, flash, make_response
from config import Config
from models import db, User, Tenant, Apartment, Building, Street
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from io import BytesIO 
from datetime import datetime  
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('tenants'))
        else:
            flash('Невірний логін або пароль')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        role = request.form.get('role', 'user')
        
        # Перевіряємо, чи існує користувач
        if User.query.filter_by(username=username).first():
            flash('Користувач вже існує')
            return render_template('register.html')
        
        # Шукаємо мешканця за ПІБ
        tenant = Tenant.query.filter_by(full_name=full_name).first()
        if not tenant:
            flash('Мешканця з таким ПІБ не знайдено. Зверніться до адміністратора.')
            return render_template('register.html')
        
        # Перевіряємо, чи вже є користувач для цього мешканця
        existing_user = User.query.filter_by(tenant_id=tenant.id).first()
        if existing_user:
            flash('Для цього мешканця вже зареєстровано користувача')
            return render_template('register.html')
        
        # Створюємо користувача
        user = User(
            username=username, 
            password_hash=generate_password_hash(password), 
            role=role,
            tenant_id=tenant.id  # Зв'язуємо з мешканцем
        )
        db.session.add(user)
        db.session.commit()
        flash('Користувача зареєстровано! Тепер ви можете увійти.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/tenants')
@login_required
def tenants():
    if current_user.role == 'admin':
        # Адмін бачить всіх
        tenants = Tenant.query.join(
            Apartment, Tenant.apartment_id == Apartment.id
        ).join(
            Building, Apartment.building_id == Building.id
        ).join(
            Street, Building.street_id == Street.id
        ).add_columns(
            Tenant.id, 
            Tenant.full_name, 
            Tenant.passport_series,
            Tenant.passport_number, 
            Tenant.phone,
            Tenant.registration_date,
            Apartment.number.label('apartment_number'),
            Apartment.area, 
            Apartment.rooms,
            Apartment.ownership_type,
            Building.number.label('building_number'),
            Street.name.label('street_name')
        ).all()
    else:
        # Звичайний користувач бачить тільки себе
        if not current_user.tenant_id:
            flash('Ваш акаунт не повʼязаний з мешканцем. Зверніться до адміністратора.')
            return render_template('tenants.html', tenants=[])
        
        tenants = Tenant.query.join(
            Apartment, Tenant.apartment_id == Apartment.id
        ).join(
            Building, Apartment.building_id == Building.id
        ).join(
            Street, Building.street_id == Street.id
        ).filter(
            Tenant.id == current_user.tenant_id  # Тільки свій запис
        ).add_columns(
            Tenant.id, 
            Tenant.full_name, 
            Tenant.passport_series,
            Tenant.passport_number, 
            Tenant.phone,
            Tenant.registration_date,
            Apartment.number.label('apartment_number'),
            Apartment.area, 
            Apartment.rooms,
            Apartment.ownership_type,
            Building.number.label('building_number'),
            Street.name.label('street_name')
        ).all()
    
    return render_template('tenants.html', tenants=tenants)

@app.route('/tenant/add', methods=['GET', 'POST'])
@login_required
def add_tenant():
    if current_user.role != 'admin':
        flash('Доступ заборонено. Потрібні права адміністратора')
        return redirect(url_for('tenants'))
    
    if request.method == 'POST':
        try:
            full_name = request.form['full_name']
            passport_series = request.form.get('passport_series')
            passport_number = request.form['passport_number']
            phone = request.form.get('phone')
            registration_date = request.form['registration_date']
            apartment_id = request.form['apartment_id']
            
            tenant = Tenant(
                full_name=full_name,
                passport_series=passport_series,
                passport_number=passport_number,
                phone=phone,
                registration_date=registration_date,
                apartment_id=apartment_id
            )
            db.session.add(tenant)
            db.session.commit()
            flash('Квартиронаймача додано')
            return redirect(url_for('tenants'))
        except Exception as e:
            flash(f'Помилка при додаванні: {e}')
    
    apartments = Apartment.query.join(Building).join(Street).all()
    return render_template('tenant_form.html', apartments=apartments)

@app.route('/address/add', methods=['GET', 'POST'])
@login_required
def add_address():
    if current_user.role != 'admin':
        flash('Доступ заборонено. Потрібні права адміністратора')
        return redirect(url_for('tenants'))
    
    if request.method == 'POST':
        try:
            street_name = request.form['street_name']
            building_number = request.form['building_number']
            apartment_number = request.form['apartment_number']
            area = request.form['area']
            rooms = request.form.get('rooms')
            ownership_type = request.form['ownership_type']
            
            street = Street.query.filter_by(name=street_name).first()
            if not street:
                street = Street(name=street_name)
                db.session.add(street)
                db.session.commit()
            
            building = Building.query.filter_by(street_id=street.id, number=building_number).first()
            if not building:
                building = Building(street_id=street.id, number=building_number)
                db.session.add(building)
                db.session.commit()
            
            apartment = Apartment(
                building_id=building.id,
                number=apartment_number,
                area=area,
                rooms=rooms if rooms else None,
                ownership_type=ownership_type
            )
            db.session.add(apartment)
            db.session.commit()
            
            flash('Адресу успішно додано!')
            return redirect(url_for('add_tenant'))
            
        except Exception as e:
            flash(f'Помилка при додаванні адреси: {e}')
    
    return render_template('add_address.html')

# ДОКУМЕНТ 1: Персональна довідка (доступна всім)
@app.route('/tenant/<int:tenant_id>/certificate')
@login_required
def tenant_certificate(tenant_id):
    """Довідка щодо жилплощі для конкретного мешканця - доступна всім"""
    tenant = Tenant.query.join(Apartment).join(Building).join(Street).filter(Tenant.id == tenant_id).first()
    
    if not tenant:
        flash('Мешканця не знайдено')
        return redirect(url_for('tenants'))
    
    # Створюємо PDF документ
    response = make_response()
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=certificate_{tenant_id}.pdf'
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    elements = []
    
    # Заголовок
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1
    )
    elements.append(Paragraph('ДОВІДКА ЩОДО ЖИТЛОВОЇ ПЛОЩІ', title_style))
    elements.append(Spacer(1, 20))
    
    # Дані мешканця
    data = [
        ['ПІБ:', tenant.full_name],
        ['Паспорт:', f"{tenant.passport_series or ''} №{tenant.passport_number}"],
        ['Адреса:', f"вул. {tenant.apartment.building.street.name}, буд. {tenant.apartment.building.number}, кв. {tenant.apartment.number}"],
        ['Площа:', f"{tenant.apartment.area} м²"],
        ['Кількість кімнат:', str(tenant.apartment.rooms)],
        ['Тип власності:', tenant.apartment.ownership_type],
        ['Дата реєстрації:', tenant.registration_date.strftime('%d.%m.%Y')]
    ]
    
    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 30))
    elements.append(Paragraph('Дата видачі: ' + datetime.now().strftime('%d.%m.%Y'), styles['Normal']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph('Підпис: _________________', styles['Normal']))
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    response.set_data(pdf)
    return response

# ДОКУМЕНТ 2: Документ ЖЕКу (тільки для адмінів)
@app.route('/district_report')
@login_required
def district_report():
    """Документ ЖЕКу по всіх вулицях району - тільки для адмінів"""
    if current_user.role != 'admin':
        flash('Доступ заборонено. Тільки адміністратори можуть переглядати документи ЖЕКу')
        return redirect(url_for('tenants'))
    
    # Отримуємо всі дані згруповані по вулицях
    streets_data = Street.query.order_by(Street.name).all()
    
    result = []
    for street in streets_data:
        street_info = {
            'street': street,
            'buildings': [],
            'total_tenants': 0  # Додаємо лічильник мешканців
        }
        
        buildings = Building.query.filter_by(street_id=street.id).order_by(Building.number).all()
        for building in buildings:
            building_info = {
                'building': building,
                'apartments': []
            }
            
            apartments = Apartment.query.filter_by(building_id=building.id).order_by(Apartment.number).all()
            for apartment in apartments:
                tenants = Tenant.query.filter_by(apartment_id=apartment.id).order_by(Tenant.full_name).all()
                apartment_info = {
                    'apartment': apartment,
                    'tenants': tenants
                }
                building_info['apartments'].append(apartment_info)
                
                # Рахуємо мешканців для вулиці
                street_info['total_tenants'] += len(tenants)
            
            street_info['buildings'].append(building_info)
        
        result.append(street_info)
    
    return render_template('district_report.html', streets_data=result)

def init_db():
    try:
        with app.app_context():
            db.session.execute(text('SELECT 1'))
            print("Database connection successful!")
            
            if not Street.query.first():
                # ... (існуючий код)
                
                # Додаємо тестового адміна (без зв'язку з мешканцем)
                if not User.query.filter_by(username='admin').first():
                    admin_user = User(
                        username='admin',
                        password_hash=generate_password_hash('admin'),
                        role='admin'
                        # tenant_id залишаємо NULL
                    )
                    db.session.add(admin_user)
                    db.session.commit()
                
                print("Test data added successfully!")
                
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5089)