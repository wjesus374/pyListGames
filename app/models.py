from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    games = db.relationship('UserGameAssociation', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(100), nullable=False)
    release_year = db.Column(db.Integer, nullable=False)
    developer = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100), nullable=True)
    style = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    users = db.relationship('UserGameAssociation', backref='game', lazy=True)

class UserGameAssociation(db.Model):
    __tablename__ = 'user_game_association'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), primary_key=True)
    media = db.Column(db.String(20), nullable=False)
    rating = db.Column(db.Integer, nullable=True)
