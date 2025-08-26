from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.models.word import Word
from db.models.language_level import LanguageLevel, LevelName
from typing import List, Optional


def create_word(db: Session, word_tr: str, word_en: str, level_id: int):
    """Create a new word"""
    # level_id'nin int olduğundan emin ol
    if not isinstance(level_id, int):
        raise ValueError(f"level_id must be an integer, got {type(level_id)}")
    
    word = Word(tr=word_tr, en=word_en, level_id=level_id, is_active=True)
    db.add(word)
    db.commit()
    db.refresh(word)
    return word


def get_word_by_word_tr(db: Session, word_tr: str) -> Optional[Word]:
    """Get a word by word_tr"""
    return db.query(Word).filter(Word.tr == word_tr).first()
    

def get_word_by_word_en(db: Session, word_en: str) -> Optional[Word]:
    """Get a word by word_en"""
    return db.query(Word).filter(Word.en == word_en).first()


def get_word(db: Session, word_id: int):
    """Get a specific word by ID"""
    return db.query(Word).filter(Word.id == word_id).first()


def get_all_words(db: Session, skip: int = 0, limit: int = 100):
    """Get all words with pagination"""
    return db.query(Word).offset(skip).limit(limit).all()


def get_words_by_level(db: Session, level_name: str, skip: int = 0, limit: int = 100) -> List[Word]:
    """Belirli seviyedeki kelimeleri getirir"""
    return db.query(Word)\
        .join(LanguageLevel)\
        .filter(
            and_(
                LanguageLevel.name == level_name,
                Word.is_active == True
            )
        )\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_words_by_level_id(db: Session, level_id: int, skip: int = 0, limit: int = 100) -> List[Word]:
    """Belirli seviye ID'sine göre kelimeleri getirir"""
    return db.query(Word)\
        .filter(
            and_(
                Word.level_id == level_id,
                Word.is_active == True
            )
        )\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_total_words_by_level(db: Session, level_name: str) -> int:
    """Belirli seviyedeki toplam kelime sayısını getirir"""
    return db.query(Word)\
        .join(LanguageLevel)\
        .filter(
            and_(
                LanguageLevel.name == level_name,
                Word.is_active == True
            )
        )\
        .count()


def get_total_words_by_level_id(db: Session, level_id: int) -> int:
    """Belirli seviye ID'sine göre toplam kelime sayısını getirir"""
    return db.query(Word)\
        .filter(
            and_(
                Word.level_id == level_id,
                Word.is_active == True
            )
        )\
        .count()


def get_available_words_for_user(
    db: Session, 
    user_id: int, 
    level_name: str,
    skip: int = 0, 
    limit: int = 100
) -> List[Word]:
    """Kullanıcının erişebileceği kelimeleri getirir (seviye kilitli ise boş liste döner)"""
    from crud.user_progress import get_user_level_completion
    
    # Seviye bilgisini al
    level = db.query(LanguageLevel).filter(LanguageLevel.name == level_name).first()
    if not level:
        return []
    
    # Kullanıcının seviye durumunu kontrol et
    level_completion = get_user_level_completion(db, user_id, level.id)
    
    # Seviye kilitli ise boş liste döner
    if not level_completion["is_unlocked"]:
        return []
    
    # Seviye açıksa kelimeleri getir
    return get_words_by_level_id(db, level.id, skip, limit)


def get_level_info(db: Session, level_name: str) -> Optional[dict]:
    """Seviye bilgilerini getirir"""
    level = db.query(LanguageLevel).filter(LanguageLevel.name == level_name).first()
    if not level:
        return None
    
    total_words = get_total_words_by_level_id(db, level.id)
    
    return {
        "id": level.id,
        "name": level.name.value,
        "total_words": total_words,
        "is_active": True
    }


def get_all_levels_info(db: Session) -> List[dict]:
    """Tüm seviyelerin bilgilerini getirir"""
    levels = db.query(LanguageLevel).all()
    result = []
    
    for level in levels:
        total_words = get_total_words_by_level_id(db, level.id)
        result.append({
            "id": level.id,
            "name": level.name.value,
            "total_words": total_words,
            "is_active": True
        })
    
    return result