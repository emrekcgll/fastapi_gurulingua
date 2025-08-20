from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.models.word_attempt import WordAttempt
from typing import Optional, List
from datetime import datetime


def create_word_attempt(
    db: Session,
    user_id: int,
    word_id: int,
    selected_word_id: int,
    is_correct: bool,
    user_progress_id: Optional[int] = None
) -> WordAttempt:
    """Yeni kelime denemesi oluşturur"""
    
    word_attempt = WordAttempt(
        user_id=user_id,
        word_id=word_id,
        selected_word_id=selected_word_id,
        is_correct=is_correct,
        user_progress_id=user_progress_id
    )
    
    db.add(word_attempt)
    db.commit()
    db.refresh(word_attempt)
    
    return word_attempt


def get_word_attempt_by_id(db: Session, attempt_id: int) -> Optional[WordAttempt]:
    """ID ile kelime denemesi getirir"""
    return db.query(WordAttempt).filter(WordAttempt.id == attempt_id).first()


def get_user_word_attempts(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[WordAttempt]:
    """Kullanıcının kelime denemelerini getirir (sayfalama ile)"""
    return db.query(WordAttempt)\
        .filter(WordAttempt.user_id == user_id)\
        .order_by(WordAttempt.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_user_word_attempts_by_word(
    db: Session,
    user_id: int,
    word_id: int
) -> List[WordAttempt]:
    """Kullanıcının belirli kelime için tüm denemelerini getirir"""
    return db.query(WordAttempt)\
        .filter(
            and_(
                WordAttempt.user_id == user_id,
                WordAttempt.word_id == word_id
            )
        )\
        .order_by(WordAttempt.created_at.desc())\
        .all()


def get_word_attempts_by_word(
    db: Session,
    word_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[WordAttempt]:
    """Belirli kelime için tüm denemeleri getirir"""
    return db.query(WordAttempt)\
        .filter(WordAttempt.word_id == word_id)\
        .order_by(WordAttempt.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_user_recent_attempts(
    db: Session,
    user_id: int,
    limit: int = 10
) -> List[WordAttempt]:
    """Kullanıcının son kelime denemelerini getirir"""
    return db.query(WordAttempt)\
        .filter(WordAttempt.user_id == user_id)\
        .order_by(WordAttempt.created_at.desc())\
        .limit(limit)\
        .all()


def get_word_attempt_count_by_user(
    db: Session,
    user_id: int
) -> int:
    """Kullanıcının toplam kelime deneme sayısını getirir"""
    return db.query(WordAttempt).filter(WordAttempt.user_id == user_id).count()


def get_correct_attempt_count_by_user(
    db: Session,
    user_id: int
) -> int:
    """Kullanıcının doğru yanıt sayısını getirir"""
    return db.query(WordAttempt)\
        .filter(
            and_(
                WordAttempt.user_id == user_id,
                WordAttempt.is_correct == True
            )
        ).count()