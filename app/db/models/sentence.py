from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from db.base import Base


class Sentence(Base):
    __tablename__ = "sentence"

    id = Column(Integer, primary_key=True, index=True)
    tr = Column(Text)
    en = Column(Text)

    word = relationship("Word", back_populates="sentence", uselist=False)