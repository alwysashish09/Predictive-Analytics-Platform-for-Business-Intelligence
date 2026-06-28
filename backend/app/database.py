from supabase import create_client, Client
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_supabase_client: Client | None = None


def get_supabase() -> Client:
    """Get or create Supabase client singleton."""
    global _supabase_client
    if _supabase_client is None:
        settings = get_settings()
        if not settings.supabase_url or not settings.supabase_anon_key:
            logger.warning("Supabase credentials not configured. Some features will be unavailable.")
            return None
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key,
        )
        logger.info("Supabase client initialized")
    return _supabase_client


def get_supabase_admin() -> Client:
    """Get Supabase client with service role key for admin operations."""
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        logger.warning("Supabase admin credentials not configured.")
        return None
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
    )
