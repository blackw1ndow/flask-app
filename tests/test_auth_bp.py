import unittest
from app import app


class AuthAndCookiesTestCase(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def login(self, username="user1", password="qwerty"):
        return self.client.post(
            "/users/login",
            data={"username": username, "password": password},
            follow_redirects=True,
        )

    # ---------- Вхід і профіль ----------

    def test_login_page_opens(self):
        response = self.client.get("/users/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn('name="username"'.encode(), response.data)
        self.assertIn('name="password"'.encode(), response.data)

    def test_login_success_redirects_to_profile(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/users/profile")
        self.assertIn("Вхід успішний".encode(), response.data)
        self.assertIn(b"user1", response.data)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess["username"], "user1")

    def test_login_wrong_password(self):
        response = self.login(password="wrong")
        self.assertEqual(response.request.path, "/users/login")
        self.assertIn("Неправильний логін або пароль".encode(), response.data)
        with self.client.session_transaction() as sess:
            self.assertNotIn("username", sess)

    def test_profile_requires_login(self):
        response = self.client.get("/users/profile", follow_redirects=True)
        self.assertEqual(response.request.path, "/users/login")
        self.assertIn("Спершу увійдіть".encode(), response.data)

    def test_logout(self):
        self.login()
        response = self.client.post("/users/logout", follow_redirects=True)
        self.assertEqual(response.request.path, "/users/login")
        self.assertIn("Ви вийшли".encode(), response.data)
        with self.client.session_transaction() as sess:
            self.assertNotIn("username", sess)

    # ---------- Кукі ----------

    def test_add_cookie(self):
        self.login()
        response = self.client.post(
            "/users/cookies/add",
            data={"key": "lang", "value": "uk", "max_age": "3600"},
            follow_redirects=True,
        )
        self.assertIn("Кукі «lang» додано".encode(), response.data)
        self.assertEqual(self.client.get_cookie("lang").value, "uk")

    def test_add_cookie_requires_login(self):
        response = self.client.post("/users/cookies/add", data={"key": "a", "value": "b"})
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(self.client.get_cookie("a"))

    def test_add_cookie_invalid_key(self):
        self.login()
        response = self.client.post(
            "/users/cookies/add", data={"key": "bad key", "value": "x"}, follow_redirects=True
        )
        self.assertIn("Ключ кукі може містити".encode(), response.data)

    def test_delete_cookie_by_key(self):
        self.login()
        self.client.post("/users/cookies/add", data={"key": "lang", "value": "uk"})
        response = self.client.post("/users/cookies/delete", data={"key": "lang"}, follow_redirects=True)
        self.assertIn("Кукі «lang» видалено".encode(), response.data)
        self.assertIsNone(self.client.get_cookie("lang"))

    def test_delete_missing_cookie(self):
        self.login()
        response = self.client.post("/users/cookies/delete", data={"key": "nope"}, follow_redirects=True)
        self.assertIn("не знайдено".encode(), response.data)

    def test_clear_cookies_keeps_session(self):
        self.login()
        self.client.post("/users/cookies/add", data={"key": "a", "value": "1"})
        self.client.post("/users/cookies/add", data={"key": "b", "value": "2"})
        response = self.client.post("/users/cookies/clear", follow_redirects=True)
        self.assertIn("Видалено всі кукі".encode(), response.data)
        self.assertIsNone(self.client.get_cookie("a"))
        self.assertIsNone(self.client.get_cookie("b"))
        self.assertIsNotNone(self.client.get_cookie("session"))

    def test_cookies_table_shows_values(self):
        self.login()
        self.client.post("/users/cookies/add", data={"key": "color", "value": "green"})
        response = self.client.get("/users/profile")
        self.assertIn(b"color", response.data)
        self.assertIn(b"green", response.data)

    # ---------- Тема ----------

    def test_set_dark_theme(self):
        self.login()
        response = self.client.get("/users/theme/dark", follow_redirects=True)
        self.assertEqual(response.request.path, "/users/profile")
        self.assertIn(b'class="theme-dark"', response.data)
        self.assertEqual(self.client.get_cookie("theme").value, "dark")

    def test_theme_persists_after_relogin(self):
        self.login()
        self.client.get("/users/theme/dark")
        self.client.post("/users/logout")
        response = self.login()
        self.assertIn(b'class="theme-dark"', response.data)

    def test_unknown_theme(self):
        self.login()
        response = self.client.get("/users/theme/pink", follow_redirects=True)
        self.assertIn("Невідома кольорова схема".encode(), response.data)
        self.assertIsNone(self.client.get_cookie("theme"))


if __name__ == "__main__":
    unittest.main()
