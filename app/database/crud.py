from sqlalchemy.orm import Session
from .models import User, Image

# =========================
# Users CRUD
# =========================
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_all_users(db: Session):
    return db.query(User).all()

def create_user(db: Session, username: str, password: str):
    # Password is already hashed with bcrypt before being passed here
    user = User(username=username, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

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
