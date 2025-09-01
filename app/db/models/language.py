from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db.base import Base


class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(2), unique=True, index=True, nullable=False)  # EN, TR, DE
    name = Column(String(50), nullable=False)  # English, Turkish, German
    
    # Relationships
    native_language_users = relationship("User", foreign_keys="User.native_language_id", back_populates="native_language")
    target_language_users = relationship("User", foreign_keys="User.target_language_id", back_populates="target_language")
    words = relationship("Word", back_populates="language")
    user_progress = relationship("UserProgress", back_populates="language")
