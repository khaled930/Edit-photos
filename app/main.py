from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn

# Routes
from app.routes import image_routes, auth_routes

# Database
from app.database.db import engine, SessionLocal
from app.database.models import Base
from app.database import crud

from passlib.hash import bcrypt

# =========================
# App
# =========================
app = FastAPI(title="Image Editing Platform")

# =========================
# Static files
# =========================
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="app/static/uploads"), name="uploads")

# =========================
# Templates
# =========================
templates = Jinja2Templates(directory="app/templates")

# =========================
# Database
# =========================
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# Create default admin (bcrypt)
# =========================
def create_default_admin():
    db = SessionLocal()
    try:
        if not crud.get_user_by_username(db, "admin"):
            hashed = bcrypt.hash("admin")
            crud.create_user(db, "admin", hashed)
    finally:
        db.close()

create_default_admin()

# =========================
# Auth Middleware
# =========================
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    open_paths = ["/login", "/register"]
    static_paths = ["/static", "/uploads"]

    path = request.url.path

    if (
        path in open_paths
        or any(path.startswith(p) for p in static_paths)
    ):
        return await call_next(request)

    user = request.cookies.get("user")
    if not user:
        return RedirectResponse("/login")

    return await call_next(request)


# =========================
# Routers
# =========================
app.include_router(auth_routes.router)
app.include_router(image_routes.router)

# =========================
# Root
# =========================
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    user = request.cookies.get("user")
    if user:
        return RedirectResponse("/editor")
    return RedirectResponse("/login")

# =========================
# Editor
# =========================
@app.get("/editor", response_class=HTMLResponse)
def editor_page(request: Request, db: Session = Depends(get_db)):
    username = request.cookies.get("user")
    if not username:
        return RedirectResponse("/login")

    user = crud.get_user_by_username(db, username)
    if not user:
        return RedirectResponse("/login")

    images = crud.get_user_images(db, user.id)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": username,
            "images": images,
            "image_url": "",
            "edited_url": ""
        }
    )

# =========================
# Admin users page
# =========================
@app.get("/users", response_class=HTMLResponse)
def users_page(request: Request, db: Session = Depends(get_db)):
    if request.cookies.get("user") != "admin":
        return RedirectResponse("/login")

    users = crud.get_all_users(db)
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": users}
    )

@app.get("/force-logout")
def force_logout():
    response = RedirectResponse("/login")
    response.delete_cookie("user")
    return response


# =========================
# Run
# =========================
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
