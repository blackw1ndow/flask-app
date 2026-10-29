import unittest
from app import app


class ProductsBlueprintTestCase(unittest.TestCase):

    def setUp(self):
        """Налаштування клієнта тестування перед кожним тестом."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_products_list(self):
        """Тест маршруту /products/ зі списком усіх товарів."""
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, 200)
        for name in (b"Laptop", b"Phone", b"PC"):
            self.assertIn(name, response.data)

    def test_products_list_has_detail_links(self):
        """На сторінці списку є посилання на детальну сторінку кожного товару."""
        response = self.client.get("/products/")
        for product_id in (1, 2, 3):
            self.assertIn(f'href="/products/{product_id}"'.encode(), response.data)

    def test_detail_product(self):
        """Тест маршруту /products/<id> для існуючого товару."""
        response = self.client.get("/products/1")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Laptop", response.data)
        self.assertIn(b"1200", response.data)
        self.assertIn("Intel Core i7".encode(), response.data)

    def test_detail_product_not_found(self):
        """Неіснуючий товар повертає 404."""
        response = self.client.get("/products/999")
        self.assertEqual(response.status_code, 404)

    def test_detail_product_invalid_id(self):
        """Нечисловий id не підходить під маршрут і теж дає 404."""
        response = self.client.get("/products/abc")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
