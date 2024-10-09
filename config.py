class Config:
    SECRET_KEY = 'pdN4|%ZvQflO{_W1W\~>tOH`7~e6IU'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///game_catalog.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # Limite de 16MB para uploads
