from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from crud import sentence as crud
from schemas.sentence import Sentence

router = APIRouter()


@router.get("/", response_model=List[Sentence])
def get_sentences(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """Get all sentences"""
    return crud.get_all_sentences(db, skip, limit)


@router.get("/{sentence_id}", response_model=Sentence)
def get_sentence(sentence_id: int, db: Session = Depends(get_db)):
    """Get a specific sentence by ID"""
    sentence = crud.get_sentence(db, sentence_id)
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found")
    return sentence
