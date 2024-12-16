import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:1234@localhost/dbitam"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret")

def create_app():
    app = Flask(__name__, template_folder='D:/Apps/PyCharm/itamsvg/templates')
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.routes.auth import auth
    from app.routes.teacher import teacher

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(teacher, url_prefix='/teacher')

    return app