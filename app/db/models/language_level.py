from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from db.base import Base
import enum


class LevelName(enum.Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

    
class LanguageLevel(Base):
    __tablename__ = "language_level"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(LevelName), unique=True, nullable=False)

    words = relationship("Word", back_populates="level")
    user_progress = relationship("UserProgress", back_populates="level")
