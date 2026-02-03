from dotenv import dotenv_values

config = dotenv_values(".env")


class Config:
    SECRET_KEY = config.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = config.get("DB_URI") or "sqlite:///site.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    EBAY_CLIENT_ID = config.get("EBAY_CLIENT_ID") or ""
    EBAY_CLIENT_SECRET = config.get("EBAY_CLIENT_SECRET") or ""
