import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very-secret-key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/housing_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = "redis://localhost:6379/0"
    COUCHDB_URL = "http://couchdb:28102005@localhost:5984/"
    COUCHDB_DB = "certificates"