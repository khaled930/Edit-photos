from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.image_service import save_image

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/editor", response_class=HTMLResponse)
def editor_page(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "image_url": None}
    )

@router.post("/upload", response_class=HTMLResponse)
async def upload_image(request: Request, file: UploadFile = File(...)):
    image_path = await save_image(file)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "image_url": image_path
        }
    )
