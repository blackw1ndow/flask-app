import io
import os
import re
import shutil
import tempfile
import unittest

from app import app
from app.products.storage import TABLE_NAME, init_storage, open_db

VALID = {
    "name": "Gaming Mouse",
    "content": "Бездротова миша з сенсором 26000 DPI.",
    "price": "49.99",
    "quantity": "10",
    "category": "accessories",
}


def fake_image(filename="photo.png", size=16):
    return (io.BytesIO(b"\x89PNG" + b"0" * size), filename)


class ProductsCrudTestCase(unittest.TestCase):
    """CRUD товарів на тимчасовій базі й тимчасовій папці для фото."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.old_config = {k: app.config[k] for k in ("PRODUCTS_DB", "PRODUCT_UPLOAD_FOLDER")}
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            PRODUCTS_DB=os.path.join(self.tmp_dir, "products.json"),
            PRODUCT_UPLOAD_FOLDER=os.path.join(self.tmp_dir, "uploads"),
        )
        init_storage(app.config["PRODUCTS_DB"])  # 3 стартові товари з id 1, 2, 3
        self.client = app.test_client()

    def tearDown(self):
        app.config.update(self.old_config, WTF_CSRF_ENABLED=True)
        shutil.rmtree(self.tmp_dir)

    # ---------- допоміжні ----------

    def post(self, url, data):
        return self.client.post(url, data=data, content_type="multipart/form-data")

    def product(self, product_id):
        with app.app_context(), open_db() as db:
            return db.table(TABLE_NAME).get(doc_id=product_id)

    def count(self):
        with app.app_context(), open_db() as db:
            return len(db.table(TABLE_NAME))

    def uploads(self):
        folder = app.config["PRODUCT_UPLOAD_FOLDER"]
        return os.listdir(folder) if os.path.isdir(folder) else []

    # ---------- Create ----------

    def test_add_page_renders_form(self):
        response = self.client.get("/product/add")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        for field in ('name="name"', 'name="price"', 'name="quantity"', 'name="image"', "<select", "<textarea"):
            self.assertIn(field, text)
        self.assertIn('enctype="multipart/form-data"', text)

    def test_create_without_image(self):
        response = self.post("/product/add", VALID)
        self.assertEqual(response.status_code, 302)          # PRG
        self.assertEqual(response.headers["Location"], "/product/4")
        product = self.product(4)
        self.assertEqual(product["name"], "Gaming Mouse")
        self.assertEqual(product["price"], 49.99)
        self.assertEqual(product["quantity"], 10)
        self.assertIsNone(product["image"])
        self.assertTrue(product["created_at"])                # встановлено автоматично

        page = self.client.get("/product/4")
        self.assertIn("Товар «Gaming Mouse» додано".encode(), page.data)
        self.assertIn("Немає фото".encode(), page.data)

    def test_create_with_image_uses_uuid_name(self):
        self.post("/product/add", {**VALID, "image": fake_image("my photo.JPG")})
        image = self.product(4)["image"]
        self.assertRegex(image, r"^uploads/[0-9a-f]{32}\.jpg$")
        self.assertEqual(self.uploads(), [os.path.basename(image)])

    def test_create_accepts_comma_in_price(self):
        self.post("/product/add", {**VALID, "price": "19,90"})
        self.assertEqual(self.product(4)["price"], 19.9)

    def test_create_invalid_data(self):
        data = {"name": "Ab", "content": "", "price": "0", "quantity": "-1", "category": "cars"}
        response = self.post("/product/add", data)
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("Товар не збережено", text)
        self.assertIn("від 3 до 100 символів", text)
        self.assertIn("Додайте опис", text)
        self.assertIn("більшою за 0", text)
        self.assertIn("не може бути від", text)
        self.assertIn("Оберіть категорію зі списку", text)
        self.assertEqual(self.count(), 3)

    def test_price_more_than_two_decimals(self):
        response = self.post("/product/add", {**VALID, "price": "9.999"})
        self.assertIn("не більше двох знаків".encode(), response.data)
        self.assertEqual(self.count(), 3)

    def test_quantity_must_be_integer(self):
        response = self.post("/product/add", {**VALID, "quantity": "1.5"})
        self.assertIn("цілим числом".encode(), response.data)

    def test_zero_quantity_is_allowed(self):
        self.post("/product/add", {**VALID, "quantity": "0"})
        self.assertEqual(self.product(4)["quantity"], 0)

    def test_wrong_image_format(self):
        response = self.post("/product/add", {**VALID, "image": fake_image("anim.gif")})
        self.assertIn("лише файли PNG, JPG і JPEG".encode(), response.data)
        self.assertEqual(self.count(), 3)
        self.assertEqual(self.uploads(), [])

    def test_image_too_large(self):
        big = fake_image("big.png", size=2 * 1024 * 1024 + 1)
        response = self.post("/product/add", {**VALID, "image": big})
        self.assertIn("Файл завеликий".encode(), response.data)
        self.assertEqual(self.count(), 3)

    # ---------- Read ----------

    def test_list_shows_new_product(self):
        self.post("/product/add", {**VALID, "image": fake_image()})
        text = self.client.get("/product").get_data(as_text=True)
        self.assertIn("Gaming Mouse", text)
        self.assertIn("$49.99", text)
        self.assertIn("Аксесуари", text)
        self.assertIn("10 шт.", text)
        self.assertRegex(text, r'src="/product/static/uploads/[0-9a-f]{32}\.png"')

    # ---------- Update ----------

    def test_edit_page_prefilled(self):
        text = self.client.get("/product/1/edit").get_data(as_text=True)
        self.assertIn('value="Laptop"', text)
        self.assertIn('value="1200.00"', text)
        self.assertIn("Intel Core i7", text)

    def test_edit_keeps_id_and_created_at(self):
        before = self.product(1)
        response = self.post("/product/1/edit", {**VALID, "name": "Laptop Pro", "price": "1300.50"})
        self.assertEqual(response.headers["Location"], "/product/1")
        after = self.product(1)
        self.assertEqual(after.doc_id, 1)
        self.assertEqual(after["created_at"], before["created_at"])
        self.assertEqual(after["name"], "Laptop Pro")
        self.assertEqual(after["price"], 1300.5)
        self.assertEqual(self.count(), 3)

    def test_edit_keeps_image_when_no_new_file(self):
        self.post("/product/add", {**VALID, "image": fake_image()})
        image = self.product(4)["image"]
        self.post("/product/4/edit", {**VALID, "name": "Renamed"})
        self.assertEqual(self.product(4)["image"], image)
        self.assertEqual(len(self.uploads()), 1)

    def test_edit_replaces_image_and_removes_old_file(self):
        self.post("/product/add", {**VALID, "image": fake_image("a.png")})
        old = self.product(4)["image"]
        self.post("/product/4/edit", {**VALID, "image": fake_image("b.jpeg")})
        new = self.product(4)["image"]
        self.assertNotEqual(old, new)
        self.assertTrue(new.endswith(".jpeg"))
        self.assertEqual(self.uploads(), [os.path.basename(new)])

    def test_edit_remove_image(self):
        self.post("/product/add", {**VALID, "image": fake_image()})
        self.post("/product/4/edit", {**VALID, "remove_image": "y"})
        self.assertIsNone(self.product(4)["image"])
        self.assertEqual(self.uploads(), [])

    def test_edit_invalid_data_not_saved(self):
        response = self.post("/product/1/edit", {**VALID, "name": "X"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Зміни не збережено".encode(), response.data)
        self.assertEqual(self.product(1)["name"], "Laptop")

    def test_edit_not_found(self):
        self.assertEqual(self.client.get("/product/999/edit").status_code, 404)

    # ---------- Delete ----------

    def test_delete_product_and_image(self):
        self.post("/product/add", {**VALID, "image": fake_image()})
        response = self.client.post("/product/4/delete")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/product")
        self.assertIsNone(self.product(4))
        self.assertEqual(self.uploads(), [])
        page = self.client.get("/product")
        self.assertIn("Товар «Gaming Mouse» видалено".encode(), page.data)

    def test_delete_requires_post(self):
        self.assertEqual(self.client.get("/product/1/delete").status_code, 405)
        self.assertIsNotNone(self.product(1))

    def test_delete_not_found(self):
        self.assertEqual(self.client.post("/product/999/delete").status_code, 404)

    def test_delete_page_has_confirmation(self):
        text = self.client.get("/product/1").get_data(as_text=True)
        self.assertIn('id="deleteModal"', text)
        self.assertIn("Видалити товар?", text)

    def test_delete_without_csrf_token_is_rejected(self):
        app.config["WTF_CSRF_ENABLED"] = True
        self.client.post("/product/1/delete")
        self.assertIsNotNone(self.product(1))

    def test_ids_are_never_reused(self):
        """Після видалення останнього товару новий отримує новий id."""
        self.post("/product/add", VALID)
        self.client.post("/product/4/delete")
        response = self.post("/product/add", VALID)
        self.assertEqual(response.headers["Location"], "/product/5")
        self.assertEqual(self.client.get("/product/4").status_code, 404)

    def test_full_crud_cycle(self):
        """Додати -> переглянути -> змінити -> видалити."""
        self.post("/product/add", VALID)
        self.assertIn(b"Gaming Mouse", self.client.get("/product/4").data)
        self.post("/product/4/edit", {**VALID, "quantity": "7"})
        self.assertEqual(self.product(4)["quantity"], 7)
        self.client.post("/product/4/delete")
        self.assertEqual(self.client.get("/product/4").status_code, 404)


if __name__ == "__main__":
    unittest.main()
