from flask import Flask, render_template, redirect, url_for, request, flash
from config import Config
from models import db, User, Tenant, Apartment, Building, Street  # імпортуємо db з models
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text

# Create Flask app
def create_app(testing=False):
    app = Flask(__name__)

    if testing:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # IN-MEMORY DB
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test-secret-key'
    else:
        app.config.from_object(Config)

    # Ініціалізація SQLAlchemy
    db.init_app(app)

    # Ініціалізація Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID (required for Flask-Login)"""
        return User.query.get(int(user_id))
    
    # Реєстрація блюпринтів
    from routes import register_blueprints
    register_blueprints(app)

    # Головна сторінка
    @app.route('/')
    def index():
        """Main page → redirect to login"""
        return redirect(url_for('auth.login'))

    # Реєстрація користувача
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Register a new user (link to tenant by full name)"""
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            full_name = request.form['full_name']
            role = request.form.get('role', 'user')

            try:
                first_name, last_name = full_name.strip().split(' ', 1)
            except ValueError:
                flash("Enter full name in format: 'FirstName LastName'")
                return render_template('register.html')
            
            # Check if username exists
            if User.query.filter_by(username=username).first():
                flash('User already exists')
                return render_template('register.html')

            # Search for tenant
            tenant = Tenant.query.filter_by(first_name=first_name, last_name=last_name).first()
            if not tenant:
                flash('Tenant with this full name not found')
                return render_template('register.html')

            # One user = one tenant
            if User.query.filter_by(tenant_id=tenant.id).first():
                flash('An account for this tenant already exists')
                return render_template('register.html')

            # Create user
            user = User(
                username=username,
                password_hash=generate_password_hash(password),
                role=role,
                tenant_id=tenant.id
            )
            db.session.add(user)
            db.session.commit()

            flash('Registration successful! Please log in.')
            return redirect(url_for('auth.login'))

        return render_template('register.html')

    return app


# Для запуску без тестування
if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        # Check database availability
        try:
            db.session.execute(text('SELECT 1'))
            print("Database connection successful!")
        except Exception as e:
            print(f"Database connection error: {e}")
            exit(1)

        # Create tables
        db.create_all()

        # Add test data (first run)
        if not Street.query.first():
            street = Street(name="Test Street")
            db.session.add(street)
            db.session.commit()

            building = Building(street_id=street.id, number="1")
            db.session.add(building)
            db.session.commit()

            apartment = Apartment(
                building_id=building.id,
                number="1",
                area=50,
                rooms=2,
                ownership_type="Private"
            )
            db.session.add(apartment)
            db.session.commit()

            # Add admin
            if not User.query.filter_by(username='admin').first():
                admin_user = User(
                    username='admin',
                    password_hash=generate_password_hash('admin'),
                    role='admin'
                )
                db.session.add(admin_user)
                db.session.commit()

            print("Test data added successfully!")

    app.run(debug=True, port=5089)