from fastapi import APIRouter
from api.v1.endpoints import auth, word, sentence, language_level, game, user_progress, word_attempt

api_router = APIRouter()

# Auth endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Word endpoints
api_router.include_router(word.router, prefix="/words", tags=["words"])

# Sentence endpoints
api_router.include_router(sentence.router, prefix="/sentences", tags=["sentences"])

# Language level endpoints
api_router.include_router(language_level.router, prefix="/language-levels", tags=["language-levels"])

# Game endpoints
api_router.include_router(game.router, prefix="/game", tags=["game"])

# User progress endpoints
api_router.include_router(user_progress.router, prefix="/user-progress", tags=["user-progress"])

# Word attempt endpoints
api_router.include_router(word_attempt.router, prefix="/word-attempts", tags=["word-attempts"])
