from fastapi import APIRouter
from app.presentation.api.v1.endpoints.auth import router as auth_router


v1_router = APIRouter(prefix="/v1")
v1_router.include_router(auth_router, prefix="/auth", tags=["auth"])
