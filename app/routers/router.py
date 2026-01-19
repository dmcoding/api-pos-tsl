from fastapi import APIRouter
from app.routers import transactions
api_router = APIRouter()

api_router.include_router(transactions.router, prefix="/convert-transaction")