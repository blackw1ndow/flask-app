from datetime import datetime

from flask import Blueprint

products_bp = Blueprint(
    "products",
    __name__,
    template_folder="templates",
    static_folder="static",
)


@products_bp.record_once
def setup_storage(state):
    """Ініціалізація TinyDB під час реєстрації блюпринта."""
    from .storage import init_storage
    init_storage(state.app.config["PRODUCTS_DB"])


@products_bp.app_template_filter("datetime")
def format_datetime(value):
    """2026-11-05T14:30:00 -> 05.11.2026 14:30"""
    if not value:
        return "—"
    return datetime.fromisoformat(value).strftime("%d.%m.%Y %H:%M")


from . import views