from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from api.v1.dependencies.database import get_db
from api.v1.dependencies.auth import get_current_user
from core.security import create_access_token, create_refresh_token
from core.config import settings
from crud.user import authenticate_user, create_user, update_user_last_login, get_user_by_email
from schemas.auth import UserLogin, UserRegister, Token, UserResponse, UserUpdate, PasswordChange, GoogleLogin
from db.models.user import User
from core.google_auth import GoogleAuthService

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Yeni kullanıcı kaydı
    """
    # Email zaten var mı kontrol et
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email adresi zaten kayıtlı"
        )
    
    # Yeni kullanıcı oluştur
    user = create_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        name=user_data.name
    )
    
    return user

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Kullanıcı girişi ve token oluşturma
    """
    # Kullanıcıyı doğrula
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hatalı email veya şifre",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Kullanıcının aktif olup olmadığını kontrol et
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pasif kullanıcı"
        )
    
    # Son giriş zamanını güncelle
    update_user_last_login(db, user.id)
    
    # Token'ları oluştur
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh token ile yeni access token oluşturma
    """
    from core.security import verify_token
    
    # Refresh token'ı doğrula
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz refresh token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz kullanıcı"
        )
    
    # Yeni token'ları oluştur
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    new_refresh_token_expires = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    new_access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=new_refresh_token_expires
    )
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

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

@router.post("/google/login", response_model=Token)
def google_login(
    google_data: GoogleLogin,
    db: Session = Depends(get_db)
):
    """
    Google ID token ile giriş yapma (Android için)
    Hem giriş hem kayıt işlemini yapar
    """
    try:
        # Google ID token'ını doğrula
        google_user_info = GoogleAuthService.verify_google_token(google_data.id_token)
        
        # Kullanıcı zaten var mı kontrol et
        user = get_user_by_email(db, google_user_info['email'])
        is_new_user = False
        
        if not user:
            # Yeni kullanıcı oluştur
            user = create_user(
                db=db,
                email=google_user_info['email'],
                password=None,  # Google kullanıcıları için şifre yok
                name=google_user_info['name']
            )
            is_new_user = True
        else:
            # Mevcut kullanıcının son giriş zamanını güncelle
            update_user_last_login(db, user.id)
        
        # Token'ları oluştur
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=refresh_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google token doğrulama hatası: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Giriş hatası: {str(e)}"
        )
