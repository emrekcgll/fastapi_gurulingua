from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from api.v1.dependencies.database import get_db
from api.v1.dependencies.auth import get_current_user
from crud.word import (
    get_words_by_level,
    get_words_by_level_id,
    get_total_words_by_level,
    get_available_words_for_user,
    get_level_info,
    get_all_levels_info
)
from crud.user_progress import get_user_level_completion
from db.models.user import User
from db.models.language_level import LevelName

router = APIRouter()


@router.get("/levels")
def get_all_levels(db: Session = Depends(get_db)):
    """
    Tüm dil seviyelerini ve kelime sayılarını getirir
    """
    levels = get_all_levels_info(db)
    return {"levels": levels}


@router.get("/levels/{level_name}")
def get_level_details(
    level_name: str,
    db: Session = Depends(get_db)
):
    """
    Belirli bir seviyenin detaylarını getirir
    """
    level_info = get_level_info(db, level_name.upper())
    if not level_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seviye '{level_name}' bulunamadı"
        )
    
    return level_info


@router.get("/levels/{level_name}/words")
def get_words_by_level_endpoint(
    level_name: str,
    skip: int = Query(0, ge=0, description="Atlanacak kayıt sayısı"),
    limit: int = Query(100, ge=1, le=1000, description="Maksimum kayıt sayısı"),
    db: Session = Depends(get_db)
):
    """
    Belirli seviyedeki tüm kelimeleri getirir (admin/öğretmen için)
    """
    # Seviye adını doğrula
    try:
        LevelName(level_name.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz seviye adı: {level_name}. Geçerli seviyeler: A1, A2, B1, B2, C1, C2"
        )
    
    words = get_words_by_level(db, level_name.upper(), skip, limit)
    total_words = get_total_words_by_level(db, level_name.upper())
    
    return {
        "level": level_name.upper(),
        "words": [
            {
                "id": word.id,
                "tr": word.tr,
                "en": word.en,
                "is_active": word.is_active
            }
            for word in words
        ],
        "total_words": total_words,
        "skip": skip,
        "limit": limit
    }


@router.get("/levels/{level_name}/words/available")
def get_available_words_for_user_endpoint(
    level_name: str,
    skip: int = Query(0, ge=0, description="Atlanacak kayıt sayısı"),
    limit: int = Query(100, ge=1, le=1000, description="Maksimum kayıt sayısı"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kullanıcının erişebileceği kelimeleri getirir (seviye kilitli ise boş liste döner)
    """
    # Seviye adını doğrula
    try:
        LevelName(level_name.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz seviye adı: {level_name}. Geçerli seviyeler: A1, A2, B1, B2, C1, C2"
        )
    
    # Kullanıcının seviye durumunu kontrol et
    level_info = get_level_info(db, level_name.upper())
    if not level_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seviye '{level_name}' bulunamadı"
        )
    
    level_completion = get_user_level_completion(db, current_user.id, level_info["id"])
    
    # Seviye kilitli ise sadece durum bilgisi döner
    if not level_completion["is_unlocked"]:
        return {
            "level": level_name.upper(),
            "words": [],
            "total_words": level_info["total_words"],
            "is_unlocked": False,
            "completion_percentage": level_completion["completion_percentage"],
            "required_percentage": 70.0,
            "message": f"A{level_name[1]} seviyesine erişmek için A{int(level_name[1])-1} seviyesinde %70 başarı gerekli"
        }
    
    # Seviye açıksa kelimeleri getir
    words = get_available_words_for_user(db, current_user.id, level_name.upper(), skip, limit)
    
    return {
        "level": level_name.upper(),
        "words": [
            {
                "id": word.id,
                "tr": word.tr,
                "en": word.en,
                "is_active": word.is_active
            }
            for word in words
        ],
        "total_words": level_info["total_words"],
        "is_unlocked": True,
        "completion_percentage": level_completion["completion_percentage"],
        "skip": skip,
        "limit": limit
    }


@router.get("/levels/{level_name}/progress")
def get_user_level_progress(
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
    level_info = get_level_info(db, level_name.upper())
    if not level_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seviye '{level_name}' bulunamadı"
        )
    
    # Kullanıcının seviye durumunu kontrol et
    level_completion = get_user_level_completion(db, current_user.id, level_info["id"])
    
    return {
        "level": level_name.upper(),
        "level_id": level_info["id"],
        "total_words": level_info["total_words"],
        "is_unlocked": level_completion["is_unlocked"],
        "completion_percentage": level_completion["completion_percentage"],
        "can_advance": level_completion["can_advance"],
        "total_attempts": level_completion["total_attempts"],
        "correct_attempts": level_completion["correct_attempts"],
        "required_percentage": 70.0,
        "next_level_unlocked": level_completion["is_unlocked"]
    }


@router.get("/my-progress")
def get_user_all_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kullanıcının tüm seviyelerdeki ilerleme durumunu getirir
    """
    from crud.user_progress import get_user_all_progress
    
    all_progress = get_user_all_progress(db, current_user.id)
    
    # Her seviye için detaylı bilgi ekle
    progress_details = []
    for progress in all_progress:
        level_info = get_level_info(db, progress.level.name.value)
        progress_details.append({
            "level": progress.level.name.value,
            "level_id": progress.level_id,
            "total_words": level_info["total_words"] if level_info else 0,
            "is_unlocked": progress.is_unlocked,
            "completion_percentage": progress.completion_percentage,
            "can_advance": progress.is_unlocked,
            "total_attempts": progress.total_attempts,
            "correct_attempts": progress.correct_attempts,
            "is_completed": progress.is_completed,
            "required_percentage": progress.required_percentage
        })
    
    return {
        "user_id": current_user.id,
        "progress": progress_details
    }


@router.get("/test")
def test_endpoint():
    """
    Test endpoint'i
    """
    return {"message": "Words endpoint çalışıyor!"}
