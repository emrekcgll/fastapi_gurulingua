from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base


class WordAttempt(Base):
    __tablename__ = "word_attempt"

    id = Column(Integer, primary_key=True, index=True)

    # Kelime bilgileri
    word_id = Column(Integer, ForeignKey("word.id"), nullable=False)
    word = relationship("Word", back_populates="word_attempts", foreign_keys=[word_id])

    # Kullanıcı bilgileri
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="word_attempts")

    # Oyun sonucu
    is_correct = Column(Boolean, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # UserProgress ile ilişki
    user_progress_id = Column(Integer, ForeignKey("user_progress.id"), nullable=True)
    user_progress = relationship("UserProgress", back_populates="word_attempts")