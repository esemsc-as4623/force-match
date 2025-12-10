import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.recommendations.engine import RecommendationEngine
from backend.data.enriched_store import EnrichedStore
from backend.llm.client import LLMClient

@pytest.fixture
def mock_store():
    store = MagicMock(spec=EnrichedStore)
    store.get_character.side_effect = lambda uri: {
        "name": "Luke Skywalker" if "luke" in uri else "Darth Vader",
        "species": "Human",
        "semantics": MagicMock(traits=["Heroic", "Pilot"]) if "luke" in uri else MagicMock(traits=["Sith", "Father"])
    }
    return store

@pytest.fixture
def mock_llm_client():
    client = MagicMock(spec=LLMClient)
    client.get_gift_suggestions = AsyncMock(return_value=["Lightsaber Polish", "New Hand", "Flight Simulator"])
    return client

@pytest.mark.asyncio
async def test_generate_gift_ideas_success(mock_store, mock_llm_client):
    with patch("backend.recommendations.engine.LLMClient", return_value=mock_llm_client):
        engine = RecommendationEngine(mock_store)
        
        gifts = await engine.generate_gift_ideas("http://swapi.co/resource/human/1", "http://swapi.co/resource/human/4")
        
        assert len(gifts) == 3
        assert "Lightsaber Polish" in gifts
        mock_llm_client.get_gift_suggestions.assert_called_once()

@pytest.mark.asyncio
async def test_generate_gift_ideas_fallback(mock_store, mock_llm_client):
    # Simulate LLM failure
    mock_llm_client.get_gift_suggestions.side_effect = Exception("LLM Down")
    
    with patch("backend.recommendations.engine.LLMClient", return_value=mock_llm_client):
        engine = RecommendationEngine(mock_store)
        
        gifts = await engine.generate_gift_ideas("http://swapi.co/resource/human/1", "http://swapi.co/resource/human/4")
        
        # Should return fallback gifts
        assert len(gifts) == 3
        assert gifts[0] in engine.fallback_gifts

@pytest.mark.asyncio
async def test_caching_behavior(mock_store, mock_llm_client):
    with patch("backend.recommendations.engine.LLMClient", return_value=mock_llm_client):
        engine = RecommendationEngine(mock_store)
        
        # First call
        await engine.generate_gift_ideas("http://swapi.co/resource/human/1", "http://swapi.co/resource/human/4")
        
        # Second call (should be cached)
        await engine.generate_gift_ideas("http://swapi.co/resource/human/1", "http://swapi.co/resource/human/4")
        
        # LLM should only be called once
        mock_llm_client.get_gift_suggestions.assert_called_once()

def test_prompt_construction():
    client = LLMClient()
    giver = {"name": "Han Solo", "species": "Human", "traits": ["Smuggler", "Scoundrel"]}
    receiver = {"name": "Chewbacca", "species": "Wookiee", "traits": ["Loyal", "Strong"]}
    
    prompt = client._construct_gift_prompt(giver, receiver)
    
    assert "Han Solo" in prompt
    assert "Chewbacca" in prompt
    assert "Smuggler" in prompt
    assert "Wookiee" in prompt
    assert "humorous" in prompt
