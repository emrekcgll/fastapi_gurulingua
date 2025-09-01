from fastapi import APIRouter
from api.v1.endpoints import test, auth, user

api_router = APIRouter()

# Test endpoints
api_router.include_router(test.router, prefix="/test", tags=["test"])

# Auth endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# User endpoints
api_router.include_router(user.router, prefix="/user", tags=["user"])

