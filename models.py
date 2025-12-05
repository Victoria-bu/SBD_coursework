from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
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
    number = db.Column(db.String(10), nullable=False)  # Номер будинку: "25", "14А"
    street = db.relationship('Street', backref='buildings')

    """Кількість квартир у будинку"""
    @property
    def apartment_count(self):
        return len(self.apartments)

class Apartment(db.Model):
    __tablename__ = 'apartments'
    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer, db.ForeignKey('buildings.id'), nullable=False)
    number = db.Column(db.String(10), nullable=False)  # Номер квартири: "1", "15"
    area = db.Column(db.Numeric(8, 2), nullable=False)  # Площа: 65.50
    rooms = db.Column(db.Integer)  # Кількість кімнат: 3
    ownership_type = db.Column(db.String(50), nullable=False)  # "приватна", "комунальна", "орендна"
    building = db.relationship('Building', backref='apartments')
    """Чи заселена квартира"""
    @property
    def is_occupied(self):
        return len(self.tenants) > 0

class Person(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    def getFullInfo(self):
        return f"{self.last_name} {self.first_name}"

class Tenant(Person):
    __tablename__ = 'tenants'
    apartment_id = db.Column(db.Integer, db.ForeignKey("apartments.id"))
    passport_series = db.Column(db.String(10))  # Серія: "КН"
    passport_number = db.Column(db.String(20), nullable=False)  # Номер: "123456"
    phone = db.Column(db.String(20))  # Телефон
    registration_date = db.Column(db.Date, nullable=False)

    apartment = db.relationship("Apartment", backref="tenants")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @full_name.setter
    def full_name(self, value):
        parts = value.split(" ", 1)
        self.first_name = parts[0]
        self.last_name = parts[1] if len(parts) > 1 else ""

    def validatePassport(self):
        """Перевірка паспорта: серія+номер"""
        import re
        passport_full = f"{self.passport_series}{self.passport_number}"
        return bool(re.match(r"^[A-ZА-ЯІЇЄ]{2}\d{6}$", passport_full))

    def isOccupied(self):
        """Перевірка, чи живе людина у квартирі"""
        return self.apartment is not None

    def getTenancyDuration(self):
        return (datetime.utcnow().date() - self.registration_date).days

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)  # зберігаємо хеш
    role = db.Column(db.String(20), nullable=False)

    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True)
    tenant = db.relationship('Tenant', backref='user_account')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def authenticate(self, password):
        return check_password_hash(self.password_hash, password)

    def isAdmin(self):
        return self.role == 'admin'
