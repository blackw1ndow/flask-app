from flask import render_template, request

from . import app

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


@app.context_processor
def inject_profile():
    return {"profile": PROFILE}


@app.route("/")
@app.route("/resume")
def resume():
    return render_template(
        "resume.html",
        title="Резюме",
        resume=RESUME,
        sections=SECTIONS,
    )


def describe_agent(agent_string):
    """Грубо визначає браузер і ОС за рядком User-Agent."""
    browsers = [("Edg", "Edge"), ("OPR", "Opera"), ("Chrome", "Chrome"),
                ("Firefox", "Firefox"), ("Safari", "Safari")]
    systems = [("Android", "Android"), ("iPhone", "iOS"), ("Windows", "Windows"),
               ("Mac OS", "macOS"), ("Linux", "Linux")]
    browser = next((name for key, name in browsers if key in agent_string), "невідомо")
    system = next((name for key, name in systems if key in agent_string), "невідомо")
    return browser, system


@app.route("/homepage")
def home():
    """View for the Home page of your website."""
    agent = request.user_agent
    browser, system = describe_agent(agent.string)
    return render_template(
        "homepage.html",
        title="Головна",
        agent=agent,
        browser=browser,
        system=system,
    )


@app.route("/contacts", methods=["GET", "POST"])
def contacts():
    sent_name = None
    if request.method == "POST":
        sent_name = request.form.get("name", "").strip() or "друже"
    return render_template("contacts.html", title="Контакти", sent_name=sent_name)
