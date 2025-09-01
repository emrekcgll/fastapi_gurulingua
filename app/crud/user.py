from sqlalchemy.orm import Session
from db.models.user import User, UserProvider, UserRole
from core.security import get_password_hash, verify_password
from typing import Optional


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """ID ile kullanıcı getirir"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Email ile kullanıcı getirir"""
    return db.query(User).filter(User.email == email).first()


def create_user(
    db: Session,
    email: str,
    password: str = None,
    name: str = None,
    provider: UserProvider = UserProvider.LOCAL,
    role: UserRole = UserRole.USER,
) -> User:
    """Yeni kullanıcı oluşturur"""
    hashed_password = get_password_hash(password) if password else None
    db_user = User(
        email=email,
        hashed_password=hashed_password,
        name=name,
        provider=provider,
        role=role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Kullanıcı kimlik doğrulaması yapar"""
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user_last_login(db: Session, user_id: int):
    """Kullanıcının son giriş zamanını günceller"""
    user = get_user_by_id(db, user_id=user_id)
    if user:
        from datetime import datetime

        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)


def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
    """Kullanıcı bilgilerini günceller"""
    user = get_user_by_id(db, user_id=user_id)
    if user:
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
    return user
