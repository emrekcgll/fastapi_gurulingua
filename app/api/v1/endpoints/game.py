from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from db.session import get_db
from db.models.user import User
from db.models.word import Word
from db.models.language_level import LanguageLevel
from db.models.user_progress import UserProgress
from db.models.word_attempt import WordAttempt
from schemas.game import (
    GameSession, GameAnswer, GameSessionResult, 
    UserStats, LevelProgress, WordPair
)
from schemas.user_progress import UserProgressCreate, UserProgressUpdate
from schemas.word_attempt import WordAttemptCreate
from api.v1.dependencies.auth import get_current_user

router = APIRouter()


@router.post("/start-session/{level_id}", response_model=GameSession)
def start_game_session(
    level_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Belirli bir seviyede oyun oturumu başlatır"""
    
    # Seviyeyi kontrol et
    level = db.query(LanguageLevel).filter(LanguageLevel.id == level_id).first()
    if not level:
        raise HTTPException(status_code=404, detail="Seviye bulunamadı")
    
    # Kullanıcının bu seviyeye erişim hakkı var mı kontrol et
    user_progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.level_id == level_id
    ).first()
    
    if not user_progress:
        # İlk kez bu seviyeye giriyor, progress oluştur
        user_progress = UserProgress(
            user_id=current_user.id,
            level_id=level_id,
            is_unlocked=True if level_id == 1 else False  # A1 varsayılan olarak açık
        )
        db.add(user_progress)
        db.commit()
        db.refresh(user_progress)
    
    if not user_progress.is_unlocked:
        raise HTTPException(
            status_code=403, 
            detail="Bu seviyeye erişim için önceki seviyeyi %70 başarı ile tamamlamanız gerekir"
        )
    
    # Seviyedeki kelimeleri getir
    words = db.query(Word).filter(Word.level_id == level_id).all()
    if not words:
        raise HTTPException(status_code=404, detail="Bu seviyede kelime bulunamadı")
    
    word_pairs = [WordPair(id=word.id, tr=word.tr, en=word.en) for word in words]
    
    return GameSession(
        level_id=level_id,
        level_name=level.level,
        words=word_pairs,
        total_words=len(word_pairs)
    )


@router.post("/submit-answer", response_model=GameSessionResult)
def submit_game_answer(
    answer: GameAnswer,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kelime eşleştirme cevabını kaydeder ve sonucu döner"""
    
    # Kelimeyi kontrol et
    word = db.query(Word).filter(Word.id == answer.word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Kelime bulunamadı")
    
    # Kullanıcının progress'ini bul
    user_progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.level_id == word.level_id
    ).first()
    
    if not user_progress:
        raise HTTPException(status_code=404, detail="Kullanıcı ilerlemesi bulunamadı")
    
    # Cevabın doğru olup olmadığını kontrol et
    is_correct = (
        answer.selected_tr == word.tr and 
        answer.selected_en == word.en
    )
    
    # WordAttempt kaydet
    word_attempt = WordAttempt(
        user_id=current_user.id,
        word_id=answer.word_id,
        user_progress_id=user_progress.id,
        is_correct=is_correct,
        selected_tr=answer.selected_tr,
        selected_en=answer.selected_en,
        correct_tr=word.tr,
        correct_en=word.en,
        response_time_ms=answer.response_time_ms
    )
    db.add(word_attempt)
    
    # Progress'i güncelle
    total_attempts = db.query(WordAttempt).filter(
        WordAttempt.user_progress_id == user_progress.id
    ).count()
    
    correct_attempts = db.query(WordAttempt).filter(
        WordAttempt.user_progress_id == user_progress.id,
        WordAttempt.is_correct == True
    ).count()
    
    completion_percentage = (correct_attempts / total_attempts) * 100 if total_attempts > 0 else 0
    
    user_progress.completion_percentage = completion_percentage
    user_progress.is_completed = completion_percentage >= 70.0
    
    # Sonraki seviyeyi aç
    if user_progress.is_completed:
        next_level = db.query(LanguageLevel).filter(
            LanguageLevel.id == word.level_id + 1
        ).first()
        if next_level:
            next_progress = db.query(UserProgress).filter(
                UserProgress.user_id == current_user.id,
                UserProgress.level_id == next_level.id
            ).first()
            if next_progress:
                next_progress.is_unlocked = True
    
    db.commit()
    
    # Sonuç hesapla
    accuracy_percentage = (correct_attempts / total_attempts) * 100 if total_attempts > 0 else 0
    
    return GameSessionResult(
        session_id=str(uuid.uuid4()),
        level_id=word.level_id,
        total_words=total_attempts,
        correct_answers=correct_attempts,
        incorrect_answers=total_attempts - correct_attempts,
        accuracy_percentage=accuracy_percentage,
        is_level_completed=user_progress.is_completed,
        is_next_level_unlocked=user_progress.is_completed,
        total_time_ms=answer.response_time_ms
    )


@router.get("/user-stats", response_model=UserStats)
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kullanıcının genel istatistiklerini döner"""
    
    # Tüm denemeleri say
    total_attempts = db.query(WordAttempt).filter(
        WordAttempt.user_id == current_user.id
    ).count()
    
    correct_attempts = db.query(WordAttempt).filter(
        WordAttempt.user_id == current_user.id,
        WordAttempt.is_correct == True
    ).count()
    
    incorrect_attempts = total_attempts - correct_attempts
    overall_accuracy = (correct_attempts / total_attempts) * 100 if total_attempts > 0 else 0
    
    # Mevcut seviyeyi bul
    current_progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.is_completed == False
    ).order_by(UserProgress.level_id).first()
    
    current_level = "A1"  # Varsayılan
    if current_progress:
        level = db.query(LanguageLevel).filter(LanguageLevel.id == current_progress.level_id).first()
        if level:
            current_level = level.level
    
    # Sonraki seviyeyi bul
    next_level = None
    if current_progress:
        next_level_obj = db.query(LanguageLevel).filter(
            LanguageLevel.id == current_progress.level_id + 1
        ).first()
        if next_level_obj:
            next_level = next_level_obj.level
    
    # Genel ilerleme yüzdesi
    total_levels = db.query(LanguageLevel).count()
    completed_levels = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.is_completed == True
    ).count()
    progress_percentage = (completed_levels / total_levels) * 100 if total_levels > 0 else 0
    
    return UserStats(
        user_id=current_user.id,
        total_words_attempted=total_attempts,
        total_correct=correct_attempts,
        total_incorrect=incorrect_attempts,
        overall_accuracy=overall_accuracy,
        current_level=current_level,
        next_level=next_level,
        progress_percentage=progress_percentage
    )


@router.get("/level-progress/{level_id}", response_model=LevelProgress)
def get_level_progress(
    level_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Belirli bir seviyedeki ilerlemeyi döner"""
    
    # Seviyeyi kontrol et
    level = db.query(LanguageLevel).filter(LanguageLevel.id == level_id).first()
    if not level:
        raise HTTPException(status_code=404, detail="Seviye bulunamadı")
    
    # Kullanıcının progress'ini bul
    user_progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.level_id == level_id
    ).first()
    
    if not user_progress:
        # Progress yoksa oluştur
        user_progress = UserProgress(
            user_id=current_user.id,
            level_id=level_id,
            is_unlocked=True if level_id == 1 else False
        )
        db.add(user_progress)
        db.commit()
        db.refresh(user_progress)
    
    # Seviyedeki toplam kelime sayısı
    total_words = db.query(Word).filter(Word.level_id == level_id).count()
    
    # Tamamlanan kelime sayısı
    completed_words = db.query(WordAttempt).filter(
        WordAttempt.user_progress_id == user_progress.id
    ).count()
    
    # Doğru cevaplanan kelime sayısı
    correct_words = db.query(WordAttempt).filter(
        WordAttempt.user_progress_id == user_progress.id,
        WordAttempt.is_correct == True
    ).count()
    
    incorrect_words = completed_words - correct_words
    accuracy_percentage = (correct_words / completed_words) * 100 if completed_words > 0 else 0
    
    return LevelProgress(
        level_id=level_id,
        level_name=level.level,
        total_words=total_words,
        completed_words=completed_words,
        correct_words=correct_words,
        incorrect_words=incorrect_words,
        accuracy_percentage=accuracy_percentage,
        is_completed=user_progress.is_completed,
        is_unlocked=user_progress.is_unlocked
    )


@router.get("/all-levels-progress", response_model=List[LevelProgress])
def get_all_levels_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Tüm seviyelerdeki ilerlemeyi döner"""
    
    levels = db.query(LanguageLevel).order_by(LanguageLevel.id).all()
    progress_list = []
    
    for level in levels:
        user_progress = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.level_id == level.id
        ).first()
        
        if not user_progress:
            # Progress yoksa oluştur
            user_progress = UserProgress(
                user_id=current_user.id,
                level_id=level.id,
                is_unlocked=True if level.id == 1 else False
            )
            db.add(user_progress)
            db.commit()
            db.refresh(user_progress)
        
        # Seviyedeki toplam kelime sayısı
        total_words = db.query(Word).filter(Word.level_id == level.id).count()
        
        # Tamamlanan kelime sayısı
        completed_words = db.query(WordAttempt).filter(
            WordAttempt.user_progress_id == user_progress.id
        ).count()
        
        # Doğru cevaplanan kelime sayısı
        correct_words = db.query(WordAttempt).filter(
            WordAttempt.user_progress_id == user_progress.id,
            WordAttempt.is_correct == True
        ).count()
        
        incorrect_words = completed_words - correct_words
        accuracy_percentage = (correct_words / completed_words) * 100 if completed_words > 0 else 0
        
        progress_list.append(LevelProgress(
            level_id=level.id,
            level_name=level.level,
            total_words=total_words,
            completed_words=completed_words,
            correct_words=correct_words,
            incorrect_words=incorrect_words,
            accuracy_percentage=accuracy_percentage,
            is_completed=user_progress.is_completed,
            is_unlocked=user_progress.is_unlocked
        ))
    
    return progress_list
