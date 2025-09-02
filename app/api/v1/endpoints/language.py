from fastapi import APIRouter, Depends, Path
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from api.v1.dependencies.auth import get_current_user
from schemas.language import UserResponse
from db.models.user import User
from db.session import get_db
from db.models.language import Language

router = APIRouter()


@router.get("/list")
def language_list(db: Session = Depends(get_db)):
    """
    Tüm dilleri getirir
    """
    languages = db.query(Language).all()
    return {"message": "Language list", "languages": languages}


@router.patch(
    "/select/native_language/{native_language_id}/target_language/{target_language_id}",
    response_model=UserResponse
)
def select_language(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    native_language_id: int = Path(..., description="Native language ID"),
    target_language_id: int = Path(..., description="Target language ID"),
):
    """
    Kullanıcının anadil ve hedef dilini kaydetmek için anadil ve hedef dilin id'sini gönder
    """
    native_language = db.query(Language).filter(Language.id == native_language_id).first()
    target_language = db.query(Language).filter(Language.id == target_language_id).first()
    
    if not native_language or not target_language:
        raise HTTPException(status_code=404, detail="Language not found")

    current_user.native_language_id = native_language_id
    current_user.target_language_id = target_language_id
    db.commit()
    user_with_languages = db.query(User)\
        .options(
            joinedload(User.native_language),
            joinedload(User.target_language)
        )\
        .filter(User.id == current_user.id)\
        .first()
    return user_with_languages
