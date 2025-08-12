from pydantic import BaseModel


class SentenceBase(BaseModel):
    """Base schema for sentence"""
    tr: str | None = None
    en: str | None = None


class Sentence(SentenceBase):
    """Schema for sentence response"""
    id: int

    class Config:
        from_attributes = True
