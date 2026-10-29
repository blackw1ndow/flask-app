import re
from functools import wraps

from flask import flash, make_response, redirect, render_template, request, session, url_for

from . import users_bp

# Заглушка замість бази даних: логін -> пароль
USERS = {
    "admin": "admin123",
    "user1": "qwerty",
}

THEMES = ("light", "dark")
THEME_COOKIE = "theme"
THEME_MAX_AGE = 60 * 60 * 24 * 365  # рік
COOKIE_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+$")
PROTECTED_COOKIES = {"session"}


def login_required(view):
    """Пускає далі лише користувача, який є в сесії."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            flash("Спершу увійдіть у систему.", "danger")
            return redirect(url_for("users.login"))
        return view(*args, **kwargs)
    return wrapper


@users_bp.route("/hi/<string:name>")  # /users/hi/ivan?age=45
def greetings(name):
    name = name.upper()
    age = request.args.get("age", None, int)

    return render_template("users/hi.html", name=name, age=age)


@users_bp.route("/admin")
def admin():
    to_url = url_for("users.greetings", name="administrator", age=45, _external=True)
    print(to_url)
    return redirect(to_url)


# ---------- Вхід, профіль, вихід ----------

@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        flash("Ви вже увійшли в систему.", "info")
        return redirect(url_for("users.profile"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if USERS.get(username) == password and password:
            session["username"] = username
            flash(f"Вхід успішний. Вітаємо, {username}!", "success")
            return redirect(url_for("users.profile"))

        flash("Неправильний логін або пароль. Спробуйте ще раз.", "danger")
        return redirect(url_for("users.login"))

    return render_template("users/login.html", title="Вхід")


@users_bp.route("/profile")
@login_required
def profile():
    cookies = sorted(request.cookies.items())
    return render_template(
        "users/profile.html",
        title="Профіль",
        username=session["username"],
        cookies=cookies,
        theme=current_theme(),
    )


@users_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    flash("Ви вийшли з системи.", "info")
    return redirect(url_for("users.login"))


# ---------- Кукі ----------

@users_bp.route("/cookies/add", methods=["POST"])
@login_required
def add_cookie():
    key = request.form.get("key", "").strip()
    value = request.form.get("value", "").strip()
    max_age_raw = request.form.get("max_age", "").strip()

    if not COOKIE_KEY_RE.match(key):
        flash("Ключ кукі може містити лише латинські літери, цифри, «-» і «_».", "danger")
        return redirect(url_for("users.profile"))
    if key in PROTECTED_COOKIES:
        flash(f"Кукі «{key}» змінювати не можна.", "danger")
        return redirect(url_for("users.profile"))

    max_age = None
    if max_age_raw:
        if not max_age_raw.isdigit() or int(max_age_raw) <= 0:
            flash("Термін дії має бути додатним цілим числом секунд.", "danger")
            return redirect(url_for("users.profile"))
        max_age = int(max_age_raw)

    response = make_response(redirect(url_for("users.profile")))
    response.set_cookie(key, value, max_age=max_age)
    term = f"на {max_age} с" if max_age else "до закриття браузера"
    flash(f"Кукі «{key}» додано ({term}).", "success")
    return response


@users_bp.route("/cookies/delete", methods=["POST"])
@login_required
def delete_cookie():
    key = request.form.get("key", "").strip()

    if key in PROTECTED_COOKIES:
        flash(f"Кукі «{key}» видаляти не можна, інакше ви вийдете з системи.", "danger")
        return redirect(url_for("users.profile"))
    if key not in request.cookies:
        flash(f"Кукі з ключем «{key}» не знайдено.", "warning")
        return redirect(url_for("users.profile"))

    response = make_response(redirect(url_for("users.profile")))
    response.delete_cookie(key)
    flash(f"Кукі «{key}» видалено.", "success")
    return response


@users_bp.route("/cookies/clear", methods=["POST"])
@login_required
def clear_cookies():
    keys = [key for key in request.cookies if key not in PROTECTED_COOKIES]
    response = make_response(redirect(url_for("users.profile")))
    for key in keys:
        response.delete_cookie(key)

    if keys:
        flash(f"Видалено всі кукі ({len(keys)} шт.), крім кукі сесії.", "success")
    else:
        flash("Немає кукі для видалення.", "info")
    return response


# ---------- Кольорова схема ----------

def current_theme():
    theme = request.cookies.get(THEME_COOKIE)
    return theme if theme in THEMES else "light"


@users_bp.route("/theme/<string:scheme>")
@login_required
def set_theme(scheme):
    if scheme not in THEMES:
        flash("Невідома кольорова схема.", "danger")
        return redirect(url_for("users.profile"))

    response = make_response(redirect(url_for("users.profile")))
    response.set_cookie(THEME_COOKIE, scheme, max_age=THEME_MAX_AGE)
    label = "темну" if scheme == "dark" else "світлу"
    flash(f"Увімкнено {label} тему.", "success")
    return response
