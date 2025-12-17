from app.routers.router import api_router
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, get_db
from . import models
from .routers import api_router
from .config import settings

# Crear las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    description="API para sistema de punto de venta (POS) con gestión de usuarios, productos y transacciones",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins if not settings.debug else ["*"],
    allow_credentials=True,
    allow_methods=settings.allowed_methods if not settings.debug else ["*"],
    allow_headers=settings.allowed_headers if not settings.debug else ["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.api_v1_str) 
        


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
