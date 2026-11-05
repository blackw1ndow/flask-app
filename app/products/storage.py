import os
from datetime import datetime

from flask import current_app
from tinydb import TinyDB

TABLE_NAME = "products"

CATEGORIES = [
    ("laptops", "Ноутбуки"),
    ("phones", "Смартфони"),
    ("computers", "Комп'ютери"),
    ("accessories", "Аксесуари"),
]

SEED_PRODUCTS = [
    {
        "name": "Laptop",
        "content": "Потужний ноутбук з процесором Intel Core i7, 16 ГБ оперативної пам'яті та SSD на 512 ГБ.",
        "price": 1200.00,
        "category": "laptops",
        "quantity": 5,
        "image": None,
    },
    {
        "name": "Phone",
        "content": "Смартфон із 6.5-дюймовим OLED-дисплеєм, подвійною камерою та акумулятором на 5000 мА·год.",
        "price": 800.00,
        "category": "phones",
        "quantity": 12,
        "image": None,
    },
    {
        "name": "PC",
        "content": "Настільний комп'ютер для ігор або роботи з графікою: RTX 4070, 32 ГБ RAM, 1 ТБ SSD.",
        "price": 1800.00,
        "category": "computers",
        "quantity": 3,
        "image": None,
    },
]


def open_db(path=None):
    """Відкриває JSON-файл бази (створює папку, якщо її немає)."""
    path = path or current_app.config["PRODUCTS_DB"]
    return TinyDB(path, create_dirs=True, encoding="utf-8", ensure_ascii=False, indent=2)


def now():
    return datetime.now().isoformat(timespec="seconds")


def init_storage(path):
    """Створює файл бази й таблицю товарів. Стартові товари додаються лише при першому запуску."""
    is_new = not os.path.exists(path)
    with open_db(path) as db:
        table = db.table(TABLE_NAME)
        if is_new:
            table.insert_multiple({**item, "created_at": now()} for item in SEED_PRODUCTS)


def to_product(doc):
    """Документ TinyDB -> словник товару з полем id (= doc_id)."""
    return {**doc, "id": doc.doc_id}


def get_all_products():
    with open_db() as db:
        return [to_product(doc) for doc in db.table(TABLE_NAME).all()]


def get_product(product_id):
    with open_db() as db:
        doc = db.table(TABLE_NAME).get(doc_id=product_id)
        return to_product(doc) if doc else None