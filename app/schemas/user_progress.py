from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserProgressBase(BaseModel):
    level_id: int
    is_completed: bool = False
    completion_percentage: float = 0.0
    is_unlocked: bool = False


class UserProgressCreate(UserProgressBase):
    user_id: int


class UserProgressUpdate(BaseModel):
    is_completed: Optional[bool] = None
    completion_percentage: Optional[float] = None
    is_unlocked: Optional[bool] = None


class UserProgress(UserProgressBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProgressWithLevel(UserProgress):
    level_name: str
