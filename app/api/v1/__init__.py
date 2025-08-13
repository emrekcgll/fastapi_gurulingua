from fastapi import APIRouter
from api.v1.endpoints import auth, word, sentence, language_level

api_router = APIRouter()

# Auth endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Word endpoints
api_router.include_router(word.router, prefix="/words", tags=["words"])

# Sentence endpoints
api_router.include_router(sentence.router, prefix="/sentences", tags=["sentences"])

# Language level endpoints
api_router.include_router(language_level.router, prefix="/language-levels", tags=["language-levels"])
