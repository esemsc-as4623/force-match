import logging
import os
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Body
from pathlib import Path

from backend.data.enriched_store import EnrichedStore
from backend.matching.matcher import MatchingEngine
from backend.matching.evaluator import MatchEvaluator

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize store and load data once
# In a real production app, this might be a dependency or loaded on startup
store = EnrichedStore()
DATA_FILE = Path(__file__).parents[3] / "data" / "enriched_characters.json"

if DATA_FILE.exists():
    store.load_data(str(DATA_FILE))
    logger.info(f"Loaded enriched data from {DATA_FILE}")
else:
    logger.warning(f"Enriched data file not found at {DATA_FILE}. Matching may fail.")

@router.post("/match", response_model=Dict[str, Any])
async def generate_match(constraints: List[str] = Body(..., embed=True)):
    """
    Generates a Secret Santa match based on the provided constraints.
    
    Args:
        constraints: A list of constraint names to enable.
        
    Returns:
        A dictionary containing the matching result and evaluation metrics.
    """
    if not store.get_all_characters():
        # Try reloading if empty
        if DATA_FILE.exists():
            store.load_data(str(DATA_FILE))
        
        if not store.get_all_characters():
             raise HTTPException(status_code=503, detail="Enriched character data not available.")

    try:
        engine = MatchingEngine(store, active_constraints=constraints)
        result = engine.find_best_match()
        
        if not result:
             raise HTTPException(status_code=404, detail="Could not find a valid match.")

        evaluator = MatchEvaluator()
        evaluation = evaluator.evaluate_match(result)
        
        return evaluation

    except Exception as e:
        logger.error(f"Error generating match: {e}")
        raise HTTPException(status_code=500, detail=str(e))
