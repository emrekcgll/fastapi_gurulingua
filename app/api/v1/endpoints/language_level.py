from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from crud import language_level as crud
from schemas.language_level import LanguageLevel

router = APIRouter()


@router.get("/", response_model=List[LanguageLevel])
def get_language_levels(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """Get all language levels"""
    return crud.get_all_language_levels(db, skip, limit)


@router.get("/{level_id}", response_model=LanguageLevel)
def get_language_level(level_id: int, db: Session = Depends(get_db)):
    """Get a specific language level by ID"""
    language_level = crud.get_language_level(db, level_id)
    if not language_level:
        raise HTTPException(status_code=404, detail="Language level not found")
    return language_level
