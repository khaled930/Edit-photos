from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# SQLite database
# Use environment variable if available (for Railway/cloud), otherwise use local path
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Ensure database directory exists for SQLite
if DATABASE_URL.startswith("sqlite"):
    # Extract path from sqlite:///./test.db or sqlite:///test.db
    db_path = DATABASE_URL.replace("sqlite:///", "").replace("sqlite:///./", "")
    if db_path and not db_path.startswith(":memory:"):
        # Get directory path
        if "/" in db_path or "\\" in db_path:
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
        else:
            # File in current directory, no need to create directory
            pass

# إنشاء المحرك
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # مطلوب مع SQLite + FastAPI
    pool_pre_ping=True,  # Verify connections before using
    echo=False  # Set to True for SQL query logging
)

# جلسة قاعدة البيانات
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
