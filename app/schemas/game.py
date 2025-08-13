from pydantic import BaseModel
from typing import List, Optional


class WordPair(BaseModel):
    id: int
    tr: str
    en: str


class GameSession(BaseModel):
    level_id: int
    level_name: str
    words: List[WordPair]
    total_words: int
    required_correct_percentage: float = 70.0


class GameAnswer(BaseModel):
    word_id: int
    selected_tr: str
    selected_en: str
    response_time_ms: int


class GameSessionResult(BaseModel):
    session_id: str
    level_id: int
    total_words: int
    correct_answers: int
    incorrect_answers: int
    accuracy_percentage: float
    is_level_completed: bool
    is_next_level_unlocked: bool
    total_time_ms: int


class UserStats(BaseModel):
    user_id: int
    total_words_attempted: int
    total_correct: int
    total_incorrect: int
    overall_accuracy: float
    current_level: str
    next_level: Optional[str] = None
    progress_percentage: float


class LevelProgress(BaseModel):
    level_id: int
    level_name: str
    total_words: int
    completed_words: int
    correct_words: int
    incorrect_words: int
    accuracy_percentage: float
    is_completed: bool
    is_unlocked: bool
