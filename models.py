from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Street(db.Model):
    __tablename__ = 'streets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

class Building(db.Model):
    __tablename__ = 'buildings'
    id = db.Column(db.Integer, primary_key=True)
    street_id = db.Column(db.Integer, db.ForeignKey('streets.id'), nullable=False)
    number = db.Column(db.String(10), nullable=False)  # Номер будинку: "25", "14А"
    
    street = db.relationship('Street', backref='buildings')

class Apartment(db.Model):
    __tablename__ = 'apartments'
    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer, db.ForeignKey('buildings.id'), nullable=False)
    number = db.Column(db.String(10), nullable=False)  # Номер квартири: "1", "15"
    area = db.Column(db.Numeric(8, 2), nullable=False)  # Площа: 65.50
    rooms = db.Column(db.Integer)  # Кількість кімнат: 3
    ownership_type = db.Column(db.String(50), nullable=False)  # "приватна", "комунальна", "орендна"
    
    building = db.relationship('Building', backref='apartments')

class Tenant(db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    apartment_id = db.Column(db.Integer, db.ForeignKey('apartments.id'), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    passport_series = db.Column(db.String(10))  # Серія: "КН"
    passport_number = db.Column(db.String(20), nullable=False)  # Номер: "123456"
    phone = db.Column(db.String(20))  # Телефон
    registration_date = db.Column(db.Date, nullable=False)
    
    apartment = db.relationship('Apartment', backref='tenants')

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id')) 
    tenant = db.relationship('Tenant', backref='user_account')
