from sqlalchemy.orm import Session
from db.models.word import Word


def get_word(db: Session, word_id: int):
    """Get a specific word by ID"""
    return db.query(Word).filter(Word.id == word_id).first()


def get_all_words(db: Session, skip: int = 0, limit: int = 100):
    """Get all words with pagination"""
    return db.query(Word).offset(skip).limit(limit).all()