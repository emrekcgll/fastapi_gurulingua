from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from db.base import Base


class Word(Base):
    __tablename__ = "word"

    id = Column(Integer, primary_key=True, index=True)
    tr = Column(String(100), nullable=False, index=True)
    en = Column(String(100), nullable=False, index=True)

    level_id = Column(Integer, ForeignKey("language_level.id"), nullable=False)
    level = relationship("LanguageLevel", back_populates="word")

    sentence_id = Column(Integer, ForeignKey("sentence.id"), unique=True)
    sentence = relationship("Sentence", back_populates="word")