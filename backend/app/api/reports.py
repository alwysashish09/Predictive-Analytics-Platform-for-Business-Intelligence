"""Reports API — generate and download PDF reports."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.database import get_supabase
from app.middleware.auth import get_current_user
from app.utils.logger import get_logger
from app.reports.pdf_generator import ReportGenerator
from app.api.insights import build_system_context, get_gemini_client
from google.genai import types

logger = get_logger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/{dataset_id}/download")
async def download_executive_report(dataset_id: str, current_user: dict = Depends(get_current_user)):
    """Generate and download a PDF executive report for a dataset and its latest model."""
    supabase = get_supabase()
    
    # 1. Fetch Dataset
    ds_res = supabase.table("datasets").select("*").eq("id", dataset_id).eq("user_id", current_user["id"]).single().execute()
    if not ds_res.data:
        raise HTTPException(404, "Dataset not found.")
    dataset = ds_res.data

    # 2. Fetch Latest Model Run
    run_res = supabase.table("model_runs").select("*").eq("dataset_id", dataset_id).eq("user_id", current_user["id"]).order("created_at", desc=True).limit(1).execute()
    if not run_res.data:
        raise HTTPException(400, "No model trained for this dataset yet. Train a model first.")
    latest_run = run_res.data[0]

    # 3. Request Executive Summary from Gemini
    ai_insights = None
    try:
        client = get_gemini_client()
        system_instruction = build_system_context(dataset, latest_run)
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        )
        
        prompt = "Write a 3 paragraph executive summary explaining the dataset, the model's accuracy, and the primary factors driving the predictions. Do not use complex markdown, just plain text with simple bullet points if necessary."
        
        chat = client.chats.create(model="gemini-2.5-flash", config=config)
        response = chat.send_message(prompt)
        ai_insights = response.text
    except Exception as e:
        logger.warning(f"Failed to generate AI insights for report: {e}")
        ai_insights = "AI Insights could not be generated at this time."

    # 4. Generate PDF
    try:
        generator = ReportGenerator(dataset, latest_run, ai_insights)
        pdf_stream = generator.generate()
        
        # 5. Return as streaming response
        filename = f"{dataset.get('name', 'dataset').replace(' ', '_')}_Executive_Report.pdf"
        
        return StreamingResponse(
            pdf_stream, 
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate PDF: {e}")
        raise HTTPException(500, "Failed to generate PDF report.")
