"""Central API router — aggregates all sub-routers."""

from fastapi import APIRouter
from app.api.auth import router as auth_router

api_router = APIRouter()

# Register sub-routers
api_router.include_router(auth_router)

# Additional routers will be added in subsequent phases:
# - datasets_router  → /datasets
# - etl_router       → /etl
# - ml_router        → /ml
# - predictions_router → /predictions
# - insights_router  → /insights
# - reports_router   → /reports


@api_router.get("/")
async def api_root():
    """API root — list available endpoint groups."""
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
