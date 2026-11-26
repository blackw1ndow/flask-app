from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column

from app import db

CATEGORIES = [
    ("news", "Новина"),
    ("publication", "Публікація"),
    ("tech", "Технології"),
    ("other", "Інше"),
]


def utcnow():
    """Те саме, що datetime.utcnow(), але без попередження про застарілість у Python 3.12+."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    posted: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    category: Mapped[str] = mapped_column(
        Enum("news", "publication", "tech", "other", name="post_category"),
        default="other",
    )
    # Частина 3: нові поля, додані другою міграцією.
    # server_default потрібен, щоб міграція пройшла, навіть якщо в таблиці вже є пости.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
    author: Mapped[str] = mapped_column(String(20), default="Anonymous", server_default="Anonymous")

    def __repr__(self):
        return f"<Post(id={self.id}, title={self.title!r})>"
