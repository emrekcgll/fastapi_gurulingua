from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base
import enum

class UserRole(enum.Enum):
    USER = "user"
    SUPERADMIN = "superadmin"


class UserProvider(enum.Enum):
    LOCAL = "local"
    GOOGLE = "google"
    FACEBOOK = "facebook"


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    provider = Column(Enum(UserProvider))
    role = Column(Enum(UserRole))
    is_active = Column(Boolean, default=True)
    hashed_password = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    progress = relationship("UserProgress", back_populates="user")
    word_attempts = relationship("WordAttempt", back_populates="user")