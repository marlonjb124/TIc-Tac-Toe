"""
Main API router that includes all endpoint routes.
"""

from fastapi import APIRouter

from app.api.routes import games, login, users

api_router = APIRouter()
api_router.include_router(login.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
