from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from api.v1.dependencies.database import get_db
from api.v1.dependencies.auth import get_current_user
from crud.language_level import get_all_levels, get_level_by_id, get_level_by_name
from crud.word import get_total_words_by_level_id
from db.models.user import User
from db.models.language_level import LevelName

router = APIRouter()


@router.get("/")
def get_all_language_levels(db: Session = Depends(get_db)):
    """
    Tüm dil seviyelerini getirir
    """
    levels = get_all_levels(db)
    
    # Her seviye için kelime sayısını ekle
    levels_with_word_count = []
    for level in levels:
        word_count = get_total_words_by_level_id(db, level.id)
        levels_with_word_count.append({
            "id": level.id,
            "name": level.name.value,
            "total_words": word_count,
            "is_active": True
        })
    
    return {"levels": levels_with_word_count}


@router.get("/{level_name}")
def get_language_level_by_name(
    level_name: str,
    db: Session = Depends(get_db)
):
    """
    Belirli bir seviyeyi adına göre getirir
    """
    # Seviye adını doğrula
    try:
        LevelName(level_name.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz seviye adı: {level_name}. Geçerli seviyeler: A1, A2, B1, B2, C1, C2"
        )
    
    level = get_level_by_name(db, level_name.upper())
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seviye '{level_name}' bulunamadı"
        )
    
    word_count = get_total_words_by_level_id(db, level.id)
    
    return {
        "id": level.id,
        "name": level.name.value,
        "total_words": word_count,
        "is_active": True
    }


@router.get("/{level_name}/words")
def get_level_words(
    level_name: str,
    skip: int = Query(0, ge=0, description="Atlanacak kayıt sayısı"),
    limit: int = Query(100, ge=1, le=1000, description="Maksimum kayıt sayısı"),
    db: Session = Depends(get_db)
):
    """
    Belirli seviyedeki tüm kelimeleri getirir
    """
    from crud.word import get_words_by_level, get_total_words_by_level
    
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


@router.get("/{level_name}/stats")
def get_level_statistics(
    level_name: str,
    db: Session = Depends(get_db)
):
    """
    Belirli seviye için genel istatistikleri getirir
    """
    from crud.word import get_total_words_by_level
    from crud.user_progress import get_level_completion_stats
    
    # Seviye adını doğrula
    try:
        LevelName(level_name.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz seviye adı: {level_name}. Geçerli seviyeler: A1, A2, B1, B2, C1, C2"
        )
    
    total_words = get_total_words_by_level(db, level_name.upper())
    completion_stats = get_level_completion_stats(db, level_name.upper())
    
    return {
        "level": level_name.upper(),
        "total_words": total_words,
        "completion_stats": completion_stats
    }


@router.get("/test")
def test_endpoint():
    """
    Test endpoint'i
    """
    return {"message": "Language levels endpoint çalışıyor!"}
