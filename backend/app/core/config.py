import os
from dotenv import load_dotenv

load_dotenv()


ENVIRONMENT = os.getenv("FLASK_ENV")
PORT = int(os.getenv("PORT", "3201"))
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me")
JWT_TOKEN_EXPIRY_HOURS = 24
JWT_COOKIE_NAME = "access_token"

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "better_assignment")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


class Config:
    """base config"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SECRET_KEY = SECRET_KEY
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    """dev config"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """test config"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    """prod config"""
    LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR")
    SQLALCHEMY_ECHO = False


configs = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
