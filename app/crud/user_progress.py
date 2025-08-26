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
    
    # A1 seviyesi için özel durum - her zaman açık
    from db.models.language_level import LanguageLevel
    level = db.query(LanguageLevel).filter(LanguageLevel.id == level_id).first()
    is_unlocked = level.name == "A1" if level else False
    
    user_progress = UserProgress(
        user_id=user_id,
        level_id=level_id,
        total_words=0,
        correct_attempts=0,
        total_attempts=0,
        completion_percentage=0.0,
        is_unlocked=is_unlocked,
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
    
    # Eğer mevcut seviye tamamlandıysa, bir sonraki seviyeyi aç
    if user_progress.is_completed:
        from db.models.language_level import LanguageLevel
        
        # Bir sonraki seviyeyi bul
        current_level = db.query(LanguageLevel).filter(LanguageLevel.id == word.level_id).first()
        if current_level:
            # Seviye sıralaması: A1 -> A2 -> B1 -> B2 -> C1 -> C2
            level_order = ["A1", "A2", "B1", "B2", "C1", "C2"]
            try:
                current_index = level_order.index(current_level.name.value)
                if current_index < len(level_order) - 1:
                    next_level_name = level_order[current_index + 1]
                    next_level = db.query(LanguageLevel).filter(LanguageLevel.name == next_level_name).first()
                    
                    if next_level:
                        # Bir sonraki seviye için progress kaydı oluştur veya güncelle
                        next_level_progress = get_user_progress_by_level(db, user_id, next_level.id)
                        if not next_level_progress:
                            next_level_progress = create_user_progress(db, user_id, next_level.id)
                        
                        # Bir sonraki seviyeyi aç
                        next_level_progress.is_unlocked = True
            except (ValueError, IndexError):
                pass  # Son seviyede ise bir şey yapma
    
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


def get_level_completion_stats(db: Session, level_name: str) -> dict:
    """Belirli seviye için genel tamamlanma istatistiklerini getirir"""
    from db.models.language_level import LanguageLevel
    
    # Seviyeyi bul
    level = db.query(LanguageLevel).filter(LanguageLevel.name == level_name).first()
    if not level:
        return {}
    
    # Bu seviyedeki tüm kullanıcı ilerlemelerini getir
    all_progress = db.query(UserProgress).filter(UserProgress.level_id == level.id).all()
    
    if not all_progress:
        return {
            "total_users": 0,
            "unlocked_users": 0,
            "completed_users": 0,
            "average_completion": 0.0,
            "average_attempts": 0.0
        }
    
    total_users = len(all_progress)
    unlocked_users = sum(1 for p in all_progress if p.is_unlocked)
    completed_users = sum(1 for p in all_progress if p.is_completed)
    
    total_completion = sum(p.completion_percentage for p in all_progress)
    total_attempts = sum(p.total_attempts for p in all_progress)
    
    average_completion = total_completion / total_users if total_users > 0 else 0
    average_attempts = total_attempts / total_users if total_users > 0 else 0
    
    return {
        "total_users": total_users,
        "unlocked_users": unlocked_users,
        "completed_users": completed_users,
        "locked_users": total_users - unlocked_users,
        "average_completion": round(average_completion, 2),
        "average_attempts": round(average_attempts, 2),
        "unlock_rate": round((unlocked_users / total_users * 100), 2) if total_users > 0 else 0,
        "completion_rate": round((completed_users / total_users * 100), 2) if total_users > 0 else 0
    }