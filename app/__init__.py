from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import logging
import sys
import os
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)

    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

# Logging Setup
    os.makedirs('logs', exist_ok=True)

    fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(fmt)

    file_handler = logging.FileHandler('logs/errors.log')
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(fmt)

# Werkzeug - request logs
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.DEBUG)
    werkzeug_logger.handlers.clear()
    werkzeug_logger.addHandler(console_handler)
    werkzeug_logger.addHandler(file_handler)
    werkzeug_logger.propagate = False

# SQLAlchemy - query logs (INFO karo agar queries dekhni ho)
    sql_logger = logging.getLogger('sqlalchemy.engine')
    sql_logger.setLevel(logging.WARNING)
    sql_logger.addHandler(console_handler)
    sql_logger.propagate = False

# Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    app.logger.setLevel(logging.DEBUG)
# Logging Setup End
    from app.routes import main
    app.register_blueprint(main)
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app