from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from db.base import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)
    level_id = Column(Integer, ForeignKey("language_levels.id"), nullable=False)
    
    # Progress tracking
    total_words = Column(Integer, default=0)  # Total words in this level
    correct_answers = Column(Integer, default=0)  # Correct answers in this level
    total_attempts = Column(Integer, default=0)  # Total attempts in this level
    success_rate = Column(Float, default=0.0)  # Percentage of correct answers
    is_completed = Column(Boolean, default=False)  # True if level is completed (70%+ success)
    is_unlocked = Column(Boolean, default=False)  # True if level is accessible
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    language = relationship("Language", back_populates="user_progress")
    level = relationship("LanguageLevel", back_populates="user_progress")
