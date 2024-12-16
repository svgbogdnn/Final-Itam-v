from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__, template_folder='D:/Apps/PyCharm/itam/templates')
    app.config.from_object('config.Config')
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.routes.auth import auth
    from app.routes.teacher import teacher
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(teacher, url_prefix='/teacher')
    return app
