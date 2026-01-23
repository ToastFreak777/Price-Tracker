from dotenv import dotenv_values

config = dotenv_values(".env")


class Config:
    SECRET_KEY = config.get("SECRET_KYEY") or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = config.get("DATABASE_URL") or "sqlite:///site.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
