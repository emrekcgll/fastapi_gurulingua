from fastapi import FastAPI
from api.v1.endpoints import user


app = FastAPI()
app.include_router(user.router, prefix="/api/v1/users", tags=["users"])


@app.get("/")
def root():
    return {"message": "Hello from Gurulingua FastAPI Backend!"}
