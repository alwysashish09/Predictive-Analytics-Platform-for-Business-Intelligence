"""ML API — trigger model training and retrieve results."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.database import get_supabase
from app.middleware.auth import get_current_user
from app.utils.logger import get_logger
from app.api.etl import _get_dataset_df
from app.schemas.model_run import TrainModelRequest, ModelRunResponse
from app.ml.pipeline import MLPipeline

logger = get_logger(__name__)

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.post("/{dataset_id}/train", response_model=ModelRunResponse)
async def train_model(
    dataset_id: str, 
    request: TrainModelRequest, 
    current_user: dict = Depends(get_current_user)
):
    """
    Train a machine learning model on a dataset.
    Currently runs synchronously for MVP (in production, use Celery/BackgroundTasks).
    """
    # 1. Fetch Dataset
    try:
        df, dataset, supabase = await _get_dataset_df(dataset_id, current_user)
    except Exception as e:
        raise HTTPException(400, f"Could not load dataset for training: {e}")

    # Validate target column exists
    if request.target_column not in df.columns:
        raise HTTPException(400, f"Target column '{request.target_column}' not found in dataset.")

    # Drop target nulls (we can't train on them)
    df = df.dropna(subset=[request.target_column])
    if len(df) < 50:
        raise HTTPException(400, "Dataset has too few rows (or too many missing targets) to train a model.")

    run_id = str(uuid.uuid4())
    
    # 2. Init Pipeline
    pipeline = MLPipeline(
        run_id=run_id,
        df=df,
        target_column=request.target_column,
        model_type=request.model_type,
        hyperparameters=request.hyperparameters
    )

    # 3. Run Pipeline
    try:
        results = pipeline.run()
    except Exception as e:
        logger.error(f"Model training failed: {e}")
        raise HTTPException(500, f"Model training failed: {str(e)}")

    # 4. Save metadata to DB
    run_data = {
        "id": run_id,
        "dataset_id": dataset_id,
        "user_id": current_user["id"],
        "model_type": request.model_type,
        "target_column": request.target_column,
        "features_used": [f.feature for f in results["feature_importance"]],
        "hyperparameters": request.hyperparameters,
        "metrics": results["metrics"].model_dump(),
        "feature_importance": [f.model_dump() for f in results["feature_importance"]],
        "model_file_url": results["model_file_path"], # Storing local path for MVP instead of bucket
        "status": "completed",
        "training_duration_sec": results["training_duration_sec"]
    }
    
    try:
        db_res = supabase.table("model_runs").insert(run_data).execute()
        if not db_res.data:
            raise HTTPException(500, "Failed to save model run to database.")
            
        # Update dataset with problem type
        supabase.table("datasets").update({
            "target_column": request.target_column,
            "problem_type": "classification" # Hardcoded for now based on Phase 11
        }).eq("id", dataset_id).execute()
        
        return db_res.data[0]
        
    except Exception as e:
        logger.error(f"DB insert error: {e}")
        raise HTTPException(500, "Database error saving model run.")


@router.get("/{dataset_id}/runs", response_model=list[ModelRunResponse])
async def list_model_runs(dataset_id: str, current_user: dict = Depends(get_current_user)):
    """List all model runs for a specific dataset."""
    supabase = get_supabase()
    try:
        result = supabase.table("model_runs").select("*").eq("dataset_id", dataset_id).eq("user_id", current_user["id"]).order("created_at", desc=True).execute()
        return result.data
    except Exception as e:
        logger.error(f"Failed to list model runs: {e}")
        raise HTTPException(500, "Failed to fetch model runs.")
