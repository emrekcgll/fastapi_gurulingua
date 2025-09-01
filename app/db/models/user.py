from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
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
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    provider = Column(Enum(UserProvider))
    role = Column(Enum(UserRole))
    is_active = Column(Boolean, default=True)
    hashed_password = Column(String, nullable=True)
    
    # Language preferences
    native_language_id = Column(Integer, ForeignKey("languages.id"), nullable=True)
    target_language_id = Column(Integer, ForeignKey("languages.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    native_language = relationship("Language", foreign_keys=[native_language_id], back_populates="native_language_users")
    target_language = relationship("Language", foreign_keys=[target_language_id], back_populates="target_language_users")
    progress = relationship("UserProgress", back_populates="user")
    word_attempts = relationship("WordAttempt", back_populates="user")