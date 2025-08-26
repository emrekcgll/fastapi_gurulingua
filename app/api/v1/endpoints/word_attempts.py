from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from api.v1.dependencies.database import get_db
from api.v1.dependencies.auth import get_current_user
from crud.word_attempt import create_word_attempt, get_user_word_attempts
from crud.user_progress import update_user_progress_after_attempt
from db.models.user import User
from pydantic import BaseModel

router = APIRouter()


class WordAttemptCreate(BaseModel):
    word_id: int
    is_correct: bool


class WordAttemptResponse(BaseModel):
    id: int
    word_id: int
    user_id: int
    is_correct: bool
    created_at: str


@router.post("/attempts", response_model=WordAttemptResponse)
def create_word_attempt_endpoint(
    attempt_data: WordAttemptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kullanıcının kelime denemesini kaydeder ve ilerlemesini günceller
    """
    from crud.word import get_word
    
    # Kelimenin var olup olmadığını kontrol et
    word = get_word(db, attempt_data.word_id)
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kelime bulunamadı"
        )
    
    # Kelime denemesini oluştur
    word_attempt = create_word_attempt(
        db=db,
        user_id=current_user.id,
        word_id=attempt_data.word_id,
        is_correct=attempt_data.is_correct
    )
    
    # Kullanıcı ilerlemesini güncelle
    update_user_progress_after_attempt(
        db=db,
        user_id=current_user.id,
        word_id=attempt_data.word_id,
        is_correct=attempt_data.is_correct
    )
    
    return {
        "id": word_attempt.id,
        "word_id": word_attempt.word_id,
        "user_id": word_attempt.user_id,
        "is_correct": word_attempt.is_correct,
        "created_at": word_attempt.created_at.isoformat() if word_attempt.created_at else None
    }


@router.get("/attempts/my", response_model=List[WordAttemptResponse])
def get_my_word_attempts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kullanıcının kelime denemelerini getirir
    """
    attempts = get_user_word_attempts(db, current_user.id, skip, limit)
    
    return [
        {
            "id": attempt.id,
            "word_id": attempt.word_id,
            "user_id": attempt.user_id,
            "is_correct": attempt.is_correct,
            "created_at": attempt.created_at.isoformat() if attempt.created_at else None
        }
        for attempt in attempts
    ]


@router.get("/attempts/my/stats")
def get_my_attempt_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kullanıcının kelime deneme istatistiklerini getirir
    """
    from crud.word_attempt import get_user_attempt_stats
    
    stats = get_user_attempt_stats(db, current_user.id)
    
    return {
        "user_id": current_user.id,
        "total_attempts": stats["total_attempts"],
        "correct_attempts": stats["correct_attempts"],
        "incorrect_attempts": stats["incorrect_attempts"],
        "success_rate": stats["success_rate"],
        "total_words_attempted": stats["total_words_attempted"]
    }


@router.get("/attempts/my/level/{level_name}")
def get_my_attempts_by_level(
    level_name: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kullanıcının belirli seviyedeki kelime denemelerini getirir
    """
    from crud.word_attempt import get_user_attempts_by_level
    from db.models.language_level import LevelName
    
    # Seviye adını doğrula
    try:
        LevelName(level_name.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz seviye adı: {level_name}. Geçerli seviyeler: A1, A2, B1, B2, C1, C2"
        )
    
    attempts = get_user_attempts_by_level(
        db, 
        current_user.id, 
        level_name.upper(), 
        skip, 
        limit
    )
    
    return {
        "level": level_name.upper(),
        "attempts": [
            {
                "id": attempt.id,
                "word_id": attempt.word_id,
                "word_tr": attempt.word.tr,
                "word_en": attempt.word.en,
                "is_correct": attempt.is_correct,
                "created_at": attempt.created_at.isoformat() if attempt.created_at else None
            }
            for attempt in attempts
        ],
        "skip": skip,
        "limit": limit
    }
