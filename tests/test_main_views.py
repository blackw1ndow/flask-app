import unittest
from app import app


class MainViewsTestCase(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_homepage(self):
        """Головна сторінка показує User-Agent клієнта."""
        response = self.client.get("/homepage", headers={"User-Agent": "TestBrowser/1.0"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"TestBrowser/1.0", response.data)

    def test_resume_pages(self):
        """Резюме відкривається і за /, і за /resume."""
        for url in ("/", "/resume"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
