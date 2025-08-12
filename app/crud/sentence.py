from sqlalchemy.orm import Session
from db.models.sentence import Sentence


def get_sentence(db: Session, sentence_id: int):
    """Get a specific sentence by ID"""
    return db.query(Sentence).filter(Sentence.id == sentence_id).first()


def get_all_sentences(db: Session, skip: int = 0, limit: int = 100):
    """Get all sentences with pagination"""
    return db.query(Sentence).offset(skip).limit(limit).all()
