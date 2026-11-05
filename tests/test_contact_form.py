import unittest
import uuid

from app import app


class ContactFormTestCase(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()
        self.valid = {
            "name": "Ivan",
            "email": "ivan@example.com",
            "phone": "+380931234567",
            "subject": "question",
            "message": "Привіт! Тестове повідомлення.",
        }

    def tearDown(self):
        app.config["WTF_CSRF_ENABLED"] = True

    def test_form_renders_fields(self):
        response = self.client.get("/contacts")
        self.assertEqual(response.status_code, 200)
        for name in (b'name="name"', b'name="email"', b'name="phone"', b"<select", b"<textarea"):
            self.assertIn(name, response.data)

    def test_valid_form_redirects_and_flashes(self):
        response = self.client.post("/contacts", data=self.valid)
        self.assertEqual(response.status_code, 302)  # Post/Redirect/Get
        page = self.client.get(response.headers["Location"])
        self.assertIn("Повідомлення надіслано".encode(), page.data)

    def test_valid_form_is_logged(self):
        marker = "msg-" + uuid.uuid4().hex[:8]
        self.client.post("/contacts", data={**self.valid, "message": marker})
        with open(app.config["CONTACT_LOG_FILE"], encoding="utf-8") as log:
            self.assertIn(marker, log.read())

    def test_invalid_form_shows_errors(self):
        data = {**self.valid, "name": "Iv", "email": "bad", "phone": "0931234567", "message": ""}
        response = self.client.post("/contacts", data=data)
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("Повідомлення не надіслано", text)
        self.assertIn("від 4 до 10 символів", text)
        self.assertIn("Неправильний формат email", text)
        self.assertIn("+380XXXXXXXXX", text)
        self.assertIn("Напишіть повідомлення", text)

    def test_message_too_long(self):
        response = self.client.post("/contacts", data={**self.valid, "message": "a" * 501})
        self.assertIn("не може бути довшим за 500".encode(), response.data)

    def test_csrf_protection(self):
        app.config["WTF_CSRF_ENABLED"] = True
        response = self.client.post("/contacts", data=self.valid)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Повідомлення не надіслано".encode(), response.data)


if __name__ == "__main__":
    unittest.main()