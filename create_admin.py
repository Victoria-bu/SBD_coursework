# create_admin.py
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():  # Обов'язково створюємо контекст додатка
    # Перевіряємо, чи адміністратор вже існує
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print("Admin already exists.")
    else:
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin created successfully!")
