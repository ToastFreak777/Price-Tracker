import os

from dotenv import dotenv_values

config = dotenv_values(".env")


def get_env_value(key: str, default: str = "") -> str:
    return os.getenv(key) or config.get(key) or default


class BaseConfig:
    SECRET_KEY = get_env_value("SECRET_KEY", "you-will-never-guess")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    EBAY_CLIENT_ID = get_env_value("EBAY_CLIENT_ID")
    EBAY_CLIENT_SECRET = get_env_value("EBAY_CLIENT_SECRET")

    API_TITLE = "Price Tracker API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/api"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = get_env_value("DB_URI", "sqlite:///site.db")


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = False
    SERVER_NAME = "localhost"


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = get_env_value("DB_URI", "sqlite:///site.db")
