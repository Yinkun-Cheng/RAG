"""API Router"""

from fastapi import APIRouter
from .endpoints import router as endpoints_router

router = APIRouter()

# Include endpoints router
router.include_router(endpoints_router)
