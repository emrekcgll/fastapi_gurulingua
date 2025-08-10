from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from db.base import Base


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    tr = Column(String(100), nullable=False, index=True)
    en = Column(String(100), nullable=False, index=True)

    level_id = Column(Integer, ForeignKey("language_levels.id"), nullable=False)
    level = relationship("LanguageLevel", back_populates="words")

    sentence_id = Column(Integer, ForeignKey("sentences.id"), unique=True)
    sentence = relationship("Sentence", back_populates="word")
