"""Datasets API — upload, list, and preview datasets."""

import io
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from app.database import get_supabase
from app.middleware.auth import get_current_user
from app.utils.logger import get_logger
from app.utils.storage import upload_file, get_content_type
from app.etl.file_parser import parse_file, extract_column_metadata
from app.schemas.dataset import DatasetResponse, DatasetListItem, DatasetPreview

logger = get_logger(__name__)

router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str | None = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Upload a new CSV/Excel dataset, parse it, and store metadata in Supabase."""
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(400, "Only CSV and Excel files are supported.")

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(400, "File is empty.")

    # 1. Parse File to get initial metadata
    try:
        df = parse_file(file_bytes, file.filename)
    except Exception as e:
        logger.error(f"Failed to parse file: {e}")
        raise HTTPException(422, f"Failed to parse file. Make sure it's a valid CSV/Excel. Error: {str(e)}")

    dataset_name = name or file.filename.rsplit(".", 1)[0]
    row_count = int(df.shape[0])
    col_count = int(df.shape[1])
    
    # 2. Extract column metadata
    column_metadata = extract_column_metadata(df)

    # 3. Upload to Supabase Storage
    dataset_id = str(uuid.uuid4())
    storage_path = f"{current_user['id']}/{dataset_id}_{file.filename}"
    content_type = get_content_type(file.filename)
    
    file_url = await upload_file("datasets", storage_path, file_bytes, content_type)
    if not file_url:
        raise HTTPException(500, "Failed to upload file to storage.")

    # 4. Save metadata to DB
    supabase = get_supabase()
    dataset_data = {
        "id": dataset_id,
        "user_id": current_user["id"],
        "name": dataset_name,
        "file_name": file.filename,
        "file_url": file_url,
        "file_size_bytes": len(file_bytes),
        "row_count": row_count,
        "column_count": col_count,
        "column_metadata": column_metadata,
        "status": "uploaded"
    }

    try:
        result = supabase.table("datasets").insert(dataset_data).execute()
        if not result.data:
            raise HTTPException(500, "Failed to save dataset metadata.")
        return result.data[0]
    except Exception as e:
        logger.error(f"DB insert error: {e}")
        raise HTTPException(500, "Database error saving dataset.")


@router.get("", response_model=list[DatasetListItem])
async def list_datasets(current_user: dict = Depends(get_current_user)):
    """List all datasets for the current user."""
    supabase = get_supabase()
    try:
        result = supabase.table("datasets").select(
            "id, name, file_name, row_count, column_count, status, problem_type, target_column, created_at"
        ).eq("user_id", current_user["id"]).order("created_at", desc=True).execute()
        
        return result.data
    except Exception as e:
        logger.error(f"Failed to list datasets: {e}")
        raise HTTPException(500, "Failed to fetch datasets.")


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific dataset."""
    supabase = get_supabase()
    try:
        result = supabase.table("datasets").select("*").eq("id", dataset_id).eq("user_id", current_user["id"]).single().execute()
        if not result.data:
            raise HTTPException(404, "Dataset not found.")
        return result.data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dataset: {e}")
        raise HTTPException(500, "Failed to fetch dataset details.")


@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a dataset and its storage file."""
    supabase = get_supabase()
    try:
        # DB deletion (Storage files can be cleaned up via trigger or background job later, 
        # or we can rely on RLS if implemented carefully. For now, just DB.)
        result = supabase.table("datasets").delete().eq("id", dataset_id).eq("user_id", current_user["id"]).execute()
        if not result.data:
            raise HTTPException(404, "Dataset not found.")
        return {"success": True, "message": "Dataset deleted."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete dataset: {e}")
        raise HTTPException(500, "Failed to delete dataset.")
