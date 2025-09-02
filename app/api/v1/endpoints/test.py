from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from typing import Optional
from db.models.user import User
from sqlalchemy.orm import Session
from db.session import get_db
from core.config import settings
from pydantic import BaseModel
from db.models.language import Language


router = APIRouter()


def verify_test_api_key_query(api_key: Optional[str] = None):
    """
    Query parameter ile API key doğrulaması
    
    URL'de ?api_key=your_test_key_here şeklinde gönderilmeli
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key gerekli. Query parameter'da 'api_key' ile gönderin."
        )
    
    if api_key != settings.TEST_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz API key"
        )
    
    return True

@router.get("/user-list")
def user_list(db: Session = Depends(get_db), api_key: Optional[str] = Query(None, description="Test API key")):
    _ = verify_test_api_key_query(api_key)
    users = db.query(User).all()
    return {"users": users}


class LanguageCreate(BaseModel):
    name: str
    code: str

@router.post("/language/create")
def language_create(data: LanguageCreate, db: Session = Depends(get_db), api_key: Optional[str] = Query(None, description="Test API key")):
    _ = verify_test_api_key_query(api_key)
    language = Language(name=data.name, code=data.code)
    db.add(language)
    db.commit()
    db.refresh(language)
    return {"message": "Language created", "language": language}

@router.get("/language/list")
def language_list(db: Session = Depends(get_db), api_key: Optional[str] = Query(None, description="Test API key")):
    _ = verify_test_api_key_query(api_key)
    languages = db.query(Language).all()
    return {"message": "Language list", "languages": languages}