from flask import Flask
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    from ptracker.extensions import db, migrate, login_manager

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        from ptracker.models import User

        return db.session.get(User, int(user_id))

    # Initialize data sources
    from ptracker.datasources import init_datasources

    init_datasources(app)

    # Dependency injection
    from ptracker.dependencies import init_services

    init_services(app)

    # Register blueprints
    from ptracker.auth.routes import auth_bp
    from ptracker.price_tracking.routes import price_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(price_bp)

    # Register error handlers
    from ptracker.errors import register_error_handlers

    register_error_handlers(app)

    # Register CLI commands
    from ptracker.commands import seed_db, reset_db

    app.cli.add_command(seed_db)
    app.cli.add_command(reset_db)

    return app
