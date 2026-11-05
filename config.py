import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
JSON_AS_ASCII = False

# Лог-файл для повідомлень з форми контактів
CONTACT_LOG_FILE = os.path.join(BASE_DIR, "logs", "contacts.log")

# TinyDB: JSON-файл із товарами
PRODUCTS_DB = os.path.join(BASE_DIR, "data", "products.json")

# Завантаження зображень товарів
PRODUCT_UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "products", "static", "uploads")
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # жорстка межа розміру запиту: 5 МБ
