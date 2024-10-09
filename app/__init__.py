from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    migrate = Migrate(app, db)  # Inicializa o Flask-Migrate

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.routes import auth, game
    app.register_blueprint(auth.bp)
    app.register_blueprint(game.bp)

    with app.app_context():
        db.create_all()

    return app

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))