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

    from ptracker.datasources import init_datasources

    init_datasources(app)

    # Blueprints
    from ptracker.price_tracking.routes import price_bp
    from ptracker.auth.routes import auth_bp

    app.register_blueprint(price_bp)
    app.register_blueprint(auth_bp)

    # CLI Commands
    from ptracker.commands import seed_db, reset_db

    app.cli.add_command(seed_db)
    app.cli.add_command(reset_db)

    return app
