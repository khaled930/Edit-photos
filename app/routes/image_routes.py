from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.image_service import crop_image
from app.services.image_service import save_image, rotate_image

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/editor", response_class=HTMLResponse)
def editor_page(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "image_url": None}
    )


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
            "image_url": image_path
        }
    )


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
            "image_url": new_image
        }
    )
    
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
            "image_url": new_image
        }
    )
   
