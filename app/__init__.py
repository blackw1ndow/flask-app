import logging
import os

from flask import Flask

app = Flask(__name__)
app.config.from_pyfile("../config.py")


def setup_contact_logger(path):
    """Пише дані з форми контактів у окремий лог-файл."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    logger = logging.getLogger("contacts")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.FileHandler(path, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(handler)


setup_contact_logger(app.config["CONTACT_LOG_FILE"])

from . import views

from .users import users_bp
from .products import products_bp

app.register_blueprint(users_bp, url_prefix="/users")
app.register_blueprint(products_bp, url_prefix="/product")