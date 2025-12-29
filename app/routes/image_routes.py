from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.image_service import (
    save_image,
    rotate_image,
    crop_image
)
from app.services.image_enhancement_service import (
    adjust_brightness,
    adjust_contrast,
    sharpen_image,
    smooth_image,
    generate_histogram
)

from app.services.compression_service import compress_jpeg

import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# =========================
# Editor Page
# =========================
@router.get("/editor", response_class=HTMLResponse)
def editor_page(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "image_url": None,
            "edited_url": None
        }
    )


# =========================
# Upload Image
# =========================
@router.post("/upload", response_class=HTMLResponse)
async def upload_image(
    request: Request,
    file: UploadFile = File(...)
):
    image_path = await save_image(file)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "image_url": image_path,   # Before
            "edited_url": None         # After → فارغة قبل أي تعديل
        }
    )


# =========================
# Rotate Image
# =========================
@router.post("/rotate", response_class=HTMLResponse)
def rotate(
    request: Request,
    image_url: str = Form(...),
    angle: int = Form(...)
):
    new_image = rotate_image(image_url, angle)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "image_url": image_url,   # قبل التدوير
            "edited_url": new_image   # بعد التدوير
        }
    )


# =========================
# Crop Image
# =========================
@router.post("/crop", response_class=HTMLResponse)
def crop(
    request: Request,
    image_url: str = Form(...),
    x: int = Form(...),
    y: int = Form(...),
    width: int = Form(...),
    height: int = Form(...)
):
    new_image = crop_image(image_url, x, y, width, height)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "image_url": image_url,   # الصورة الأصلية
            "edited_url": new_image   # الصورة بعد القص
        }
    )


# =========================
# JPEG Compression
# =========================
@router.post("/compress", response_class=HTMLResponse)
def compress_image(
    request: Request,س
    image_url: str = Form(...),
    quality: int = Form(...)
):
    input_path = "app/static" + image_url
    filename = os.path.basename(input_path)

    output_dir = "app/static/uploads/compressed"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(
        output_dir,
        f"compressed_{filename}"
    )

    stats = compress_jpeg(
        input_path=input_path,
        output_path=output_path,
        quality=quality
    )

    compressed_url = "/uploads/compressed/" + f"compressed_{filename}"

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "image_url": image_url,        # Before
            "edited_url": compressed_url,  # After
            "stats": stats
        }
    )



# =========================
# Brightness
# =========================
@router.post("/brightness", response_class=HTMLResponse)
def brightness(
    request: Request,
    image_url: str = Form(...),
    factor: float = Form(...)
):
    new_image = adjust_brightness(image_url, factor)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "image_url": image_url,   # Before
            "edited_url": new_image   # After
        }
    )


# =========================
# Contrast
# =========================
@router.post("/contrast", response_class=HTMLResponse)
def contrast(
    request: Request,
    image_url: str = Form(...),
    factor: float = Form(...)
):
    new_image = adjust_contrast(image_url, factor)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "image_url": image_url,
            "edited_url": new_image
        }
    )


# =========================
# Sharpen
# =========================
@router.post("/sharpen", response_class=HTMLResponse)
def sharpen(
    request: Request,
    image_url: str = Form(...)
):
    new_image = sharpen_image(image_url)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "image_url": image_url,
            "edited_url": new_image
        }
    )


# =========================
# Smooth
# =========================
@router.post("/smooth", response_class=HTMLResponse)
def smooth(
    request: Request,
    image_url: str = Form(...)
):
    new_image = smooth_image(image_url)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "image_url": image_url,
            "edited_url": new_image
        }
    )


# =========================
# Histogram
# =========================
@router.post("/histogram", response_class=HTMLResponse)
def histogram(
    request: Request,
    image_url: str = Form(...)
):
    histogram_image = generate_histogram(image_url)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "image_url": image_url,
            "edited_url": None,
            "histogram_url": histogram_image
        }
    )
