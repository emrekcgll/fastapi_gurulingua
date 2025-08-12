from pydantic import BaseModel


class LanguageLevelBase(BaseModel):
    """Base schema for language level"""
    level: str


class LanguageLevel(LanguageLevelBase):
    """Schema for language level response"""
    id: int

    class Config:
        from_attributes = True
