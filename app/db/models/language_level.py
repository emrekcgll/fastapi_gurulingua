from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.base import Base


class LanguageLevel(Base):
    __tablename__ = "language_levels"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(10), unique=True, nullable=False)

    words = relationship("Word", back_populates="level")
