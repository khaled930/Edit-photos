from fastapi import APIRouter, Request, UploadFile, File, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from app.services.image_service import save_image, rotate_image, crop_image
from app.services.image_enhancement_service import (
    adjust_brightness,
    adjust_contrast,
    sharpen_image,
    smooth_image,
    generate_histogram
)
from app.services.compression_service import compress_jpeg
from app.database.db import SessionLocal
from app.database import crud

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# =========================
# DB dependency
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# Helper: require login
# =========================
def require_user(request: Request, db: Session):
    username = request.cookies.get("user")
    if not username:
        return None
    return crud.get_user_by_username(db, username)

# =========================
# Upload Image
# =========================
@router.post("/upload", response_class=HTMLResponse)
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = require_user(request, db)
    if not user:
        return RedirectResponse("/login")

    image_url = await save_image(file)
    crud.create_image(db, file.filename, image_url, user.id)

    images = crud.get_user_images(db, user.id)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user.username,
            "images": images,
            "image_url": image_url,
            "edited_url": ""
        }
    )

# =========================
# Rotate
# =========================
@router.post("/rotate", response_class=HTMLResponse)
def rotate(
    request: Request,
    image_url: str = Form(...),
    angle: int = Form(...),
    db: Session = Depends(get_db)
):
    user = require_user(request, db)
    if not user:
        return RedirectResponse("/login")

    new_image = rotate_image(image_url, angle)
    images = crud.get_user_images(db, user.id)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user.username,
            "images": images,
            "image_url": image_url,
            "edited_url": new_image
        }
    )

# =========================
# Crop
# =========================
@router.post("/crop", response_class=HTMLResponse)
def crop(
    request: Request,
    image_url: str = Form(...),
    x: int = Form(...),
    y: int = Form(...),
    width: int = Form(...),
    height: int = Form(...),
    db: Session = Depends(get_db)
):
    user = require_user(request, db)
    if not user:
        return RedirectResponse("/login")

    new_image = crop_image(image_url, x, y, width, height)
    images = crud.get_user_images(db, user.id)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user.username,
            "images": images,
            "image_url": image_url,
            "edited_url": new_image
        }
    )

# =========================
# Compress
# =========================
@router.post("/compress", response_class=HTMLResponse)
def compress_image(
    request: Request,
    image_url: str = Form(...),
    quality: int = Form(...),
    db: Session = Depends(get_db)
):
    user = require_user(request, db)
    if not user:
        return RedirectResponse("/login")

    input_path = "app/static" + image_url
    filename = os.path.basename(input_path)

    output_dir = "app/static/uploads/compressed"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"compressed_{filename}")

    stats = compress_jpeg(input_path, output_path, quality)
    compressed_url = "/uploads/compressed/compressed_" + filename

    images = crud.get_user_images(db, user.id)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user.username,
            "images": images,
            "image_url": image_url,
            "edited_url": compressed_url,
            "stats": stats
        }
    )

# =========================
# Enhancements
# =========================
@router.post("/brightness")
def brightness(request: Request, image_url: str = Form(...), factor: float = Form(...), db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return RedirectResponse("/login")
    new_image = adjust_brightness(image_url, factor)
    images = crud.get_user_images(db, user.id)
    return templates.TemplateResponse("index.html", {"request": request, "user": user.username, "images": images, "image_url": image_url, "edited_url": new_image})

@router.post("/contrast")
def contrast(request: Request, image_url: str = Form(...), factor: float = Form(...), db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return RedirectResponse("/login")
    new_image = adjust_contrast(image_url, factor)
    images = crud.get_user_images(db, user.id)
    return templates.TemplateResponse("index.html", {"request": request, "user": user.username, "images": images, "image_url": image_url, "edited_url": new_image})

@router.post("/sharpen")
def sharpen(request: Request, image_url: str = Form(...), db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return RedirectResponse("/login")
    new_image = sharpen_image(image_url)
    images = crud.get_user_images(db, user.id)
    return templates.TemplateResponse("index.html", {"request": request, "user": user.username, "images": images, "image_url": image_url, "edited_url": new_image})

@router.post("/smooth")
def smooth(request: Request, image_url: str = Form(...), db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return RedirectResponse("/login")
    new_image = smooth_image(image_url)
    images = crud.get_user_images(db, user.id)
    return templates.TemplateResponse("index.html", {"request": request, "user": user.username, "images": images, "image_url": image_url, "edited_url": new_image})

@router.post("/histogram")
def histogram(request: Request, image_url: str = Form(...), db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return RedirectResponse("/login")
    histogram_image = generate_histogram(image_url)
    images = crud.get_user_images(db, user.id)
    return templates.TemplateResponse("index.html", {"request": request, "user": user.username, "images": images, "image_url": image_url, "edited_url": "", "histogram_url": histogram_image})
