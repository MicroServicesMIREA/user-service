from fastapi import FastAPI, Response
from .database import engine
from . import models
from .routers import users
from .middleware import MetricsMiddleware
from .metrics import get_metrics
from .logging_config import setup_logging
import logging

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Service",
    description="Микросервис для управления пользователями",
    version="1.0.0"
)

# Добавляем middleware для сбора метрик
app.add_middleware(MetricsMiddleware)

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "User Service is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "user"}

@app.get("/metrics")
def metrics():
    return Response(content=get_metrics(), media_type="text/plain")