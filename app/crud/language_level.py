from sqlalchemy.orm import Session
from db.models.language_level import LanguageLevel, LevelName


def get_all_levels(db: Session):
    """Tüm dil seviyelerini getirir"""
    return db.query(LanguageLevel).order_by(LanguageLevel.id).all()


def get_level_by_id(db: Session, level_id: int):
    """ID ile dil seviyesi getirir"""
    return db.query(LanguageLevel).filter(LanguageLevel.id == level_id).first()


def get_level_by_name(db: Session, level_name: str):
    """Ad ile dil seviyesi getirir"""
    return db.query(LanguageLevel).filter(LanguageLevel.name == level_name).first()


def create_level(db: Session, level_name: str):
    """Yeni dil seviyesi oluşturur"""
    try:
        # Level adını enum'a çevir
        level_enum = LevelName(level_name)
        level = LanguageLevel(name=level_enum)
        db.add(level)
        db.commit()
        db.refresh(level)
        return level
    except ValueError as e:
        print(f"Invalid level name: {level_name}")
        raise ValueError(f"Invalid level name: {level_name}. Valid levels: A1, A2, B1, B2, C1, C2")