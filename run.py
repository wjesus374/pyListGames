from app import create_app, db
from flask_migrate import Migrate

app = create_app()  # A função create_app deve criar e retornar a instância do aplicativo
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()
