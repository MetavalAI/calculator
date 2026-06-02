from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import logging
import os
from flask_login import LoginManager

db = SQLAlchemy()

login_manager = LoginManager()


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    migrate = Migrate(app, db)

    login_manager.init_app(app)

    os.makedirs('logs', exist_ok=True)

    logging.basicConfig(
        filename='logs/errors.log',
        level=logging.ERROR,
        format='%(asctime)s %(levelname)s %(message)s'
    )

    from app.routes import main
    app.register_blueprint(main)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app