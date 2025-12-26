import os
from uuid import uuid4

UPLOAD_DIR = "app/static/uploads"

async def save_image(file):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    extension = file.filename.split(".")[-1]
    filename = f"{uuid4()}.{extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return f"/uploads/{filename}"
