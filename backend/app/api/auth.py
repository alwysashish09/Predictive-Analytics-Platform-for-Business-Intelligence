"""Authentication API endpoints — signup, login, logout, profile."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from app.database import get_supabase
from app.middleware.auth import get_current_user
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Request / Response Schemas ───────────────────────────────

class SignUpRequest(BaseModel):
    email: str
    password: str
    full_name: str = ""


class SignInRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    success: bool
    message: str
    user: dict | None = None
    session: dict | None = None


class ProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str | None = None
    avatar_url: str | None = None


class UpdateProfileRequest(BaseModel):
    full_name: str | None = None
    avatar_url: str | None = None


# ── Endpoints ────────────────────────────────────────────────

@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    """Register a new user with email and password."""
    supabase = get_supabase()
    if supabase is None:
        raise HTTPException(status_code=503, detail="Auth service unavailable.")

    try:
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name,
                }
            }
        })

        if response.user is None:
            raise HTTPException(status_code=400, detail="Signup failed.")

        return AuthResponse(
            success=True,
            message="Account created successfully. Please check your email for verification.",
            user={
                "id": str(response.user.id),
                "email": response.user.email,
                "full_name": request.full_name,
            },
            session={
                "access_token": response.session.access_token if response.session else None,
                "refresh_token": response.session.refresh_token if response.session else None,
            } if response.session else None,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def login(request: SignInRequest):
    """Authenticate with email and password."""
    supabase = get_supabase()
    if supabase is None:
        raise HTTPException(status_code=503, detail="Auth service unavailable.")

    try:
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password,
        })

        if response.user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials.")

        return AuthResponse(
            success=True,
            message="Login successful.",
            user={
                "id": str(response.user.id),
                "email": response.user.email,
                "full_name": response.user.user_metadata.get("full_name", ""),
            },
            session={
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "expires_at": response.session.expires_at,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid email or password.")


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Sign out the current user."""
    supabase = get_supabase()
    if supabase is None:
        raise HTTPException(status_code=503, detail="Auth service unavailable.")

    try:
        supabase.auth.sign_out()
        return {"success": True, "message": "Logged out successfully."}
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        # Even if server-side logout fails, client should clear its token
        return {"success": True, "message": "Logged out."}


@router.get("/me", response_model=ProfileResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    supabase = get_supabase()

    try:
        # Fetch full profile from profiles table
        result = supabase.table("profiles").select("*").eq(
            "id", current_user["id"]
        ).single().execute()

        if result.data:
            return ProfileResponse(
                id=result.data["id"],
                email=result.data["email"],
                full_name=result.data.get("full_name"),
                avatar_url=result.data.get("avatar_url"),
            )

        # Fallback to auth user data
        return ProfileResponse(
            id=current_user["id"],
            email=current_user["email"],
            full_name=current_user.get("full_name"),
        )
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return ProfileResponse(
            id=current_user["id"],
            email=current_user["email"],
            full_name=current_user.get("full_name"),
        )


@router.put("/me", response_model=ProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
):
    """Update the current user's profile."""
    supabase = get_supabase()

    try:
        update_data = {}
        if request.full_name is not None:
            update_data["full_name"] = request.full_name
        if request.avatar_url is not None:
            update_data["avatar_url"] = request.avatar_url

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update.")

        result = supabase.table("profiles").update(
            update_data
        ).eq("id", current_user["id"]).execute()

        data = result.data[0] if result.data else {}
        return ProfileResponse(
            id=current_user["id"],
            email=current_user["email"],
            full_name=data.get("full_name", current_user.get("full_name")),
            avatar_url=data.get("avatar_url"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update profile.")
