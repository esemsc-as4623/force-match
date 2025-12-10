import logging
from typing import List, Dict, Any, Tuple
from backend.llm.client import LLMClient
from backend.data.enriched_store import EnrichedStore

logger = logging.getLogger(__name__)

class RecommendationEngine:
    def __init__(self, enriched_store: EnrichedStore):
        self.store = enriched_store
        self.llm_client = LLMClient()
        self._cache: Dict[Tuple[str, str], List[str]] = {}
        self.fallback_gifts = [
            "A gallon of Blue Milk",
            "Death Star plans (slightly used)",
            "A ticket to the Podrace",
            "Wookiee-sized hairbrush",
            "Droid maintenance kit",
            "Jar Jar Binks voice modulator"
        ]

    async def generate_gift_ideas(self, giver_uri: str, receiver_uri: str) -> List[str]:
        """
        Generates gift ideas for a giver to give to a receiver.
        Uses LLM if available, otherwise falls back to static list.
        Caches results.
        """
        # Check cache
        cache_key = (giver_uri, receiver_uri)
        if cache_key in self._cache:
            logger.info(f"Returning cached gift ideas for {giver_uri} -> {receiver_uri}")
            return self._cache[cache_key]

        giver = self.store.get_character(giver_uri)
        receiver = self.store.get_character(receiver_uri)

        if not giver:
            logger.warning(f"Giver not found: {giver_uri}")
            return self.fallback_gifts[:3]
        
        if not receiver:
            logger.warning(f"Receiver not found: {receiver_uri}")
            return self.fallback_gifts[:3]

        # Prepare data for LLM
        giver_data = self._prepare_character_data(giver)
        receiver_data = self._prepare_character_data(receiver)

        # Call LLM
        try:
            gifts = await self.llm_client.get_gift_suggestions(giver_data, receiver_data)
        except Exception as e:
            logger.error(f"Error calling LLM for gifts: {e}")
            gifts = []

        if not gifts:
            logger.info("Using fallback gifts")
            gifts = self.fallback_gifts[:3]
        
        # Update cache
        self._cache[cache_key] = gifts
        return gifts

    def _prepare_character_data(self, char_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts relevant fields for LLM from the character data dictionary.
        """
        data = {
            "name": char_data.get("name", "Unknown"),
            "species": char_data.get("species", "Unknown"),
            "traits": []
        }
        
        semantics = char_data.get("semantics")
        if semantics:
            # semantics is a SemanticProfile object
            if hasattr(semantics, 'traits'):
                data["traits"] = semantics.traits
            
        return data
