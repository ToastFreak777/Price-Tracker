import os

from flask import Flask
from config import DevelopmentConfig, TestingConfig, ProductionConfig
from flask_smorest import Api
from sqlalchemy import inspect


def create_app(override_config=None):
    env = os.getenv("FLASK_ENV", "development")
    print(env)
    if env == "production":
        config_class = ProductionConfig
    elif env == "testing":
        config_class = TestingConfig
    else:
        config_class = DevelopmentConfig

    app = Flask(__name__)
    app.config.from_object(override_config or config_class)
    api = Api(app)

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
    from ptracker.main.routes import main_bp
    from ptracker.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(price_bp)
    app.register_blueprint(main_bp)
    api.register_blueprint(api_bp)

    # Register error handlers
    from ptracker.errors import register_error_handlers

    register_error_handlers(app)

    # Register CLI commands
    from ptracker.commands import seed_db, reset_db, update_items

    app.cli.add_command(seed_db)
    app.cli.add_command(reset_db)
    app.cli.add_command(update_items)

    with app.app_context():
        if app.config.get("TESTING"):
            db.create_all()
        else:
            inspector = inspect(db.engine)
            if "user" not in inspector.get_table_names():
                db.create_all()

    return app
