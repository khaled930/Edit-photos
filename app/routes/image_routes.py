from fastapi import APIRouter, Request, UploadFile, File, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
import os
from pydantic import BaseModel

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
@router.post("/upload")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = require_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    image_url = await save_image(file)
    crud.create_image(db, file.filename, image_url, user.id)

    return JSONResponse({
        "image_url": image_url,
        "edited_url": "",
        "message": "Image uploaded successfully"
    })

# =========================
# Rotate
# =========================
@router.post("/rotate")
def rotate(
    request: Request,
    image_url: str = Form(...),
    angle: int = Form(...),
    db: Session = Depends(get_db)
):
    user = require_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    new_image = rotate_image(image_url, angle)
    return JSONResponse({"edited_url": new_image, "image_url": image_url})

# =========================
# Crop
# =========================
@router.post("/crop")
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
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    new_image = crop_image(image_url, x, y, width, height)
    return JSONResponse({"edited_url": new_image, "image_url": image_url})

# =========================
# Compress
# =========================
@router.post("/compress")
def compress_image(
    request: Request,
    image_url: str = Form(...),
    quality: int = Form(...),
    db: Session = Depends(get_db)
):
    user = require_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    input_path = "app/static" + image_url
    
    # Check if input file exists
    if not os.path.exists(input_path):
        return JSONResponse({"error": f"Image not found: {input_path}"}, status_code=404)
    
    filename = os.path.basename(input_path)

    output_dir = "app/static/uploads/compressed"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"compressed_{filename}")

    try:
        stats = compress_jpeg(input_path, output_path, quality)
        # Verify file was created
        if not os.path.exists(output_path):
            return JSONResponse({"error": "Failed to create compressed file"}, status_code=500)
        
        compressed_url = "/uploads/compressed/compressed_" + filename
    except Exception as e:
        return JSONResponse({"error": f"Compression failed: {str(e)}"}, status_code=500)

    return JSONResponse({
        "edited_url": compressed_url,
        "image_url": image_url,
        "stats": stats
    })

# =========================
# Enhancements
# =========================
@router.post("/brightness")
def brightness(request: Request, image_url: str = Form(...), factor: float = Form(...), db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    new_image = adjust_brightness(image_url, factor)
    return JSONResponse({"edited_url": new_image, "image_url": image_url})

@router.post("/contrast")
def contrast(request: Request, image_url: str = Form(...), factor: float = Form(...), db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    new_image = adjust_contrast(image_url, factor)
    return JSONResponse({"edited_url": new_image, "image_url": image_url})

@router.post("/sharpen")
def sharpen(request: Request, image_url: str = Form(...), db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    new_image = sharpen_image(image_url)
    return JSONResponse({"edited_url": new_image, "image_url": image_url})

@router.post("/smooth")
def smooth(request: Request, image_url: str = Form(...), db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    new_image = smooth_image(image_url)
    return JSONResponse({"edited_url": new_image, "image_url": image_url})

@router.post("/histogram")
def histogram(request: Request, image_url: str = Form(...), db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    histogram_image = generate_histogram(image_url)
    return JSONResponse({"histogram_url": histogram_image, "image_url": image_url})

# =========================
# API Endpoints (JSON) for AJAX
# =========================

class EditRequest(BaseModel):
    image_url: str
    factor: float = None
    angle: int = None
    quality: int = None
    x: int = None
    y: int = None
    width: int = None
    height: int = None

@router.post("/api/brightness")
async def api_brightness(request: Request, data: EditRequest, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    if data.factor is None:
        return JSONResponse({"error": "factor is required"}, status_code=400)
    
    new_image = adjust_brightness(data.image_url, data.factor)
    return JSONResponse({"edited_url": new_image, "image_url": data.image_url})

@router.post("/api/contrast")
async def api_contrast(request: Request, data: EditRequest, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    if data.factor is None:
        return JSONResponse({"error": "factor is required"}, status_code=400)
    
    new_image = adjust_contrast(data.image_url, data.factor)
    return JSONResponse({"edited_url": new_image, "image_url": data.image_url})

@router.post("/api/sharpen")
async def api_sharpen(request: Request, data: EditRequest, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    new_image = sharpen_image(data.image_url)
    return JSONResponse({"edited_url": new_image, "image_url": data.image_url})

@router.post("/api/smooth")
async def api_smooth(request: Request, data: EditRequest, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    new_image = smooth_image(data.image_url)
    return JSONResponse({"edited_url": new_image, "image_url": data.image_url})

@router.post("/api/rotate")
async def api_rotate(request: Request, data: EditRequest, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    if data.angle is None:
        return JSONResponse({"error": "angle is required"}, status_code=400)
    
    new_image = rotate_image(data.image_url, data.angle)
    return JSONResponse({"edited_url": new_image, "image_url": data.image_url})

@router.post("/api/crop")
async def api_crop(request: Request, data: EditRequest, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    if data.x is None or data.y is None or data.width is None or data.height is None:
        return JSONResponse({"error": "x, y, width, height are required"}, status_code=400)
    
    new_image = crop_image(data.image_url, data.x, data.y, data.width, data.height)
    return JSONResponse({"edited_url": new_image, "image_url": data.image_url})

@router.post("/api/compress")
async def api_compress(request: Request, data: EditRequest, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    if data.quality is None:
        return JSONResponse({"error": "quality is required"}, status_code=400)
    
    input_path = "app/static" + data.image_url
    
    # Check if input file exists
    if not os.path.exists(input_path):
        return JSONResponse({"error": f"Image not found: {input_path}"}, status_code=404)
    
    filename = os.path.basename(input_path)
    
    output_dir = "app/static/uploads/compressed"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"compressed_{filename}")
    
    try:
        stats = compress_jpeg(input_path, output_path, data.quality)
        # Verify file was created
        if not os.path.exists(output_path):
            return JSONResponse({"error": "Failed to create compressed file"}, status_code=500)
        
        compressed_url = "/uploads/compressed/compressed_" + filename
    except Exception as e:
        return JSONResponse({"error": f"Compression failed: {str(e)}"}, status_code=500)
    
    return JSONResponse({
        "edited_url": compressed_url,
        "image_url": data.image_url,
        "stats": stats
    })

@router.post("/api/histogram")
async def api_histogram(request: Request, data: EditRequest, db: Session = Depends(get_db)):
    user = require_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    histogram_image = generate_histogram(data.image_url)
    return JSONResponse({"histogram_url": histogram_image, "image_url": data.image_url})
