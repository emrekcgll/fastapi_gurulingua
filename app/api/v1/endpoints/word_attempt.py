from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.session import get_db
from db.models.word_attempt import WordAttempt as WordAttemptModel
from db.models.word import Word
from db.models.language_level import LanguageLevel
from schemas.word_attempt import WordAttempt, WordAttemptCreate, WordAttemptUpdate, WordAttemptWithWord
from api.v1.dependencies.auth import get_current_user
from db.models.user import User

router = APIRouter()


@router.get("/", response_model=List[WordAttemptWithWord])
def get_word_attempts_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """Kullanıcının tüm kelime denemelerini listeler"""
    
    attempts = db.query(WordAttemptModel).filter(
        WordAttemptModel.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    result = []
    for attempt in attempts:
        word = db.query(Word).filter(Word.id == attempt.word_id).first()
        if word:
            level = db.query(LanguageLevel).filter(LanguageLevel.id == word.level_id).first()
            level_name = level.level if level else "Unknown"
            
            result.append(WordAttemptWithWord(
                **attempt.__dict__,
                word_tr=word.tr,
                word_en=word.en,
                level_name=level_name
            ))
    
    return result


@router.get("/{attempt_id}", response_model=WordAttemptWithWord)
def get_word_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Belirli bir kelime denemesini getirir"""
    
    attempt = db.query(WordAttemptModel).filter(
        WordAttemptModel.id == attempt_id,
        WordAttemptModel.user_id == current_user.id
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Kelime denemesi bulunamadı")
    
    word = db.query(Word).filter(Word.id == attempt.word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Kelime bulunamadı")
    
    level = db.query(LanguageLevel).filter(LanguageLevel.id == word.level_id).first()
    level_name = level.level if level else "Unknown"
    
    return WordAttemptWithWord(
        **attempt.__dict__,
        word_tr=word.tr,
        word_en=word.en,
        level_name=level_name
    )


@router.post("/", response_model=WordAttempt)
def create_word_attempt(
    attempt: WordAttemptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Yeni bir kelime denemesi oluşturur"""
    
    # Kullanıcı sadece kendi denemelerini oluşturabilir
    if attempt.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sadece kendi denemelerinizi oluşturabilirsiniz")
    
    db_attempt = WordAttemptModel(**attempt.dict())
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    
    return db_attempt


@router.put("/{attempt_id}", response_model=WordAttempt)
def update_word_attempt(
    attempt_id: int,
    attempt_update: WordAttemptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kelime denemesini günceller"""
    
    db_attempt = db.query(WordAttemptModel).filter(
        WordAttemptModel.id == attempt_id,
        WordAttemptModel.user_id == current_user.id
    ).first()
    
    if not db_attempt:
        raise HTTPException(status_code=404, detail="Kelime denemesi bulunamadı")
    
    update_data = attempt_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_attempt, field, value)
    
    db.commit()
    db.refresh(db_attempt)
    
    return db_attempt


@router.delete("/{attempt_id}")
def delete_word_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kelime denemesini siler"""
    
    db_attempt = db.query(WordAttemptModel).filter(
        WordAttemptModel.id == attempt_id,
        WordAttemptModel.user_id == current_user.id
    ).first()
    
    if not db_attempt:
        raise HTTPException(status_code=404, detail="Kelime denemesi bulunamadı")
    
    db.delete(db_attempt)
    db.commit()
    
    return {"message": "Kelime denemesi başarıyla silindi"}


@router.get("/by-level/{level_id}", response_model=List[WordAttemptWithWord])
def get_word_attempts_by_level(
    level_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """Belirli bir seviyedeki kelime denemelerini listeler"""
    
    # Önce o seviyedeki kelimeleri bul
    words = db.query(Word).filter(Word.level_id == level_id).all()
    word_ids = [word.id for word in words]
    
    if not word_ids:
        return []
    
    # O kelimelerle yapılan denemeleri getir
    attempts = db.query(WordAttemptModel).filter(
        WordAttemptModel.user_id == current_user.id,
        WordAttemptModel.word_id.in_(word_ids)
    ).offset(skip).limit(limit).all()
    
    result = []
    for attempt in attempts:
        word = db.query(Word).filter(Word.id == attempt.word_id).first()
        if word:
            level = db.query(LanguageLevel).filter(LanguageLevel.id == word.level_id).first()
            level_name = level.level if level else "Unknown"
            
            result.append(WordAttemptWithWord(
                **attempt.__dict__,
                word_tr=word.tr,
                word_en=word.en,
                level_name=level_name
            ))
    
    return result


@router.get("/correct-words", response_model=List[WordAttemptWithWord])
def get_correct_word_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """Kullanıcının doğru bildiği kelimeleri listeler"""
    
    attempts = db.query(WordAttemptModel).filter(
        WordAttemptModel.user_id == current_user.id,
        WordAttemptModel.is_correct == True
    ).offset(skip).limit(limit).all()
    
    result = []
    for attempt in attempts:
        word = db.query(Word).filter(Word.id == attempt.word_id).first()
        if word:
            level = db.query(LanguageLevel).filter(LanguageLevel.id == word.level_id).first()
            level_name = level.level if level else "Unknown"
            
            result.append(WordAttemptWithWord(
                **attempt.__dict__,
                word_tr=word.tr,
                word_en=word.en,
                level_name=level_name
            ))
    
    return result


@router.get("/incorrect-words", response_model=List[WordAttemptWithWord])
def get_incorrect_word_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """Kullanıcının yanlış bildiği kelimeleri listeler"""
    
    attempts = db.query(WordAttemptModel).filter(
        WordAttemptModel.user_id == current_user.id,
        WordAttemptModel.is_correct == False
    ).offset(skip).limit(limit).all()
    
    result = []
    for attempt in attempts:
        word = db.query(Word).filter(Word.id == attempt.word_id).first()
        if word:
            level = db.query(LanguageLevel).filter(LanguageLevel.id == word.level_id).first()
            level_name = level.level if level else "Unknown"
            
            result.append(WordAttemptWithWord(
                **attempt.__dict__,
                word_tr=word.tr,
                word_en=word.en,
                level_name=level_name
            ))
    
    return result
