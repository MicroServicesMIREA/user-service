from fastapi import FastAPI
from .database import engine
from . import models
from .routers import users

# Создаем таблицы
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Service",
    description="Микросервис для управления пользователями",
    version="1.0.0"
)

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "User Service is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "user"}