from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse
from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.database import crud
from passlib.context import CryptContext
import os
import bcrypt as bcrypt_lib

# Password hashing context - initialize with error handling
try:
    # Try to initialize with passlib first
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # Test the context to ensure it works
    _ = pwd_context.hash("test")
    USE_PASSLIB = True
except Exception as e:
    print(f"Warning: Failed to initialize passlib bcrypt context: {e}")
    # Fallback to direct bcrypt
    USE_PASSLIB = False
    print("Using direct bcrypt library instead")

def hash_password(password: str) -> str:
    """Hash password using available method"""
    if USE_PASSLIB:
        return pwd_context.hash(password)
    else:
        # Use bcrypt directly
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            raise ValueError("password cannot be longer than 72 bytes")
        salt = bcrypt_lib.gensalt()
        hashed = bcrypt_lib.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password using available method"""
    if USE_PASSLIB:
        return pwd_context.verify(password, hashed)
    else:
        # Use bcrypt directly
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed.encode('utf-8')
        return bcrypt_lib.checkpw(password_bytes, hashed_bytes)

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

    if not user or not verify_password(password, user.password):
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
        try:
            # Ensure password is not too long for bcrypt (72 bytes max)
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                return JSONResponse(
                    {"error": "كلمة المرور طويلة جداً (الحد الأقصى 72 حرف)"},
                    status_code=400
                )
            
            hashed_pw = hash_password(password)
            crud.create_user(db, username.strip(), hashed_pw)
        except ValueError as e:
            # Handle bcrypt-specific errors
            if "password cannot be longer than 72 bytes" in str(e):
                return JSONResponse(
                    {"error": "كلمة المرور طويلة جداً (الحد الأقصى 72 حرف)"},
                    status_code=400
                )
            raise

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
