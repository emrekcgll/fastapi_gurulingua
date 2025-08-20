from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.models.user_progress import UserProgress
from db.models.word_attempt import WordAttempt
from db.models.word import Word
from typing import Optional, List
from datetime import datetime


def get_user_progress_by_level(
    db: Session,
    user_id: int,
    level_id: int
) -> Optional[UserProgress]:
    """Kullanıcının belirli seviyedeki ilerlemesini getirir"""
    return db.query(UserProgress)\
        .filter(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.level_id == level_id
            )
        ).first()


def create_user_progress(
    db: Session,
    user_id: int,
    level_id: int
) -> UserProgress:
    """Kullanıcı için yeni seviye ilerlemesi oluşturur"""
    
    user_progress = UserProgress(
        user_id=user_id,
        level_id=level_id,
        total_words=0,
        correct_attempts=0,
        total_attempts=0,
        completion_percentage=0.0,
        is_unlocked=False,
        required_percentage=70.0
    )
    
    db.add(user_progress)
    db.commit()
    db.refresh(user_progress)
    
    return user_progress


def update_user_progress_after_attempt(
    db: Session,
    user_id: int,
    word_id: int,
    is_correct: bool
) -> None:
    """Kelime denemesinden sonra kullanıcı ilerlemesini günceller
    A1 seviyesinde 100 kelime var
    Kullanıcı 20 kelime denedi, 16'sını doğru bildi
    Başarı: 16/100 = %16 A2'ye geçemez
    
    Kullanıcı 80 kelime denedi, 70'ini doğru bildi  
    Başarı: 70/100 = %70 A2'ye geçebilir
    """
    
    # Kelimenin seviyesini bul
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        return
    
    # UserProgress kaydını bul veya oluştur
    user_progress = get_user_progress_by_level(db, user_id, word.level_id)
    
    if not user_progress:
        user_progress = create_user_progress(db, user_id, word.level_id)
    
    # İstatistikleri güncelle
    user_progress.total_attempts += 1
    if is_correct:
        user_progress.correct_attempts += 1
    
    # Seviyedeki toplam kelime sayısını bul
    total_words_in_level = db.query(Word)\
        .filter(Word.level_id == word.level_id, Word.is_active == True)\
        .count()
    
    # Başarı yüzdesi: Doğru bilinen kelime sayısı / Toplam kelime sayısı
    user_progress.completion_percentage = (
        user_progress.correct_attempts / total_words_in_level * 100
    )
    
    # Seviye kilidini kontrol et (%70 kuralı)
    user_progress.is_unlocked = user_progress.completion_percentage >= user_progress.required_percentage
    
    # Seviye tamamlanma durumunu kontrol et
    user_progress.is_completed = user_progress.completion_percentage >= 100.0
    
    db.commit()


def get_user_all_progress(db: Session, user_id: int) -> List[UserProgress]:
    """Kullanıcının tüm seviye ilerlemelerini getirir"""
    return db.query(UserProgress)\
        .filter(UserProgress.user_id == user_id)\
        .order_by(UserProgress.level_id)\
        .all()


def can_user_advance_to_level(
    db: Session,
    user_id: int,
    current_level_id: int
) -> bool:
    """Kullanıcının bir sonraki seviyeye geçip geçemeyeceğini kontrol eder"""
    
    user_progress = get_user_progress_by_level(db, user_id, current_level_id)
    if not user_progress:
        return False
    
    return user_progress.is_unlocked


def get_user_level_completion(
    db: Session,
    user_id: int,
    level_id: int
) -> dict:
    """Kullanıcının belirli seviyedeki tamamlanma durumunu getirir"""
    
    user_progress = get_user_progress_by_level(db, user_id, level_id)
    if not user_progress:
        return {
            "level_id": level_id,
            "is_unlocked": False,
            "completion_percentage": 0.0,
            "can_advance": False,
            "total_attempts": 0,
            "correct_attempts": 0
        }
    
    return {
        "level_id": level_id,
        "is_unlocked": user_progress.is_unlocked,
        "completion_percentage": user_progress.completion_percentage,
        "can_advance": user_progress.is_unlocked,
        "total_attempts": user_progress.total_attempts,
        "correct_attempts": user_progress.correct_attempts
    }


def reset_user_level_progress(
    db: Session,
    user_id: int,
    level_id: int
) -> bool:
    """Kullanıcının belirli seviyedeki ilerlemesini sıfırlar"""
    
    user_progress = get_user_progress_by_level(db, user_id, level_id)
    if user_progress:
        user_progress.total_words = 0
        user_progress.correct_attempts = 0
        user_progress.total_attempts = 0
        user_progress.completion_percentage = 0.0
        user_progress.is_unlocked = False
        user_progress.is_completed = False
        
        db.commit()
        return True
    
    return False


def unlock_user_level(
    db: Session,
    user_id: int,
    level_id: int
) -> bool:
    """Kullanıcının belirli seviyesini manuel olarak açar (admin işlemi)"""
    
    user_progress = get_user_progress_by_level(db, user_id, level_id)
    if user_progress:
        user_progress.is_unlocked = True
        db.commit()
        return True
    
    return False