from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from api.v1.dependencies.database import get_db
from api.v1.dependencies.auth import get_current_user
from crud.user_progress import (
    get_user_all_progress,
    get_user_progress_by_level,
    get_user_level_completion,
    reset_user_level_progress,
    unlock_user_level
)
from crud.word import get_total_words_by_level_id
from db.models.user import User
from db.models.language_level import LevelName

router = APIRouter()


@router.get("/my-progress")
def get_my_all_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kullanıcının tüm seviyelerdeki ilerleme durumunu getirir
    """
    all_progress = get_user_all_progress(db, current_user.id)
    
    # Her seviye için detaylı bilgi ekle
    progress_details = []
    for progress in all_progress:
        level_info = {
            "id": progress.level.id,
            "name": progress.level.name.value
        }
        
        total_words = get_total_words_by_level_id(db, progress.level_id)
        
        progress_details.append({
            "level": progress.level.name.value,
            "level_id": progress.level_id,
            "total_words": total_words,
            "is_unlocked": progress.is_unlocked,
            "completion_percentage": progress.completion_percentage,
            "can_advance": progress.is_unlocked,
            "total_attempts": progress.total_attempts,
            "correct_attempts": progress.correct_attempts,
            "is_completed": progress.is_completed,
            "required_percentage": progress.required_percentage,
            "created_at": progress.created_at.isoformat() if progress.created_at else None,
            "updated_at": progress.updated_at.isoformat() if progress.updated_at else None
        })
    
    return {
        "user_id": current_user.id,
        "user_email": current_user.email,
        "progress": progress_details
    }


@router.get("/my-progress/{level_name}")
def get_my_level_progress(
    level_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kullanıcının belirli seviyedeki ilerleme durumunu getirir
    """
    # Seviye adını doğrula
    try:
        LevelName(level_name.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz seviye adı: {level_name}. Geçerli seviyeler: A1, A2, B1, B2, C1, C2"
        )
    
    # Seviye bilgisini al
    from crud.language_level import get_level_by_name
    level = get_level_by_name(db, level_name.upper())
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seviye '{level_name}' bulunamadı"
        )
    
    # Kullanıcının seviye durumunu kontrol et
    level_completion = get_user_level_completion(db, current_user.id, level.id)
    total_words = get_total_words_by_level_id(db, level.id)
    
    return {
        "user_id": current_user.id,
        "level": level_name.upper(),
        "level_id": level.id,
        "total_words": total_words,
        "is_unlocked": level_completion["is_unlocked"],
        "completion_percentage": level_completion["completion_percentage"],
        "can_advance": level_completion["is_unlocked"],
        "total_attempts": level_completion["total_attempts"],
        "correct_attempts": level_completion["correct_attempts"],
        "required_percentage": 70.0,
        "next_level_unlocked": level_completion["is_unlocked"],
        "remaining_words": max(0, total_words - level_completion["correct_attempts"]),
        "words_to_unlock": max(0, int(total_words * 0.7) - level_completion["correct_attempts"])
    }


@router.get("/my-progress/{level_name}/detailed")
def get_my_level_progress_detailed(
    level_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kullanıcının belirli seviyedeki detaylı ilerleme durumunu getirir
    """
    # Seviye adını doğrula
    try:
        LevelName(level_name.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz seviye adı: {level_name}. Geçerli seviyeler: A1, A2, B1, B2, C1, C2"
        )
    
    # Seviye bilgisini al
    from crud.language_level import get_level_by_name
    level = get_level_by_name(db, level_name.upper())
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seviye '{level_name}' bulunamadı"
        )
    
    # Kullanıcının seviye durumunu kontrol et
    user_progress = get_user_progress_by_level(db, current_user.id, level.id)
    if not user_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bu seviye için ilerleme kaydı bulunamadı"
        )
    
    total_words = get_total_words_by_level_id(db, level.id)
    
    return {
        "user_id": current_user.id,
        "level": level_name.upper(),
        "level_id": level.id,
        "total_words": total_words,
        "is_unlocked": user_progress.is_unlocked,
        "completion_percentage": user_progress.completion_percentage,
        "can_advance": user_progress.is_unlocked,
        "total_attempts": user_progress.total_attempts,
        "correct_attempts": user_progress.correct_attempts,
        "is_completed": user_progress.is_completed,
        "required_percentage": user_progress.required_percentage,
        "remaining_words": max(0, total_words - user_progress.correct_attempts),
        "words_to_unlock": max(0, int(total_words * 0.7) - user_progress.correct_attempts),
        "created_at": user_progress.created_at.isoformat() if user_progress.created_at else None,
        "updated_at": user_progress.updated_at.isoformat() if user_progress.updated_at else None,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }


@router.post("/my-progress/{level_name}/reset")
def reset_my_level_progress(
    level_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kullanıcının belirli seviyedeki ilerlemesini sıfırlar
    """
    # Seviye adını doğrula
    try:
        LevelName(level_name.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz seviye adı: {level_name}. Geçerli seviyeler: A1, A2, B1, B2, C1, C2"
        )
    
    # Seviye bilgisini al
    from crud.language_level import get_level_by_name
    level = get_level_by_name(db, level_name.upper())
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seviye '{level_name}' bulunamadı"
        )
    
    # İlerlemeyi sıfırla
    success = reset_user_level_progress(db, current_user.id, level.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bu seviye için ilerleme kaydı bulunamadı"
        )
    
    return {
        "message": f"{level_name} seviyesi ilerlemesi başarıyla sıfırlandı",
        "level": level_name.upper(),
        "user_id": current_user.id
    }


@router.get("/my-progress/summary")
def get_my_progress_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kullanıcının ilerleme özetini getirir
    """
    all_progress = get_user_all_progress(db, current_user.id)
    
    total_levels = len(all_progress)
    unlocked_levels = sum(1 for p in all_progress if p.is_unlocked)
    completed_levels = sum(1 for p in all_progress if p.is_completed)
    
    total_attempts = sum(p.total_attempts for p in all_progress)
    total_correct = sum(p.correct_attempts for p in all_progress)
    
    overall_success_rate = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
    
    # Seviye bazında özet
    level_summary = []
    for progress in all_progress:
        level_summary.append({
            "level": progress.level.name.value,
            "is_unlocked": progress.is_unlocked,
            "is_completed": progress.is_completed,
            "completion_percentage": progress.completion_percentage,
            "status": "completed" if progress.is_completed else "in_progress" if progress.is_unlocked else "locked"
        })
    
    return {
        "user_id": current_user.id,
        "user_email": current_user.email,
        "summary": {
            "total_levels": total_levels,
            "unlocked_levels": unlocked_levels,
            "completed_levels": completed_levels,
            "locked_levels": total_levels - unlocked_levels,
            "total_attempts": total_attempts,
            "total_correct": total_correct,
            "overall_success_rate": round(overall_success_rate, 2)
        },
        "level_summary": level_summary
    }


@router.get("/test")
def test_endpoint():
    """
    Test endpoint'i
    """
    return {"message": "User progress endpoint çalışıyor!"}
