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


def delete_image(relative_path):
    """Видаляє файл зображення, якщо він є. Шлях з бази: uploads/<ім'я>."""
    if not relative_path:
        return
    filename = os.path.basename(relative_path)
    path = os.path.join(current_app.config["PRODUCT_UPLOAD_FOLDER"], filename)
    if os.path.isfile(path):
        os.remove(path)
