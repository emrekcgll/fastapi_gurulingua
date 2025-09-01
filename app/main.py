from fastapi import FastAPI
from api.v1 import api_router

app = FastAPI(
    title="Gurulingua FastAPI Backend",
    description="Gurulingua FastAPI Backend",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["*"],
    allow_credentials=True,
)

app.include_router(api_router, prefix="/api/v1")

