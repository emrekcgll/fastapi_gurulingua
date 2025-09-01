from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db.base import Base


class LanguageLevel(Base):
    __tablename__ = "language_levels"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(2), unique=True, index=True, nullable=False)  # A1, A2, B1, B2, C1, C2
    name = Column(String(50), nullable=False)  # Beginner, Elementary, Intermediate, etc.
    order = Column(Integer, nullable=False)  # 1, 2, 3, 4, 5, 6 for progression order
    
    # Relationships
    words = relationship("Word", back_populates="level")
    user_progress = relationship("UserProgress", back_populates="level")
