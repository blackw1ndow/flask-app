from decimal import Decimal, InvalidOperation

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileSize
from wtforms import DecimalField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, ValidationError
from wtforms.widgets import TextInput

from .storage import CATEGORIES

ALLOWED_IMAGE_EXTENSIONS = ["png", "jpg", "jpeg"]
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 МБ


class PriceField(DecimalField):
    """DecimalField, що приймає і крапку, і кому та має українське повідомлення про помилку."""

    widget = TextInput()  # звичайне текстове поле, щоб можна було ввести 49,99

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            valuelist = [valuelist[0].strip().replace(",", ".")]
        try:
            super().process_formdata(valuelist)
        except (ValueError, InvalidOperation):
            self.data = None
            raise ValueError("Ціна має бути числом, наприклад 199.99.")


class QuantityField(IntegerField):
    def process_formdata(self, valuelist):
        try:
            super().process_formdata(valuelist)
        except ValueError:
            self.data = None
            raise ValueError("Кількість має бути цілим числом.")


class CategorySelectField(SelectField):
    def pre_validate(self, form):
        if self.data not in dict(self.choices):
            raise ValidationError("Оберіть категорію зі списку.")


def positive_price(form, field):
    if field.data is None:
        return
    if field.data <= 0:
        raise ValidationError("Ціна має бути більшою за 0.")
    if field.data.as_tuple().exponent < -2:
        raise ValidationError("Ціна може мати не більше двох знаків після коми.")


def non_negative(form, field):
    if field.data is not None and field.data < 0:
        raise ValidationError("Кількість не може бути від'ємною.")


class ProductForm(FlaskForm):
    name = StringField(
        "Назва",
        validators=[
            DataRequired(message="Вкажіть назву товару."),
            Length(min=3, max=100, message="Назва має містити від 3 до 100 символів."),
        ],
    )
    content = TextAreaField(
        "Опис",
        validators=[
            DataRequired(message="Додайте опис товару."),
            Length(max=2000, message="Опис не може бути довшим за 2000 символів."),
        ],
        render_kw={"rows": 5, "cols": 40},
    )
    price = PriceField(
        "Ціна, $",
        places=2,
        validators=[InputRequired(message="Вкажіть ціну."), positive_price],
        render_kw={"inputmode": "decimal", "placeholder": "199.99"},
    )
    category = CategorySelectField(
        "Категорія",
        choices=CATEGORIES,
        validators=[DataRequired(message="Оберіть категорію.")],
    )
    quantity = QuantityField(
        "Кількість, шт.",
        validators=[InputRequired(message="Вкажіть кількість."), non_negative],
        render_kw={"inputmode": "numeric", "placeholder": "0"},
    )
    image = FileField(
        "Зображення",
        validators=[
            FileAllowed(ALLOWED_IMAGE_EXTENSIONS, "Дозволені лише файли PNG, JPG і JPEG."),
            FileSize(max_size=MAX_IMAGE_SIZE, message="Файл завеликий: максимум 2 МБ."),
        ],
        render_kw={"accept": ".png,.jpg,.jpeg"},
    )
    submit = SubmitField("Зберегти")
