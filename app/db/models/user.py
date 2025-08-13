from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.base import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    provider = Column(String, default="local") # local, google, facebook
    role = Column(String, default="user") # user, superadmin
    is_active = Column(Boolean, default=True)
    hashed_password = Column(String, nullable=True)

    # timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Yeni relationships
    progress = relationship("UserProgress", back_populates="user")
    word_attempts = relationship("WordAttempt", back_populates="user")