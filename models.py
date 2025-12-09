from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import check_password_hash, generate_password_hash  

db = SQLAlchemy()

class Street(db.Model):
    __tablename__ = 'streets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    """Кількість будинків на вулиці"""
    @property
    def building_count(self):
        return len(self.buildings)

class Building(db.Model):
    __tablename__ = 'buildings'
    id = db.Column(db.Integer, primary_key=True)
    street_id = db.Column(db.Integer, db.ForeignKey('streets.id'), nullable=False)
    number = db.Column(db.String(10), nullable=False) 
    street = db.relationship('Street', backref='buildings')

    """Кількість квартир у будинку"""
    @property
    def apartment_count(self):
        return len(self.apartments)

class Apartment(db.Model):
    __tablename__ = 'apartments'
    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer, db.ForeignKey('buildings.id'), nullable=False)
    number = db.Column(db.String(10), nullable=False)  
    area = db.Column(db.Numeric(8, 2), nullable=False)  
    rooms = db.Column(db.Integer, default=1)
    ownership_type = db.Column(db.String(50), nullable=False, default='private') 
    building = db.relationship('Building', backref='apartments')
    
    @property
    def is_occupied(self):
        """Return True if apartment has tenants"""
        if hasattr(self, 'tenants'):
            return len(self.tenants) > 0
        from models import Tenant
        return Tenant.query.filter_by(apartment_id=self.id).count() > 0
    
class Person(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @full_name.setter
    def full_name(self, value):
        if value:
            parts = value.split(" ", 1)
            self.first_name = parts[0]
            self.last_name = parts[1] if len(parts) > 1 else ""

class Tenant(Person):
    __tablename__ = 'tenants'
    apartment_id = db.Column(db.Integer, db.ForeignKey("apartments.id"))
    passport_series = db.Column(db.String(10), default='')  
    passport_number = db.Column(db.String(20), nullable=False)  
    phone = db.Column(db.String(20), default='')  
    registration_date = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())

    apartment = db.relationship("Apartment", backref="tenants")
    
    def __init__(self, **kwargs):
        # Обробка full_name перед ініціалізацією
        if 'full_name' in kwargs:
            full_name = kwargs.pop('full_name')
            parts = full_name.split(" ", 1)
            kwargs['first_name'] = parts[0]
            kwargs['last_name'] = parts[1] if len(parts) > 1 else ""
        super().__init__(**kwargs)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)  # зберігаємо хеш
    role = db.Column(db.String(20), nullable=False, default='user')

    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True)
    tenant = db.relationship('Tenant', backref='user_account')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'