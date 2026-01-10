from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
import os

# Routes
from app.routes import image_routes, auth_routes

# Database
from app.database.db import engine, SessionLocal
from app.database.models import Base
from app.database import crud

from passlib.context import CryptContext

# =========================
# Password hashing
# =========================
# Initialize password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# =========================
# Create default admin (bcrypt)
# =========================
def create_default_admin():
    """Create default admin user if it doesn't exist"""
    db = SessionLocal()
    try:
        if not crud.get_user_by_username(db, "admin"):
            # Use CryptContext to hash password
            hashed = pwd_context.hash("admin")
            crud.create_user(db, "admin", hashed)
            print("Default admin user created successfully")
    except Exception as e:
        # Log error but don't crash the app
        print(f"Error creating default admin: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

# =========================
# Lifespan events
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_default_admin()
    yield
    # Shutdown (if needed)

# =========================
# App
# =========================
app = FastAPI(title="Image Editing Platform", lifespan=lifespan)

# =========================
# Static files
# =========================
# Mount static files - must be before routers
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Mount uploads directory - this will serve files from app/static/uploads and subdirectories
# Note: StaticFiles automatically handles subdirectories
app.mount("/uploads", StaticFiles(directory="app/static/uploads", html=False), name="uploads")

# =========================
# Database
# =========================
# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Error creating database tables: {e}")
    import traceback
    traceback.print_exc()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
# Include routers after static files mounting
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

    # Return static HTML file
    html_path = os.path.join("app", "static", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return HTMLResponse("Editor page not found", status_code=404)

# =========================
# Admin users page
# =========================
@app.get("/users", response_class=HTMLResponse)
def users_page(request: Request, db: Session = Depends(get_db)):
    if request.cookies.get("user") != "admin":
        return RedirectResponse("/login")

    # Return static HTML file
    html_path = os.path.join("app", "static", "users.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return HTMLResponse("Users page not found", status_code=404)

@app.get("/force-logout")
def force_logout():
    response = RedirectResponse("/login")
    response.delete_cookie("user")
    return response

# =========================
# API Endpoints
# =========================
@app.get("/api/user")
def get_current_user(request: Request, db: Session = Depends(get_db)):
    username = request.cookies.get("user")
    if not username:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    
    user = crud.get_user_by_username(db, username)
    if not user:
        return JSONResponse({"error": "User not found"}, status_code=404)
    
    return JSONResponse({
        "username": user.username,
        "id": user.id
    })

@app.get("/api/images")
def get_user_images(request: Request, db: Session = Depends(get_db)):
    username = request.cookies.get("user")
    if not username:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    
    user = crud.get_user_by_username(db, username)
    if not user:
        return JSONResponse({"error": "User not found"}, status_code=404)
    
    images = crud.get_user_images(db, user.id)
    images_data = [
        {
            "id": img.id,
            "filename": img.filename,
            "image_url": img.image_url,
            "created_at": img.created_at.isoformat() if img.created_at else None
        }
        for img in images
    ]
    
    return JSONResponse({"images": images_data})

@app.get("/api/users")
def get_all_users(request: Request, db: Session = Depends(get_db)):
    username = request.cookies.get("user")
    if not username or username != "admin":
        return JSONResponse({"error": "Unauthorized - Admin only"}, status_code=403)
    
    users = crud.get_all_users(db)
    users_data = [
        {
            "id": user.id,
            "username": user.username
        }
        for user in users
    ]
    
    return JSONResponse({"users": users_data})


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
