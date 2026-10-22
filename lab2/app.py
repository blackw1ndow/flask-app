from flask import Flask, render_template, request

app = Flask(__name__)

PROFILE = {
    "name": "Анатолій Кульчицький",
    "position": "Розробник",
    "contacts": [
        {"icon": "envelope-fill", "text": "kulchanatolii@gmail.com", "url": "mailto:kulchanatolii@gmail.com"},
        {"icon": "telephone-fill", "text": "+380935164742", "url": "tel:+380935164742"},
        {"icon": "geo-alt-fill", "text": "Івано-Франківськ", "url": None},
        {"icon": "github", "text": "GitHub", "url": "https://github.com/blackw1ndow"},
        {"icon": "linkedin", "text": "LinkedIn", "url": "#"},
        {"icon": "telegram", "text": "Telegram", "url": "#"},
    ],
}

RESUME = {
    "about": (
        "Студент спеціальності «Інженерія програмного забезпечення». Пишу на Python і Lua: "
        "автоматизую рутинні задачі, створюю Telegram-ботів і скрипти для збору даних. "
        "Швидко вчуся новому, зараз опановую веб-розробку на Flask."
    ),
    "education": [
        {
            "degree": "Бакалавр, Інженерія програмного забезпечення",
            "place": "Прикарпатський національний університет імені Василя Стефаника",
            "period": "09/2024 — тепер",
            "city": "Івано-Франківськ",
        },
    ],
    "certificates": [
        "Основи Web UI розробки (2023)",
        "C Essentials 1",
        "C Essentials 2",
        "C++ Essentials 1",
        "C++ Essentials 2",
    ],
    "projects": [
        {
            "title": "Telegram-бот для збору та обробки даних у реальному часі",
            "period": "06/2024 — тепер",
            "description": "Розробив автоматизовані системи збору, форматування та надсилання даних.",
            "stack": "Lua",
        },
        {
            "title": "Скрипт автоматичної реєстрації",
            "period": None,
            "description": "Веб-скрапінг, антидетект-платформи та API сторонніх сервісів.",
            "stack": "Python",
        },
        {
            "title": "All-in-one game helper suite",
            "period": None,
            "description": "Багатофункціональний скрипт, що об'єднує багато дрібних, з GUI на Moon ImGui.",
            "stack": "Lua",
        },
    ],
    "skills": [
        "Швидко навчаюся",
        "Відповідальний",
        "Адаптивний і комунікабельний",
    ],
    "technologies": [
        "C/C++", "Python", "Java", "Lua", "HTML/CSS/JS", "MS SQL", "Flask", "Git",
    ],
    "languages": [
        {"name": "Англійська", "level": "Upper-intermediate"},
        {"name": "Українська", "level": "Рідна"},
    ],
}

SECTIONS = [
    ("about", "Про себе"),
    ("education", "Освіта"),
    ("projects", "Проєкти"),
    ("skills", "Навички"),
    ("technologies", "Технології"),
]


@app.route("/")
@app.route("/resume")
def resume():
    return render_template(
        "resume.html",
        title="Резюме",
        profile=PROFILE,
        resume=RESUME,
        sections=SECTIONS,
    )


@app.route("/contacts", methods=["GET", "POST"])
def contacts():
    sent_name = None
    if request.method == "POST":
        sent_name = request.form.get("name", "").strip() or "друже"
    return render_template(
        "contacts.html",
        title="Контакти",
        profile=PROFILE,
        sent_name=sent_name,
    )


if __name__ == "__main__":
    app.run(debug=True)
