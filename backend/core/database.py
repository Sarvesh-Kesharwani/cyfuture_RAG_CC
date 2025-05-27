from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite DB path
DATABASE_URL = "sqlite:///./backend/database/complaints.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session maker
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Declarative base for models
Base = declarative_base()
