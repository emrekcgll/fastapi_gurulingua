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


from db.session import get_db
from fastapi import Depends, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
from crud.language_level import get_level_by_name, create_level
from crud.word import create_word, get_word_by_word_tr

@app.post("/import-data")
def import_data(db: Session = Depends(get_db), file: UploadFile = File(...)):
    df = pd.read_excel(file.file)
    for index, row in df.iterrows():
        word_tr = row['tr']
        word_en = row['en']
        level = row['level']

        level_id = get_level_by_name(db, level)
        if not level_id:
            level_id = create_level(db, level)

        word = get_word_by_word_tr(db, word_tr)
        if not word:
            word = create_word(db, word_tr, word_en, level_id)

    return {"message": "Data imported successfully"}