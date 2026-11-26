import os
import tempfile

from dotenv import load_dotenv

# Корінь проєкту (папка, де лежать run.py і .env)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    """Спільні налаштування для всіх режимів."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    JSON_AS_ASCII = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Лог-файл для повідомлень з форми контактів (lab5)
    CONTACT_LOG_FILE = os.path.join(BASE_DIR, "logs", "contacts.log")

    # TinyDB для товарів і папка для їхніх фото (lab5)
    PRODUCTS_DB = os.path.join(BASE_DIR, "data", "products.json")
    PRODUCT_UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "products", "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # жорстка межа розміру запиту: 5 МБ


class DevelopmentConfig(Config):
    DEBUG = True
    # Відносний шлях sqlite:///data.sqlite Flask-SQLAlchemy рахує від папки instance/
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///data.sqlite")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

    # Тести не чіпають справжні файли проєкту
    _TMP = os.path.join(tempfile.gettempdir(), "flask-app-tests")
    CONTACT_LOG_FILE = os.path.join(_TMP, "contacts.log")
    PRODUCTS_DB = os.path.join(_TMP, "products.json")
    PRODUCT_UPLOAD_FOLDER = os.path.join(_TMP, "uploads")


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///data.sqlite")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
