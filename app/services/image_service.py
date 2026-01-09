import os
from uuid import uuid4
from PIL import Image

UPLOAD_DIR = "app/static/uploads"

async def save_image(file):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    extension = file.filename.split(".")[-1]
    filename = f"{uuid4()}.{extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return f"/uploads/{filename}"



UPLOAD_DIR = "app/static/uploads"
def rotate_image(image_path: str, angle: int):
    full_path = f"app/static{image_path.replace('/uploads', '/uploads')}"
    
    image = Image.open(full_path)
    rotated = image.rotate(-angle, expand=True)

    filename = f"{uuid4()}.png"
    output_path = os.path.join(UPLOAD_DIR, filename)

    rotated.save(output_path)

    return f"/uploads/{filename}"


def crop_image(image_url: str, x: int, y: int, width: int, height: int):
    input_path = "app/static" + image_url
    image = Image.open(input_path)

    cropped = image.crop((x, y, x + width, y + height))

    filename = f"{uuid4()}.png"
    output_path = os.path.join(UPLOAD_DIR, filename)

    cropped.save(output_path)

    return f"/uploads/{filename}"

