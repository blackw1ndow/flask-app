from flask import flash, redirect, render_template, request, session, url_for

from app import db

from . import post_bp
from .forms import DeletePostForm, PostForm
from .models import CATEGORIES, Post


@post_bp.context_processor
def inject_categories():
    return {"post_categories": dict(CATEGORIES)}


@post_bp.route("/")
@post_bp.route("")
def list_posts():
    """Усі видимі (активні) пости, від найновіших до найстаріших."""
    stmt = db.select(Post).where(Post.is_active.is_(True)).order_by(Post.posted.desc())
    posts = db.session.scalars(stmt).all()
    hidden = db.session.scalar(
        db.select(db.func.count()).select_from(Post).where(Post.is_active.is_(False))
    )
    return render_template("posts/posts.html", title="Пости", posts=posts, hidden=hidden)


@post_bp.route("/<int:id>")
def detail_post(id):
    post = db.get_or_404(Post, id)
    return render_template("posts/detail_post.html", title=post.title, post=post)


@post_bp.route("/create", methods=["GET", "POST"])
def create_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(
            title=form.title.data.strip(),
            content=form.content.data.strip(),
            is_active=form.is_active.data,
            posted=form.publish_date.data,
            category=form.category.data,
            author=session.get("username", "Anonymous"),  # автор — користувач із сесії
        )
        db.session.add(post)
        db.session.commit()
        flash(f"Пост «{post.title}» додано.", "success")
        return redirect(url_for("posts.detail_post", id=post.id))

    if request.method == "POST":
        flash("Пост не збережено: виправте помилки у формі.", "danger")

    return render_template("posts/add_post.html", title="Новий пост", form=form)


@post_bp.route("/<int:id>/update", methods=["GET", "POST"])
def update_post(id):
    post = db.get_or_404(Post, id)
    form = PostForm(obj=post)  # заповнює title, content, is_active, category з об'єкта post

    if request.method == "GET":
        # Атрибут моделі називається posted, а поле форми — publish_date, тому вручну.
        # Лише для GET: при POST тут уже дата, яку ввів користувач.
        form.publish_date.data = post.posted

    if form.validate_on_submit():
        form.populate_obj(post)              # копіює поля форми в однойменні атрибути post
        post.posted = form.publish_date.data
        db.session.commit()
        flash(f"Пост «{post.title}» оновлено.", "success")
        return redirect(url_for("posts.detail_post", id=post.id))

    if request.method == "POST":
        flash("Зміни не збережено: виправте помилки у формі.", "danger")

    return render_template("posts/add_post.html", title="Редагування поста", form=form, post=post)


@post_bp.route("/<int:id>/delete", methods=["GET", "POST"])
def delete_post(id):
    post = db.get_or_404(Post, id)
    form = DeletePostForm()

    if form.validate_on_submit():            # лише POST з правильним CSRF-токеном
        db.session.delete(post)
        db.session.commit()
        flash(f"Пост «{post.title}» видалено.", "success")
        return redirect(url_for("posts.list_posts"))

    return render_template("posts/delete_confirm.html", title="Видалення поста", post=post, form=form)
