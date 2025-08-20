from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from db.base import Base


class Word(Base):
    __tablename__ = "word"

    id = Column(Integer, primary_key=True, index=True)
    tr = Column(String(100), nullable=False)
    en = Column(String(100), nullable=False)

    level_id = Column(Integer, ForeignKey("language_level.id"), nullable=False)
    level = relationship("LanguageLevel", back_populates="words")

    # Sadece aktif/pasif durumu
    is_active = Column(Boolean, default=True)  # Kelime aktif mi?
    
    # Relationships
    word_attempts = relationship("WordAttempt", back_populates="word")