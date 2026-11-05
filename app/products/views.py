from flask import render_template

from . import products_bp
from .storage import CATEGORIES, get_all_products, get_product


@products_bp.context_processor
def inject_categories():
    return {"categories": dict(CATEGORIES)}


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