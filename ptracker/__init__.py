from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate = Migrate(app, db)

    from ptracker.datasources import init_datasources

    init_datasources(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        from ptracker.models import User

        return User.query.get(int(user_id))

    # Blueprints
    from ptracker.price_tracking.routes import price_bp
    from ptracker.auth.routes import auth_bp

    app.register_blueprint(price_bp)
    app.register_blueprint(auth_bp)

    # Error handling
    from ptracker.errors import register_error_handlers

    register_error_handlers(app)

    # CLI Commands
    from ptracker.commands import seed_db, reset_db

    app.cli.add_command(seed_db)
    app.cli.add_command(reset_db)

    return app
