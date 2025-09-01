from fastapi import APIRouter, Depends, HTTPException, status
from db.models.user import User
from api.v1.dependencies.auth import get_current_user
from db.session import get_db
from sqlalchemy.orm import Session
from schemas.auth import UserResponse
from schemas.user import PasswordChange, UserUpdate

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Mevcut kullanıcı bilgilerini getirir
    """
    return current_user

@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mevcut kullanıcı bilgilerini günceller
    """
    from crud.user import update_user
    
    updated_user = update_user(
        db=db,
        user_id=current_user.id,
        **user_data.dict(exclude_unset=True)
    )
    
    return updated_user

@router.post("/change-password")
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kullanıcı şifresini değiştirir
    """
    from core.security import verify_password, get_password_hash
    
    # Mevcut şifreyi doğrula
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mevcut şifre hatalı"
        )
    
    # Yeni şifreyi hashle ve güncelle
    new_hashed_password = get_password_hash(password_data.new_password)
    from crud.user import update_user
    update_user(db=db, user_id=current_user.id, hashed_password=new_hashed_password)
    
    return {"message": "Şifre başarıyla değiştirildi"}