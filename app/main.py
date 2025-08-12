from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.language_level import LanguageLevel
from db.models.word import Word
from db.models.sentence import Sentence
import pandas as pd
from api.v1.endpoints import language_level, sentence, word

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

app.include_router(
    language_level.router, prefix="/language-levels", tags=["language-levels"]
)
app.include_router(
    sentence.router, prefix="/sentences", tags=["sentences"]
)
app.include_router(
    word.router, prefix="/words", tags=["words"]
)

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
        
        # Batch işleme için sayaçlar
        processed_count = 0
        error_count = 0
        errors = []
        
        # Her satırı işle
        for index, row in df.iterrows():
            try:
                # LanguageLevel oluştur/kaydet
                language_level_db = db.query(LanguageLevel).filter(
                    LanguageLevel.level == row["level"]
                ).first()
                
                if not language_level_db:
                    language_level_db = LanguageLevel(level=row["level"])
                    db.add(language_level_db)
                    db.flush()  # ID'yi almak için flush kullan
                
                # Sentence oluştur/kaydet
                sentence_db = db.query(Sentence).filter(
                    Sentence.tr == row["sentence_tr"], 
                    Sentence.en == row["sentence_en"]
                ).first()
                
                if not sentence_db:
                    sentence_db = Sentence(
                        tr=row["sentence_tr"], 
                        en=row["sentence_en"]
                    )
                    db.add(sentence_db)
                    db.flush()  # ID'yi almak için flush kullan
                
                # Word oluştur/kaydet
                word_db = db.query(Word).filter(
                    Word.tr == row["tr"], 
                    Word.en == row["en"]
                ).first()
                
                if not word_db:
                    word_db = Word(
                        tr=row["tr"], 
                        en=row["en"], 
                        level_id=language_level_db.id, 
                        sentence_id=sentence_db.id
                    )
                    db.add(word_db)
                
                processed_count += 1
                
                # Her 100 satırda bir commit yap (batch processing)
                if processed_count % 100 == 0:
                    db.commit()
                
            except Exception as e:
                error_count += 1
                error_msg = f"Satır {index + 1} işlenirken hata: {str(e)}"
                errors.append(error_msg)
                continue
        
        # Kalan değişiklikleri commit et
        if processed_count > 0:
            db.commit()
        
        # Sonuç raporu
        result = {
            "message": "Data import işlemi tamamlandı",
            "total_rows": len(df),
            "processed_count": processed_count,
            "error_count": error_count,
            "errors": errors[:10] if errors else []  # Sadece ilk 10 hatayı göster
        }
        
        return result
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Excel dosyası boş")
    except ValueError as e:
        if "Excel file format cannot be determined" in str(e):
            raise HTTPException(status_code=400, detail="Excel dosya formatı tanınamadı. Lütfen .xlsx veya .xls formatında dosya yükleyin.")
        else:
            raise HTTPException(status_code=400, detail=f"Excel dosyası okunamadı: {str(e)}")
    except Exception as e:
        db.rollback()
        error_msg = f"Import işlemi sırasında beklenmeyen hata: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)
