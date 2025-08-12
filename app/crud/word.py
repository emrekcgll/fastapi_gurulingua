from sqlalchemy.orm import Session
from db.models.word import Word


def get_word(db: Session, word_id: int):
    """Get a specific word by ID"""
    return db.query(Word).filter(Word.id == word_id).first()


def get_all_words(db: Session, skip: int = 0, limit: int = 100):
    """Get all words with pagination"""
    return db.query(Word).offset(skip).limit(limit).all()


def get_words_by_level(db: Session, level_id: int, skip: int = 0, limit: int = 100):
    """Get words by language level with pagination"""
    return db.query(Word).filter(Word.level_id == level_id).offset(skip).limit(limit).all()
