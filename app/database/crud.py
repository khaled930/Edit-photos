from sqlalchemy.orm import Session
from .models import User, Image
import hashlib

# =========================
# Helpers
# =========================
def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# =========================
# Users CRUD
# =========================
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, password: str):
    hashed = _hash_password(password)
    user = User(username=username, password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def verify_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if user and user.password == _hash_password(password):
        return user
    return None

# =========================
# Images CRUD
# =========================
def create_image(db: Session, filename: str, image_url: str, user_id: int):
    image = Image(
        filename=filename,
        image_url=image_url,
        user_id=user_id
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image

def get_user_images(db: Session, user_id: int):
    return db.query(Image).filter(Image.user_id == user_id).all()
