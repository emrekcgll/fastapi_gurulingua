from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from db.base import Base


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(255), nullable=False, index=True)  # The word itself
    translation = Column(String(255), nullable=False, index=True)  # Translation in target language
    pronunciation = Column(String(255), nullable=True)  # Optional pronunciation guide
    example_sentence = Column(Text, nullable=True)  # Optional example usage
    
    # Foreign Keys
    language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)
    level_id = Column(Integer, ForeignKey("language_levels.id"), nullable=False)
    
    # Relationships
    language = relationship("Language", back_populates="words")
    level = relationship("LanguageLevel", back_populates="words")
    attempts = relationship("WordAttempt", back_populates="word")
