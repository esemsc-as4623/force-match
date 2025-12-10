from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import logging
from backend.recommendations.engine import RecommendationEngine
from backend.data.enriched_store import EnrichedStore

router = APIRouter()
logger = logging.getLogger(__name__)

# Dependency to get the recommendation engine
# In a real app, this might be a singleton or injected dependency
_engine = None

def get_recommendation_engine():
    global _engine
    if _engine is None:
        # Initialize store and load data
        store = EnrichedStore()
        # Assuming data is already loaded or will be loaded. 
        # For now, we'll try to load from the default location if not loaded.
        # In a production setup, the store would likely be initialized at startup.
        if not store._is_loaded:
             store.load_data("data/enriched_characters.json")
        _engine = RecommendationEngine(store)
    return _engine

class RecommendationRequest(BaseModel):
    giver_uri: str
    receiver_uri: str

class RecommendationResponse(BaseModel):
    recommendations: List[str]

@router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """
    Generates 3 humorous gift recommendations based on the giver and receiver.
    """
    try:
        recommendations = await engine.generate_gift_ideas(request.giver_uri, request.receiver_uri)
        return RecommendationResponse(recommendations=recommendations)
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
