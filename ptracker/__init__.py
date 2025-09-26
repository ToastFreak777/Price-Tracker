from flask import Flask

from ptracker.config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from ptracker.main.routes import main

    app.register_blueprint(main)

    return app
