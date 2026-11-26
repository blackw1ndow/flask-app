import logging
import os

from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from .config import config


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
migrate = Migrate()


def setup_contact_logger(path):
    """Пише дані з форми контактів у окремий лог-файл."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    logger = logging.getLogger("contacts")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    # Якщо логер уже пише в інший файл (наприклад, у тестах), замінюємо обробник
    for handler in list(logger.handlers):
        if getattr(handler, "baseFilename", None) != os.path.abspath(path):
            logger.removeHandler(handler)
            handler.close()
    if not logger.handlers:
        handler = logging.FileHandler(path, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(handler)


def create_app(config_name=None):
    """Application factory: створює застосунок під потрібний режим."""
    config_name = config_name or os.environ.get("FLASK_CONFIG", "default")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    setup_contact_logger(app.config["CONTACT_LOG_FILE"])

    from .views import main_bp
    from .users import users_bp
    from .products import products_bp
    from .posts import post_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(products_bp, url_prefix="/product")
    app.register_blueprint(post_bp, url_prefix="/post")

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html", title="Сторінку не знайдено"), 404

    return app
