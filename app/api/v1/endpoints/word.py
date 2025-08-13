from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from api.v1.dependencies.database import get_db
from api.v1.dependencies.auth import get_current_user, get_current_superadmin
from crud import word as crud
from schemas.word import Word
from db.models.user import User

router = APIRouter()


@router.get("/", response_model=List[Word])
def get_words(
    db: Session = Depends(get_db), 
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get all words - Requires authentication"""
    return crud.get_all_words(db, skip, limit)


@router.get("/{word_id}", response_model=Word)
def get_word(
    word_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific word by ID - Requires authentication"""
    word = crud.get_word(db, word_id)
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    return word


@router.get("/level/{level_id}", response_model=List[Word])
def get_words_by_level(
    level_id: int, 
    db: Session = Depends(get_db), 
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get words by language level - Requires authentication"""
    return crud.get_words_by_level(db, level_id, skip, limit)
