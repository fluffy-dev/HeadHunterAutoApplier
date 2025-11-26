from fastapi import APIRouter

from hh.user.user_router import router as user_router
from hh.auth.router import router as auth_router
from hh.vacancy.router import router as vacancy_router

router = APIRouter(prefix="/api")

router.include_router(user_router)
router.include_router(auth_router)
router.include_router(vacancy_router)

websocket_router = APIRouter()