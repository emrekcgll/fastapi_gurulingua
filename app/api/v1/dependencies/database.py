from db.session import get_db

# Database session dependency'si
def get_db_session():
    return get_db()
