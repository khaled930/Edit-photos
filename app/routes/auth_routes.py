from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.database import crud
from fastapi.templating import Jinja2Templates
from passlib.hash import bcrypt

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# =========================
# DB Dependency
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# تسجيل الدخول
# =========================
@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None}
    )

@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, username)

    if not user or not bcrypt.verify(password, user.password):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "اسم المستخدم أو كلمة المرور غير صحيحة"
            }
        )

    response = RedirectResponse(url="/editor", status_code=302)

    # 🔴 مهم جدًا
    response.set_cookie(
        key="user",
        value=username,
        httponly=True,
        path="/"
    )

    return response

# =========================
# تسجيل جديد
# =========================
@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "error": None}
    )

@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = crud.get_user_by_username(db, username)

    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "اسم المستخدم موجود مسبقًا"
            }
        )

    hashed_pw = bcrypt.hash(password)
    crud.create_user(db, username, hashed_pw)

    # تسجيل تلقائي بعد التسجيل
    response = RedirectResponse(url="/editor", status_code=302)

    # 🔴 مهم جدًا
    response.set_cookie(
        key="user",
        value=username,
        httponly=True,
        path="/"
    )

    return response

# =========================
# تسجيل الخروج
# =========================
@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login")

    # 🔴 مهم جدًا
    response.delete_cookie(
        key="user",
        path="/"
    )

    return response
