from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from db.base import Base


class WordAttempt(Base):
    __tablename__ = "word_attempts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    
    # Attempt details
    user_answer = Column(String(255), nullable=False)  # User's answer
    is_correct = Column(Boolean, nullable=False)  # Whether the answer was correct
    response_time = Column(Integer, nullable=True)  # Response time in milliseconds
    
    # Timestamps
    attempted_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="word_attempts")
    word = relationship("Word", back_populates="attempts")
