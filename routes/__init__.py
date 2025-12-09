from flask import Blueprint
from .tenants import tenants_bp
from .documents import documents_bp
from .buildings import buildings_bp
from .apartments import apartments_bp
from .addresses import address_bp
from .auth import auth_bp 

def register_blueprints(app):
    app.register_blueprint(tenants_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(buildings_bp)
    app.register_blueprint(apartments_bp)
    app.register_blueprint(address_bp)
    app.register_blueprint(auth_bp)  