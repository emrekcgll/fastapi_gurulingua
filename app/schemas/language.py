from pydantic import BaseModel
from typing import Optional


class LanguageResponse(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    email: str
    native_language: Optional[LanguageResponse] = None  # ID değil, obje
    target_language: Optional[LanguageResponse] = None  # ID değil, obje

    class Config:
        from_attributes = True
