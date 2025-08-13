from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from api.v1.dependencies.database import get_db
from api.v1.dependencies.auth import get_current_user
from crud import language_level as crud
from schemas.language_level import LanguageLevel
from db.models.user import User

router = APIRouter()


@router.get("/", response_model=List[LanguageLevel])
def get_language_levels(
    db: Session = Depends(get_db), 
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Tüm dil seviyelerini getirir - Kimlik doğrulama gerekli"""
    return crud.get_all_language_levels(db, skip, limit)


@router.get("/{level_id}", response_model=LanguageLevel)
def get_language_level(
    level_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ID'ye göre belirli bir dil seviyesini getirir - Kimlik doğrulama gerekli"""
    language_level = crud.get_language_level(db, level_id)
    if not language_level:
        raise HTTPException(status_code=404, detail="Dil seviyesi bulunamadı")
    return language_level
