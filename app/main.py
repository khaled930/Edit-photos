from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.routes.image_routes import router as image_router
import os
import uvicorn
from pathlib import Path

app = FastAPI(title="Image Editing Platform")

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory="app/static/uploads"), name="uploads")
app.include_router(image_router)


@app.get("/")
def read_root():
    return RedirectResponse(url="/editor")



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
