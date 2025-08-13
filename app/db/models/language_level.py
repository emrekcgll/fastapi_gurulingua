from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.base import Base


class LanguageLevel(Base):
    __tablename__ = "language_level"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(10), unique=True, nullable=False)

    # Sadece bu ikisi kalmalı
    words = relationship("Word", back_populates="level")
    user_progress = relationship("UserProgress", back_populates="level")