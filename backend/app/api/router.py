from fastapi import APIRouter

api_router = APIRouter()

# Placeholder route — sub-routers will be added in subsequent phases
@api_router.get("/")
async def api_root():
    return {
        "message": "Predictive Analytics Platform API v1",
        "endpoints": [
            "/api/v1/auth",
            "/api/v1/datasets",
            "/api/v1/etl",
            "/api/v1/ml",
            "/api/v1/predictions",
            "/api/v1/insights",
            "/api/v1/reports",
        ],
    }
