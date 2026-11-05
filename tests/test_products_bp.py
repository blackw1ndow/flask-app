import os
import shutil
import tempfile
import unittest

from app import app
from app.products.storage import TABLE_NAME, init_storage, open_db


class ProductsReadTestCase(unittest.TestCase):
    """Тести читання товарів з TinyDB (на тимчасовій копії бази)."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.old_db = app.config["PRODUCTS_DB"]
        app.config["PRODUCTS_DB"] = os.path.join(self.tmp_dir, "products.json")
        init_storage(app.config["PRODUCTS_DB"])  # нова база зі стартовими товарами
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self):
        app.config["PRODUCTS_DB"] = self.old_db
        shutil.rmtree(self.tmp_dir)

    def test_storage_is_created(self):
        self.assertTrue(os.path.exists(app.config["PRODUCTS_DB"]))
        with app.app_context(), open_db() as db:
            self.assertEqual(len(db.table(TABLE_NAME)), 3)

    def test_products_list(self):
        response = self.client.get("/product")
        self.assertEqual(response.status_code, 200)
        for name in (b"Laptop", b"Phone", b"PC"):
            self.assertIn(name, response.data)
        self.assertIn("Ноутбуки".encode(), response.data)  # категорія
        self.assertIn(b"$1200.00", response.data)           # ціна з 2 знаками

    def test_products_list_has_detail_links(self):
        response = self.client.get("/product")
        for product_id in (1, 2, 3):
            self.assertIn(f'href="/product/{product_id}"'.encode(), response.data)

    def test_detail_product(self):
        response = self.client.get("/product/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Laptop", response.data)
        self.assertIn("Intel Core i7".encode(), response.data)
        self.assertIn("Немає фото".encode(), response.data)  # заглушка без картинки

    def test_detail_product_not_found(self):
        response = self.client.get("/product/999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("не знайдено".encode(), response.data)

    def test_data_persists_between_runs(self):
        """Повторна ініціалізація не перезаписує вже наявні дані."""
        with app.app_context(), open_db() as db:
            db.table(TABLE_NAME).remove(doc_ids=[1])
        init_storage(app.config["PRODUCTS_DB"])
        response = self.client.get("/product/1")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()