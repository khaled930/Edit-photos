from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.routes.image_routes import router as image_router

app = FastAPI(title="Image Editing Platform")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="app/static/uploads"), name="uploads")

app.include_router(image_router)


@app.get("/")
def read_root():
    return RedirectResponse(url="/editor")
