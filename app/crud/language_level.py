from sqlalchemy.orm import Session
from db.models.language_level import LanguageLevel


def get_language_level(db: Session, level_id: int):
    """Get a specific language level by ID"""
    return db.query(LanguageLevel).filter(LanguageLevel.id == level_id).first()


def get_all_language_levels(db: Session, skip: int = 0, limit: int = 100):
    """Get all language levels with pagination"""
    return db.query(LanguageLevel).offset(skip).limit(limit).all()
