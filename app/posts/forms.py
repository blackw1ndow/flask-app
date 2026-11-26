from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import BooleanField, DateTimeLocalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from .models import CATEGORIES


class PostForm(FlaskForm):
    title = StringField(
        "Заголовок",
        validators=[
            DataRequired(message="Вкажіть заголовок."),
            Length(min=2, max=150, message="Заголовок має містити від 2 до 150 символів."),
        ],
    )
    content = TextAreaField(
        "Текст поста",
        render_kw={"rows": 5, "cols": 40},
        validators=[DataRequired(message="Напишіть текст поста.")],
    )
    is_active = BooleanField("Активний пост (показувати у списку)", default=True)
    publish_date = DateTimeLocalField(
        "Дата публікації",
        format="%Y-%m-%dT%H:%M",
        default=datetime.now,  # функція, а не datetime.now(): так дата береться в момент відкриття форми
        validators=[DataRequired(message="Вкажіть дату й час публікації.")],
    )
    category = SelectField(
        "Категорія",
        choices=CATEGORIES,
        validators=[DataRequired(message="Оберіть категорію.")],
    )
    submit = SubmitField("Зберегти")


class DeletePostForm(FlaskForm):
    """Порожня форма: потрібна лише для CSRF-токена під час видалення."""
    submit = SubmitField("Так, видалити")
