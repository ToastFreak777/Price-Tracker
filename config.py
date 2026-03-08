from dotenv import dotenv_values

config = dotenv_values(".env")


class BaseConfig:
    SECRET_KEY = config.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    EBAY_CLIENT_ID = config.get("EBAY_CLIENT_ID") or ""
    EBAY_CLIENT_SECRET = config.get("EBAY_CLIENT_SECRET") or ""

    API_TITLE = "Price Tracker API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/api"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = config.get("DB_URI") or "sqlite:///site.db"


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = False
    SERVER_NAME = "localhost"


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = config.get("DB_URI") or "sqlite:///site.db"
