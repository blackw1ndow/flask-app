import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
JSON_AS_ASCII = False

CONTACT_LOG_FILE = os.path.join(BASE_DIR, "logs", "contacts.log")
PRODUCTS_DB = os.path.join(BASE_DIR, "data", "products.json")