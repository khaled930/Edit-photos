import os
from uuid import uuid4
from PIL import Image, ImageEnhance, ImageFilter
import matplotlib.pyplot as plt

UPLOAD_DIR = "app/static/uploads"

# =========================
# Brightness
# =========================
def adjust_brightness(image_url: str, factor: float):
    input_path = "app/static" + image_url
    image = Image.open(input_path)

    enhancer = ImageEnhance.Brightness(image)
    enhanced = enhancer.enhance(factor)

    filename = f"{uuid4()}.png"
    output_path = os.path.join(UPLOAD_DIR, filename)
    enhanced.save(output_path)

    return f"/uploads/{filename}"


# =========================
# Contrast
# =========================
def adjust_contrast(image_url: str, factor: float):
    input_path = "app/static" + image_url
    image = Image.open(input_path)

    enhancer = ImageEnhance.Contrast(image)
    enhanced = enhancer.enhance(factor)

    filename = f"{uuid4()}.png"
    output_path = os.path.join(UPLOAD_DIR, filename)
    enhanced.save(output_path)

    return f"/uploads/{filename}"


# =========================
# Sharpen Image
# =========================
def sharpen_image(image_url: str):
    input_path = "app/static" + image_url
    image = Image.open(input_path)

    sharpened = image.filter(ImageFilter.SHARPEN)

    filename = f"{uuid4()}.png"
    output_path = os.path.join(UPLOAD_DIR, filename)
    sharpened.save(output_path)

    return f"/uploads/{filename}"


# =========================
# Smooth Image
# =========================
def smooth_image(image_url: str):
    input_path = "app/static" + image_url
    image = Image.open(input_path)

    smoothed = image.filter(ImageFilter.SMOOTH)

    filename = f"{uuid4()}.png"
    output_path = os.path.join(UPLOAD_DIR, filename)
    smoothed.save(output_path)

    return f"/uploads/{filename}"


# =========================
# Histogram (Optional)
# =========================
def generate_histogram(image_url: str):
    input_path = "app/static" + image_url
    image = Image.open(input_path).convert("RGB")

    r, g, b = image.split()

    plt.figure()
    plt.hist(list(r.getdata()), bins=256, color="red", alpha=0.5)
    plt.hist(list(g.getdata()), bins=256, color="green", alpha=0.5)
    plt.hist(list(b.getdata()), bins=256, color="blue", alpha=0.5)

    filename = f"{uuid4()}.png"
    output_path = os.path.join(UPLOAD_DIR, filename)

    plt.savefig(output_path)
    plt.close()

    return f"/uploads/{filename}"
