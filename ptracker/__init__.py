from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate = Migrate(app, db)

    from ptracker.main.routes import main

    app.register_blueprint(main)

    from ptracker.commands import seed_db, reset_db

    app.cli.add_command(seed_db)
    app.cli.add_command(reset_db)

    return app
