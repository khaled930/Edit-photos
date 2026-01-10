from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.database import crud
from passlib.context import CryptContext
import os

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

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
    html_path = os.path.join("app", "static", "login.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return JSONResponse({"error": "Login page not found"}, status_code=404)

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, username)

    if not user or not pwd_context.verify(password, user.password):
        return JSONResponse(
            {"error": "اسم المستخدم أو كلمة المرور غير صحيحة"},
            status_code=401
        )

    response = RedirectResponse(url="/editor", status_code=302)
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
    html_path = os.path.join("app", "static", "register.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return JSONResponse({"error": "Register page not found"}, status_code=404)

@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Validate input
        if not username or not username.strip():
            return JSONResponse(
                {"error": "اسم المستخدم مطلوب"},
                status_code=400
            )
        
        if not password or len(password) < 3:
            return JSONResponse(
                {"error": "كلمة المرور يجب أن تكون 3 أحرف على الأقل"},
                status_code=400
            )

        # Check if user exists
        existing_user = crud.get_user_by_username(db, username)
        if existing_user:
            return JSONResponse(
                {"error": "اسم المستخدم موجود مسبقًا"},
                status_code=400
            )

        # Hash password and create user
        hashed_pw = pwd_context.hash(password)
        crud.create_user(db, username.strip(), hashed_pw)

        # تسجيل تلقائي بعد التسجيل
        response = RedirectResponse(url="/editor", status_code=302)
        response.set_cookie(
            key="user",
            value=username.strip(),
            httponly=True,
            path="/"
        )

        return response
    except Exception as e:
        # Log error and return user-friendly message
        print(f"Error creating user: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            {"error": "حدث خطأ أثناء إنشاء الحساب. يرجى المحاولة مرة أخرى."},
            status_code=500
        )

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
