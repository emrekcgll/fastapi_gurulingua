from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.language_level import LanguageLevel
from db.models.word import Word
from db.models.sentence import Sentence
import pandas as pd
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
    allow_credentials=True,
)

app.include_router(api_router, prefix="/api/v1")


@app.post("/import-data")
def import_data(db: Session = Depends(get_db), file: UploadFile = File(...)):
    """
    Excel dosyasından veri import etme fonksiyonu
    Gerekli kolonlar: level, sentence_tr, sentence_en, tr, en
    """
    
    # Dosya tipi kontrolü
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Sadece Excel dosyaları (.xlsx, .xls) kabul edilir")
    
    try:
        # Excel dosyasını oku
        df = pd.read_excel(file.file)
        
        # Gerekli kolonları kontrol et
        required_columns = ["level", "sentence_tr", "sentence_en", "tr", "en"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Excel dosyasında gerekli kolonlar eksik: {missing_columns}"
            )
        
        # Boş değerleri temizle
        df = df.dropna(subset=required_columns)
        
        errors = []
        for index, row in df.iterrows():
            language_level_db = db.query(LanguageLevel).filter(LanguageLevel.level == row["level"]).first()
            if not language_level_db:
                language_level_db = LanguageLevel(level=row["level"])
                db.add(language_level_db)
                db.flush()  # ID'yi almak için flush 
            
            sentence_db = db.query(Sentence).filter(Sentence.tr == row["sentence_tr"], Sentence.en == row["sentence_en"]).first()
            if not sentence_db:
                sentence_db = Sentence(
                    tr=row["sentence_tr"], 
                    en=row["sentence_en"]
                )
                db.add(sentence_db)
                db.flush()  # ID'yi almak için flush kullan
            
            word_db = db.query(Word).filter(Word.tr == row["tr"], Word.en == row["en"]).first()
            if not word_db:
                word_db = Word(
                    tr=row["tr"], 
                    en=row["en"], 
                    level_id=language_level_db.id, 
                    sentence_id=sentence_db.id
                )
                db.add(word_db)
                
            db.commit()
                
        
        result = {
            "message": "Data import işlemi tamamlandı",
            "total_rows": len(df),
            "errors": errors if errors else []
        }
        return result

    except Exception as e:
        db.rollback()
        error_msg = f"Import işlemi sırasında beklenmeyen hata: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)
