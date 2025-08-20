from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    level_id = Column(Integer, ForeignKey("language_level.id"), nullable=False)

    # Seviye tamamlanma durumu
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Float, default=0.0)  # 0.0 - 100.0

    # Başarı istatistikleri
    total_words = Column(Integer, default=0)  # Bu seviyedeki toplam kelime sayısı
    correct_attempts = Column(Integer, default=0)  # Doğru yanıt sayısı
    total_attempts = Column(Integer, default=0)  # Toplam deneme sayısı

    # Seviye kilidi (A1'den %70 başarı gerekli)
    is_unlocked = Column(Boolean, default=False)
    required_percentage = Column(Float, default=70.0)  # Bir sonraki seviyeye geçmek için gerekli yüzde

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="progress")
    level = relationship("LanguageLevel", back_populates="user_progress")
    word_attempts = relationship("WordAttempt", back_populates="user_progress")