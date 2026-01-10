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
    try:
        user = User(username=username, password=password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise e

# =========================
# Images CRUD
# =========================
def create_image(db: Session, filename: str, image_url: str, user_id: int):
    try:
        image = Image(
            filename=filename,
            image_url=image_url,
            user_id=user_id
        )
        db.add(image)
        db.commit()
        db.refresh(image)
        return image
    except Exception as e:
        db.rollback()
        raise e

def get_user_images(db: Session, user_id: int):
    return db.query(Image).filter(Image.user_id == user_id).all()
