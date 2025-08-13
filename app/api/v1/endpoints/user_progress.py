from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.session import get_db
from db.models.user_progress import UserProgress as UserProgressModel
from db.models.language_level import LanguageLevel
from schemas.user_progress import UserProgress, UserProgressCreate, UserProgressUpdate, UserProgressWithLevel
from api.v1.dependencies.auth import get_current_user
from db.models.user import User

router = APIRouter()


@router.get("/", response_model=List[UserProgressWithLevel])
def get_user_progress_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """Kullanıcının tüm seviye ilerlemelerini listeler"""
    
    progress_list = db.query(UserProgressModel).filter(
        UserProgressModel.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    result = []
    for progress in progress_list:
        level = db.query(LanguageLevel).filter(LanguageLevel.id == progress.level_id).first()
        level_name = level.level if level else "Unknown"
        
        result.append(UserProgressWithLevel(
            **progress.__dict__,
            level_name=level_name
        ))
    
    return result


@router.get("/{progress_id}", response_model=UserProgressWithLevel)
def get_user_progress(
    progress_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Belirli bir ilerleme kaydını getirir"""
    
    progress = db.query(UserProgressModel).filter(
        UserProgressModel.id == progress_id,
        UserProgressModel.user_id == current_user.id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="İlerleme kaydı bulunamadı")
    
    level = db.query(LanguageLevel).filter(LanguageLevel.id == progress.level_id).first()
    level_name = level.level if level else "Unknown"
    
    return UserProgressWithLevel(
        **progress.__dict__,
        level_name=level_name
    )


@router.post("/", response_model=UserProgress)
def create_user_progress(
    progress: UserProgressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Yeni bir ilerleme kaydı oluşturur"""
    
    # Kullanıcı sadece kendi progress'ini oluşturabilir
    if progress.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sadece kendi ilerlemenizi oluşturabilirsiniz")
    
    # Aynı seviyede zaten progress var mı kontrol et
    existing_progress = db.query(UserProgressModel).filter(
        UserProgressModel.user_id == current_user.id,
        UserProgressModel.level_id == progress.level_id
    ).first()
    
    if existing_progress:
        raise HTTPException(status_code=400, detail="Bu seviyede zaten ilerleme kaydı mevcut")
    
    db_progress = UserProgressModel(**progress.dict())
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    
    return db_progress


@router.put("/{progress_id}", response_model=UserProgress)
def update_user_progress(
    progress_id: int,
    progress_update: UserProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """İlerleme kaydını günceller"""
    
    db_progress = db.query(UserProgressModel).filter(
        UserProgressModel.id == progress_id,
        UserProgressModel.user_id == current_user.id
    ).first()
    
    if not db_progress:
        raise HTTPException(status_code=404, detail="İlerleme kaydı bulunamadı")
    
    update_data = progress_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_progress, field, value)
    
    db.commit()
    db.refresh(db_progress)
    
    return db_progress


@router.delete("/{progress_id}")
def delete_user_progress(
    progress_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """İlerleme kaydını siler"""
    
    db_progress = db.query(UserProgressModel).filter(
        UserProgressModel.id == progress_id,
        UserProgressModel.user_id == current_user.id
    ).first()
    
    if not db_progress:
        raise HTTPException(status_code=404, detail="İlerleme kaydı bulunamadı")
    
    db.delete(db_progress)
    db.commit()
    
    return {"message": "İlerleme kaydı başarıyla silindi"}
