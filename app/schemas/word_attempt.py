from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WordAttemptBase(BaseModel):
    word_id: int
    user_progress_id: int
    is_correct: bool
    selected_tr: str
    selected_en: str
    correct_tr: str
    correct_en: str
    response_time_ms: Optional[int] = None


class WordAttemptCreate(WordAttemptBase):
    user_id: int


class WordAttemptUpdate(BaseModel):
    is_correct: Optional[bool] = None
    response_time_ms: Optional[int] = None


class WordAttempt(WordAttemptBase):
    id: int
    user_id: int
    attempted_at: datetime

    class Config:
        from_attributes = True


class WordAttemptWithWord(WordAttempt):
    word_tr: str
    word_en: str
    level_name: str


class GameResult(BaseModel):
    word_id: int
    is_correct: bool
    response_time_ms: int
    correct_tr: str
    correct_en: str
    selected_tr: str
    selected_en: str
