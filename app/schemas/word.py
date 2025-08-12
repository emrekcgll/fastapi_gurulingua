from pydantic import BaseModel
from typing import Optional
from .language_level import LanguageLevel
from .sentence import Sentence


class WordBase(BaseModel):
    """Base schema for word"""
    tr: str
    en: str
    level_id: int
    sentence_id: Optional[int] = None


class Word(WordBase):
    """Schema for word response"""
    id: int
    level: Optional[LanguageLevel] = None
    sentence: Optional[Sentence] = None

    class Config:
        from_attributes = True
