"""Supabase Storage helpers — upload, download, delete files."""

from app.database import get_supabase
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def upload_file(bucket: str, path: str, file_bytes: bytes, content_type: str = "application/octet-stream") -> str | None:
    """
    Upload a file to Supabase Storage.
    Returns the public URL or None on failure.
    
    Path convention: {user_id}/{uuid}_{filename}
    """
    supabase = get_supabase()
    if supabase is None:
        logger.warning("Supabase not configured — file upload skipped")
        return None

    try:
        supabase.storage.from_(bucket).upload(
            path=path,
            file=file_bytes,
            file_options={"content-type": content_type, "upsert": "true"},
        )
        # Get public URL
        url = supabase.storage.from_(bucket).get_public_url(path)
        logger.info(f"Uploaded to {bucket}/{path}")
        return url
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        return None


async def download_file(bucket: str, path: str) -> bytes | None:
    """Download a file from Supabase Storage."""
    supabase = get_supabase()
    if supabase is None:
        return None

    try:
        response = supabase.storage.from_(bucket).download(path)
        logger.info(f"Downloaded from {bucket}/{path}")
        return response
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        return None


async def delete_file(bucket: str, path: str) -> bool:
    """Delete a file from Supabase Storage."""
    supabase = get_supabase()
    if supabase is None:
        return False

    try:
        supabase.storage.from_(bucket).remove([path])
        logger.info(f"Deleted {bucket}/{path}")
        return True
    except Exception as e:
        logger.error(f"Delete failed: {str(e)}")
        return False


def get_content_type(file_name: str) -> str:
    """Get MIME type from file extension."""
    ext = file_name.lower().rsplit(".", 1)[-1] if "." in file_name else ""
    return {
        "csv": "text/csv",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "xls": "application/vnd.ms-excel",
    }.get(ext, "application/octet-stream")
