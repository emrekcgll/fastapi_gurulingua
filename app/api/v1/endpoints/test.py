from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from typing import Optional
from db.models.user import User
from sqlalchemy.orm import Session
from db.session import get_db
from core.config import settings

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