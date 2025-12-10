import pytest
from unittest.mock import MagicMock
from typing import Dict, Any, List
from backend.matching.matcher import MatchingEngine, MatchingResult
from backend.matching.constraints import Constraint, ConstraintViolation, ConstraintRegistry
from backend.data.enriched_store import EnrichedStore

# --- Mocks & Helpers ---

class MockConstraint(Constraint):
    def __init__(self, name="mock_constraint", bad_pair=("A", "B")):
        self._name = name
        self.bad_pair = bad_pair

    @property
    def name(self) -> str:
        return self._name

    def validate(self, giver: Dict[str, Any], receiver: Dict[str, Any], enriched_data: Dict[str, Any]) -> List[ConstraintViolation]:
        # Fails if giver is bad_pair[0] and receiver is bad_pair[1]
        if giver.get("name") == self.bad_pair[0] and receiver.get("name") == self.bad_pair[1]:
            return [ConstraintViolation(self.name, "Bad pair!", "BLOCKING")]
        return []

@pytest.fixture
def mock_store():
    store = MagicMock(spec=EnrichedStore)
    # Create 4 characters: A, B, C, D
    chars = {
        "uri:A": {"name": "A"},
        "uri:B": {"name": "B"},
        "uri:C": {"name": "C"},
        "uri:D": {"name": "D"},
    }
    store.get_all_characters.return_value = chars
    store.get_character.side_effect = lambda uri: chars.get(uri)
    return store

@pytest.fixture
def engine(mock_store):
    # We need to patch the registry or inject constraints manually.
    # Since MatchingEngine instantiates constraints via Registry, we might need to mock that.
    # However, for unit testing, it's often easier to subclass or monkeypatch if the design allows.
    # Let's mock ConstraintRegistry.instantiate_constraints
    
    with pytest.MonkeyPatch.context() as m:
        # Mock the registry to return our MockConstraint
        mock_constraint = MockConstraint(bad_pair=("A", "B"))
        m.setattr(ConstraintRegistry, "instantiate_constraints", lambda names: [mock_constraint])
        
        engine = MatchingEngine(mock_store, ["mock_constraint"])
        yield engine

# --- Tests ---

def test_generate_derangement_validity(engine):
    """Test that generated matches are valid derangements."""
    participants = ["A", "B", "C", "D"]
    match = engine._generate_derangement(participants)
    
    # 1. Check size
    assert len(match) == 4
    
    # 2. Check keys and values
    assert set(match.keys()) == set(participants)
    assert set(match.values()) == set(participants)
    
    # 3. Check no self-loops
    for giver, receiver in match.items():
        assert giver != receiver

def test_generate_derangement_small_input(engine):
    """Test with minimal participants."""
    participants = ["A", "B"]
    match = engine._generate_derangement(participants)
    assert match["A"] == "B"
    assert match["B"] == "A"

def test_generate_derangement_error_on_single(engine):
    """Test that it raises error for < 2 participants."""
    with pytest.raises(ValueError):
        engine._generate_derangement(["A"])

def test_score_matching(engine):
    """Test that scoring correctly identifies violations."""
    # A -> B is a violation (BLOCKING = 1,000,000)
    # C -> D is fine
    # B -> A is fine
    # D -> C is fine
    
    matching = {
        "uri:A": "uri:B", # Violation
        "uri:B": "uri:A",
        "uri:C": "uri:D",
        "uri:D": "uri:C"
    }
    
    score, violations = engine._score_matching(matching)
    
    assert score == 1000000.0
    assert len(violations) == 1
    assert violations[0]["giver"] == "uri:A"
    assert violations[0]["receiver"] == "uri:B"

def test_find_best_match_optimization(mock_store):
    """
    Test that the engine finds a valid match without violations if one exists.
    We'll set up a scenario where A->B is bad, but A->C is good.
    """
    # Setup: A->B is bad.
    # Possible derangements for {A,B,C}:
    # 1. A->B, B->C, C->A (Bad because A->B)
    # 2. A->C, C->B, B->A (Good)
    
    chars = {
        "uri:A": {"name": "A"},
        "uri:B": {"name": "B"},
        "uri:C": {"name": "C"},
    }
    mock_store.get_all_characters.return_value = chars
    mock_store.get_character.side_effect = lambda uri: chars.get(uri)

    # Mock constraint: A->B is bad
    mock_constraint = MockConstraint(bad_pair=("A", "B"))
    
    with pytest.MonkeyPatch.context() as m:
        m.setattr(ConstraintRegistry, "instantiate_constraints", lambda names: [mock_constraint])
        engine = MatchingEngine(mock_store, ["mock_constraint"])
        
        # Run enough iterations to likely hit the good permutation (50% chance)
        result = engine.find_best_match(iterations=20)
        
        assert result.total_score == 0.0
        assert result.pairings["uri:A"] != "uri:B"
        assert len(result.violations) == 0

def test_find_best_match_impossible_constraint(mock_store):
    """
    Test that it returns the 'least bad' option if no perfect match exists.
    (Though with simple constraints and small N, it's hard to force 'least bad' without complex weights,
    so we'll just check that it returns *a* result with a score).
    """
    # Setup: Everyone hates everyone (A->B bad, A->C bad, etc)
    # Actually, let's just make A->B bad and force a 2-person exchange where A MUST give to B.
    
    chars = {
        "uri:A": {"name": "A"},
        "uri:B": {"name": "B"},
    }
    mock_store.get_all_characters.return_value = chars
    mock_store.get_character.side_effect = lambda uri: chars.get(uri)
    
    mock_constraint = MockConstraint(bad_pair=("A", "B"))
    
    with pytest.MonkeyPatch.context() as m:
        m.setattr(ConstraintRegistry, "instantiate_constraints", lambda names: [mock_constraint])
        engine = MatchingEngine(mock_store, ["mock_constraint"])
        
        # Only one possible derangement: A->B, B->A.
        # A->B is a violation.
        result = engine.find_best_match(iterations=5)
        
        assert result.total_score == 1000000.0
        assert len(result.violations) == 1
