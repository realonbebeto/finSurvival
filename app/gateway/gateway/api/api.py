from fastapi import APIRouter

from gateway.api.endpoints import login, report

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(report.router, prefix="/reports", tags=["reports"])
