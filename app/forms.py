from flask_wtf import FlaskForm
from wtforms import EmailField, SelectField, StringField, SubmitField, TelField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Regexp

SUBJECTS = [
    ("cooperation", "Співпраця"),
    ("job", "Пропозиція роботи"),
    ("question", "Питання"),
    ("other", "Інше"),
]


class ContactForm(FlaskForm):
    name = StringField(
        "Ім'я",
        validators=[
            DataRequired(message="Вкажіть ім'я."),
            Length(min=4, max=10, message="Ім'я має містити від 4 до 10 символів."),
        ],
    )
    email = EmailField(
        "Email",
        validators=[
            DataRequired(message="Вкажіть email."),
            Email(message="Неправильний формат email."),
        ],
    )
    phone = TelField(
        "Телефон",
        validators=[
            DataRequired(message="Вкажіть номер телефону."),
            Regexp(r"^\+380\d{9}$", message="Телефон має бути у форматі +380XXXXXXXXX."),
        ],
    )
    subject = SelectField(
        "Тема",
        choices=SUBJECTS,
        validators=[DataRequired(message="Оберіть тему.")],
    )
    message = TextAreaField(
        "Повідомлення",
        validators=[
            DataRequired(message="Напишіть повідомлення."),
            Length(max=500, message="Повідомлення не може бути довшим за 500 символів."),
        ],
    )
    submit = SubmitField("Надіслати")