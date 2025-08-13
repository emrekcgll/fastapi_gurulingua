from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base


class WordAttempt(Base):
    __tablename__ = "word_attempt"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("word.id"), nullable=False)
    user_progress_id = Column(Integer, ForeignKey("user_progress.id"), nullable=False)
    
    # Deneme sonucu
    is_correct = Column(Boolean, nullable=False)
    
    # Hangi kelime çifti eşleştirildi
    selected_tr = Column(String(100), nullable=False)  # Kullanıcının seçtiği TR kelime
    selected_en = Column(String(100), nullable=False)  # Kullanıcının seçtiği EN kelime
    
    # Doğru cevap
    correct_tr = Column(String(100), nullable=False)
    correct_en = Column(String(100), nullable=False)
    
    # Deneme süresi (milisaniye)
    response_time_ms = Column(Integer, nullable=True)
    
    # Timestamp
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="word_attempts")
    word = relationship("Word", back_populates="attempts")
    user_progress = relationship("UserProgress", back_populates="word_attempts")
