import unittest
from datetime import datetime

from app import create_app, db
from app.posts.models import Post


class PostTestCase(unittest.TestCase):
    """CRUD постів на базі SQLite у пам'яті (TestingConfig)."""

    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        # Створення бази в контексті додатка
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        # Очищення бази після кожного тесту
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    # ---------- допоміжні ----------

    def add_post(self, **kwargs):
        data = {"title": "Перший пост", "content": "Текст", "category": "news",
                "posted": datetime(2026, 11, 1, 10, 0), "is_active": True}
        data.update(kwargs)
        with self.app.app_context():
            post = Post(**data)
            db.session.add(post)
            db.session.commit()
            return post.id

    def get_post(self, post_id):
        with self.app.app_context():
            return db.session.get(Post, post_id)

    def form_data(self, **kwargs):
        data = {"title": "My first post", "content": "This is TDD!",
                "publish_date": "2026-11-19T14:30", "category": "tech", "is_active": "y"}
        data.update(kwargs)
        return data

    # ---------- модель ----------

    def test_model_defaults_and_repr(self):
        with self.app.app_context():
            post = Post(title="Test", content="Example post")
            db.session.add(post)
            db.session.commit()
            self.assertIsNotNone(post.posted)
            self.assertEqual(post.category, "other")
            self.assertTrue(post.is_active)
            self.assertEqual(post.author, "Anonymous")
            self.assertEqual(repr(post), "<Post(id=1, title='Test')>")

    # ---------- Create ----------

    def test_create_page_renders_form(self):
        response = self.client.get("/post/create")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        for field in ('name="title"', "<textarea", 'name="is_active"', 'type="datetime-local"', "<select"):
            self.assertIn(field, text)
        self.assertNotIn('name="author"', text)  # автора у формі немає

    def test_create_post(self):
        response = self.client.post("/post/create", data=self.form_data(), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Пост «My first post» додано".encode(), response.data)
        with self.app.app_context():
            post = db.session.scalars(db.select(Post).filter_by(title="My first post")).first()
            self.assertIsNotNone(post)
            self.assertEqual(post.content, "This is TDD!")
            self.assertEqual(post.posted, datetime(2026, 11, 19, 14, 30))
            self.assertEqual(post.category, "tech")
            self.assertEqual(post.author, "Anonymous")

    def test_create_post_redirects_prg(self):
        response = self.client.post("/post/create", data=self.form_data())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/post/1")

    def test_author_is_user_from_session(self):
        with self.client.session_transaction() as sess:
            sess["username"] = "user1"
        self.client.post("/post/create", data=self.form_data())
        self.assertEqual(self.get_post(1).author, "user1")

    def test_create_inactive_post(self):
        data = self.form_data()
        del data["is_active"]                      # чекбокс не відмічено
        self.client.post("/post/create", data=data)
        self.assertFalse(self.get_post(1).is_active)

    def test_create_invalid_post(self):
        response = self.client.post("/post/create", data=self.form_data(title="", content="", category="cars"))
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("Пост не збережено", text)
        self.assertIn("Вкажіть заголовок", text)
        self.assertIn("Напишіть текст поста", text)
        with self.app.app_context():
            self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(Post)), 0)

    # ---------- Read ----------

    def test_list_shows_active_posts_newest_first(self):
        self.add_post(title="Старий", posted=datetime(2026, 1, 1))
        self.add_post(title="Новий", posted=datetime(2026, 6, 1))
        self.add_post(title="Прихований", is_active=False)
        response = self.client.get("/post")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("Новий", text)
        self.assertIn("Старий", text)
        self.assertNotIn("Прихований", text)
        self.assertLess(text.index("Новий"), text.index("Старий"))  # спадання за датою
        self.assertIn("default.jpg", text)
        self.assertIn("Add Post", text)

    def test_list_truncates_content(self):
        self.add_post(content="слово " * 50)
        text = self.client.get("/post").get_data(as_text=True)
        self.assertNotIn("слово " * 30, text)
        self.assertIn("...", text)

    def test_detail_post(self):
        post_id = self.add_post(author="admin")
        response = self.client.get(f"/post/{post_id}")
        self.assertEqual(response.status_code, 200)
        for text in ("Перший пост", "Текст", "admin", "Новина", "01.11.2026 10:00", "Edit", "Delete"):
            self.assertIn(text.encode(), response.data)

    def test_detail_not_found(self):
        response = self.client.get("/post/999")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Page Not Found", response.data)

    # ---------- Update ----------

    def test_update_form_prefilled(self):
        post_id = self.add_post()
        text = self.client.get(f"/post/{post_id}/update").get_data(as_text=True)
        self.assertIn('value="Перший пост"', text)
        self.assertIn('value="2026-11-01T10:00"', text)   # дата з поля posted
        self.assertIn('<option selected value="news">', text)

    def test_update_post(self):
        post_id = self.add_post(author="admin")
        response = self.client.post(
            f"/post/{post_id}/update",
            data=self.form_data(title="Оновлений", publish_date="2026-12-24T18:00"),
        )
        self.assertEqual(response.headers["Location"], f"/post/{post_id}")
        post = self.get_post(post_id)
        self.assertEqual(post.title, "Оновлений")
        self.assertEqual(post.posted, datetime(2026, 12, 24, 18, 0))
        self.assertEqual(post.category, "tech")
        self.assertEqual(post.author, "admin")             # автор не змінюється

    def test_update_invalid_not_saved(self):
        post_id = self.add_post()
        response = self.client.post(f"/post/{post_id}/update", data=self.form_data(title=""))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_post(post_id).title, "Перший пост")

    def test_update_not_found(self):
        self.assertEqual(self.client.get("/post/999/update").status_code, 404)

    # ---------- Delete ----------

    def test_delete_confirm_page(self):
        post_id = self.add_post()
        response = self.client.get(f"/post/{post_id}/delete")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Перший пост".encode(), response.data)
        self.assertIn('method="post"'.encode(), response.data)
        self.assertIsNotNone(self.get_post(post_id))       # GET нічого не видаляє

    def test_delete_post(self):
        post_id = self.add_post()
        response = self.client.post(f"/post/{post_id}/delete", follow_redirects=True)
        self.assertEqual(response.request.path, "/post")
        self.assertIn("Пост «Перший пост» видалено".encode(), response.data)
        self.assertIsNone(self.get_post(post_id))

    def test_delete_not_found(self):
        self.assertEqual(self.client.post("/post/999/delete").status_code, 404)

    def test_delete_without_csrf_is_rejected(self):
        post_id = self.add_post()
        self.app.config["WTF_CSRF_ENABLED"] = True
        self.client.post(f"/post/{post_id}/delete")
        self.assertIsNotNone(self.get_post(post_id))


if __name__ == "__main__":
    unittest.main()
