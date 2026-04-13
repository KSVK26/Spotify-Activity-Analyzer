from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(String, primary_key=True)
    spotify_user_id = Column(String, nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    token_expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
