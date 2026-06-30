"""Insights API — Gemini-powered AI chat for querying datasets and models."""

import os
from fastapi import APIRouter, Depends, HTTPException
from google import genai
from google.genai import types

from app.database import get_supabase
from app.middleware.auth import get_current_user
from app.utils.logger import get_logger
from app.schemas.insights import ChatRequest, ChatResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/insights", tags=["Insights"])

# Initialize Gemini Client
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY is not set. Insights API will fail if called.")

def get_gemini_client():
    if not GEMINI_API_KEY:
        raise HTTPException(500, "Gemini API key is not configured on the server.")
    return genai.Client(api_key=GEMINI_API_KEY)


def build_system_context(dataset: dict, latest_run: dict | None) -> str:
    """Build a comprehensive context prompt about the dataset and model."""
    context = f"You are an expert Data Scientist and Business Analyst AI for a Predictive Analytics Platform. "
    context += f"You are analyzing a dataset named '{dataset.get('name', 'Unknown')}'.\n\n"
    
    # Dataset Stats
    context += "### Dataset Profile\n"
    context += f"- Total Rows: {dataset.get('row_count', 'Unknown')}\n"
    context += f"- Total Columns: {dataset.get('column_count', 'Unknown')}\n"
    
    if dataset.get('column_metadata'):
        context += "- Key Features:\n"
        for col, meta in list(dataset['column_metadata'].items())[:10]: # Limit to top 10 to save tokens
            context += f"  * {col} (Type: {meta.get('dtype')}, Nulls: {meta.get('null_percentage')}%, Unique: {meta.get('unique_count')})\n"

    # Model Stats
    if latest_run:
        context += "\n### Latest Machine Learning Model Run\n"
        context += f"- Target Variable Predicted: {latest_run.get('target_column')}\n"
        context += f"- Algorithm Used: {latest_run.get('model_type')}\n"
        
        metrics = latest_run.get('metrics', {})
        context += "- Performance Metrics:\n"
        context += f"  * Accuracy: {metrics.get('accuracy', 0)*100:.2f}%\n"
        context += f"  * F1 Score: {metrics.get('f1_score', 0)*100:.2f}%\n"
        context += f"  * Precision: {metrics.get('precision', 0)*100:.2f}%\n"
        
        fi = latest_run.get('feature_importance', [])
        if fi:
            context += "- Top Drivers (Feature Importance):\n"
            for f in fi[:5]:
                context += f"  * {f.get('feature')}: {f.get('importance', 0)*100:.1f}%\n"

    context += "\n### Instructions\n"
    context += "Use the context provided above to answer the user's questions about their data and the predictive model. "
    context += "Explain technical machine learning concepts (like feature importance or accuracy) in clear, business-friendly terms. "
    context += "If asked to generate code, write Python pandas or scikit-learn code. Provide actionable insights. Do not hallucinate data that is not provided in the context."
    
    return context


@router.post("/{dataset_id}/chat", response_model=ChatResponse)
async def chat_with_data(
    dataset_id: str, 
    request: ChatRequest, 
    current_user: dict = Depends(get_current_user)
):
    """Chat with Gemini about a specific dataset and its ML models."""
    supabase = get_supabase()
    
    # 1. Fetch Dataset
    ds_res = supabase.table("datasets").select("*").eq("id", dataset_id).eq("user_id", current_user["id"]).single().execute()
    if not ds_res.data:
        raise HTTPException(404, "Dataset not found.")
    dataset = ds_res.data

    # 2. Fetch Latest Model Run
    run_res = supabase.table("model_runs").select("*").eq("dataset_id", dataset_id).eq("user_id", current_user["id"]).order("created_at", desc=True).limit(1).execute()
    latest_run = run_res.data[0] if run_res.data else None

    # 3. Construct System Instructions
    system_instruction = build_system_context(dataset, latest_run)

    # 4. Format History for Gemini
    formatted_history = []
    for msg in request.history:
        role = "user" if msg.role == "user" else "model"
        formatted_history.append(
            types.Content(role=role, parts=[types.Part.from_text(text=msg.content)])
        )

    # 5. Call Gemini via SDK
    try:
        client = get_gemini_client()
        
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        )
        
        chat = client.chats.create(
            model="gemini-2.5-flash",
            config=config,
            history=formatted_history
        )
        
        response = chat.send_message(request.message)
        
        return ChatResponse(response=response.text)
        
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise HTTPException(500, f"AI generation failed: {str(e)}")
