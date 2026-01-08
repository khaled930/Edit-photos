from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite database (ملف واحد)
DATABASE_URL = "sqlite:///./test.db"

# إنشاء المحرك
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # مطلوب مع SQLite + FastAPI
)

# جلسة قاعدة البيانات
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
