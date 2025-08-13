from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from api.v1.dependencies.database import get_db
from api.v1.dependencies.auth import get_current_user
from crud import sentence as crud
from schemas.sentence import Sentence
from db.models.user import User

router = APIRouter()


@router.get("/", response_model=List[Sentence])
def get_sentences(
    db: Session = Depends(get_db), 
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get all sentences - Requires authentication"""
    return crud.get_all_sentences(db, skip, limit)


@router.get("/{sentence_id}", response_model=Sentence)
def get_sentence(
    sentence_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific sentence by ID - Requires authentication"""
    sentence = crud.get_sentence(db, sentence_id)
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found")
    return sentence
