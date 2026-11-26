import unittest

from app import create_app


class MainViewsTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

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

    def test_404_page(self):
        """Неіснуюча сторінка показує власний шаблон 404."""
        response = self.client.get("/no-such-page")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Page Not Found", response.data)
        self.assertIn(b"/no-such-page", response.data)

    def test_config_is_testing(self):
        self.assertTrue(self.app.config["TESTING"])
        self.assertEqual(self.app.config["SQLALCHEMY_DATABASE_URI"], "sqlite:///:memory:")


if __name__ == "__main__":
    unittest.main()
