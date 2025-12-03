from .auth import auth_bp
from .tenants import tenants_bp
from .addresses import address_bp
from .documents import documents_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(tenants_bp)
    app.register_blueprint(address_bp)
    app.register_blueprint(documents_bp)
