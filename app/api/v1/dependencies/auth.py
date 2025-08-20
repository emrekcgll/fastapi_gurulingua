from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.security import verify_token
from api.v1.dependencies.database import get_db
from db.models.user import User, UserRole
from crud.user import get_user_by_id

# HTTP Bearer token scheme
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    JWT token'dan mevcut kullanıcıyı getirir
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Token'ı doğrula
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        # Token tipini kontrol et (access token olmalı)
        if payload.get("type") != "access":
            raise credentials_exception
        
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    # Kullanıcıyı veritabanından getir
    user = get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    
    # Kullanıcının aktif olup olmadığını kontrol et
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Mevcut aktif kullanıcıyı getirir
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_superadmin(current_user: User = Depends(get_current_user)) -> User:
    """
    Mevcut superadmin kullanıcıyı getirir
    """
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def get_current_user_or_none(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User | None:
    """
    JWT token'dan kullanıcıyı getirir, token yoksa None döner
    """
    try:
        payload = verify_token(credentials.credentials)
        if payload is None or payload.get("type") != "access":
            return None
        
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
            
        user = get_user_by_id(db, user_id=user_id)
        if user is None or not user.is_active:
            return None
            
        return user
    except Exception:
        return None
