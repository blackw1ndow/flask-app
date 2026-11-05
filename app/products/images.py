import os
import uuid

from flask import current_app


def save_image(file_storage):
    """Зберігає файл під випадковим UUID-іменем і повертає відносний шлях для бази."""
    extension = file_storage.filename.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{extension}"
    folder = current_app.config["PRODUCT_UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    file_storage.save(os.path.join(folder, filename))
    return f"uploads/{filename}"
