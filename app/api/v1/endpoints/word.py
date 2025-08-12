from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from crud import word as crud
from schemas.word import Word

router = APIRouter()


@router.get("/", response_model=List[Word])
def get_words(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """Get all words"""
    return crud.get_all_words(db, skip, limit)


@router.get("/{word_id}", response_model=Word)
def get_word(word_id: int, db: Session = Depends(get_db)):
    """Get a specific word by ID"""
    word = crud.get_word(db, word_id)
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    return word


@router.get("/level/{level_id}", response_model=List[Word])
def get_words_by_level(level_id: int, db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """Get words by language level"""
    return crud.get_words_by_level(db, level_id, skip, limit)
