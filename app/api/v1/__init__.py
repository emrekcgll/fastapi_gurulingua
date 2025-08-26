from fastapi import APIRouter
from api.v1.endpoints import auth, words, word_attempts, language_levels, user_progress

api_router = APIRouter()

# Auth endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Word endpoints
api_router.include_router(words.router, prefix="/words", tags=["words"])

# Word attempt endpoints
api_router.include_router(word_attempts.router, prefix="/words", tags=["word_attempts"])

# Language level endpoints
api_router.include_router(language_levels.router, prefix="/language-levels", tags=["language_levels"])

# User progress endpoints
api_router.include_router(user_progress.router, prefix="/user-progress", tags=["user_progress"])