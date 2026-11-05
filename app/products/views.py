from flask import flash, redirect, render_template, request, url_for

from . import products_bp
from .forms import ProductForm
from .images import save_image
from .storage import CATEGORIES, add_product, get_all_products, get_product


@products_bp.context_processor
def inject_categories():
    return {"categories": dict(CATEGORIES)}


@products_bp.app_errorhandler(413)
def file_too_large(error):
    flash("Файл завеликий: максимальний розмір запиту 5 МБ.", "danger")
    return redirect(request.url)


@products_bp.route("/")
@products_bp.route("")
def products_list():
    return render_template("products/products.html", products=get_all_products())


@products_bp.route("/<int:id>")
def detail_product(id):
    product = get_product(id)
    if product is None:
        return render_template("products/not_found.html", id=id), 404
    return render_template("products/detail_product.html", product=product)


@products_bp.route("/add", methods=["GET", "POST"])
def add_product_view():
    form = ProductForm()

    if form.validate_on_submit():
        image = save_image(form.image.data) if form.image.data else None
        product_id = add_product({
            "name": form.name.data.strip(),
            "content": form.content.data.strip(),
            "price": float(form.price.data),
            "category": form.category.data,
            "quantity": form.quantity.data,
            "image": image,
        })
        flash(f"Товар «{form.name.data.strip()}» додано.", "success")
        return redirect(url_for("products.detail_product", id=product_id))

    if request.method == "POST":
        flash("Товар не збережено: виправте помилки у формі.", "danger")

    return render_template("products/product_form.html", form=form, title="Новий товар")
