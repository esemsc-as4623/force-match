import random
import copy
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field

from backend.data.enriched_store import EnrichedStore
from backend.matching.constraints import ConstraintRegistry, ConstraintViolation

logger = logging.getLogger(__name__)

@dataclass
class MatchingResult:
    """
    Represents the result of a Secret Santa matching process.
    """
    pairings: Dict[str, str]  # giver_uri -> receiver_uri
    total_score: float
    violations: List[Dict[str, Any]] = field(default_factory=list)
    iteration_count: int = 0

class MatchingEngine:
    """
    Engine for generating and optimizing Secret Santa matches.
    """

    def __init__(self, store: EnrichedStore, active_constraints: List[str]):
        """
        Initialize the matching engine.

        Args:
            store: The EnrichedStore containing character data.
            active_constraints: List of names of constraints to apply.
        """
        self.store = store
        self.constraints = ConstraintRegistry.instantiate_constraints(active_constraints)
        self.severity_weights = {
            "BLOCKING": 1000000.0,
            "WARNING": 100.0,
            "INFO": 10.0
        }

    def _generate_derangement(self, participants: List[str]) -> Dict[str, str]:
        """
        Generates a random valid derangement (no self-loops).
        Uses rejection sampling which is efficient for N < 1000.
        """
        if len(participants) < 2:
            raise ValueError("Need at least 2 participants for a Secret Santa.")

        givers = participants[:]
        receivers = participants[:]
        
        # Simple rejection sampling
        # Probability of derangement is ~1/e (36.8%), so expected tries is ~2.7
        while True:
            random.shuffle(receivers)
            
            has_self_loop = False
            for g, r in zip(givers, receivers):
                if g == r:
                    has_self_loop = True
                    break
            
            if not has_self_loop:
                return {g: r for g, r in zip(givers, receivers)}

    def _score_matching(self, matching: Dict[str, str]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Scores a complete matching based on active constraints.
        
        Returns:
            Tuple of (total_score, list_of_violation_details)
        """
        total_score = 0.0
        all_violations = []
        enriched_data = self.store.get_all_characters()

        for giver_uri, receiver_uri in matching.items():
            giver = self.store.get_character(giver_uri)
            receiver = self.store.get_character(receiver_uri)

            if not giver or not receiver:
                logger.warning(f"Missing data for {giver_uri} or {receiver_uri}")
                continue

            for constraint in self.constraints:
                violations = constraint.validate(giver, receiver, enriched_data)
                
                for v in violations:
                    score_penalty = self.severity_weights.get(v.severity, 0.0)
                    total_score += score_penalty
                    
                    all_violations.append({
                        "giver": giver_uri,
                        "receiver": receiver_uri,
                        "constraint": v.constraint_name,
                        "description": v.description,
                        "severity": v.severity,
                        "score_penalty": score_penalty
                    })

        return total_score, all_violations

    def find_best_match(self, iterations: int = 20) -> MatchingResult:
        """
        Runs the matching algorithm multiple times and returns the best result.
        
        Args:
            iterations: Number of random restarts to perform.
            
        Returns:
            The best MatchingResult found.
        """
        participants = list(self.store.get_all_characters().keys())
        
        if not participants:
            logger.warning("No participants found in store.")
            return MatchingResult({}, 0.0)

        best_result = None

        for i in range(iterations):
            try:
                # 1. Generate a valid graph (derangement)
                pairings = self._generate_derangement(participants)
                
                # 2. Score it
                score, violations = self._score_matching(pairings)
                
                # 3. Compare with best
                if best_result is None or score < best_result.total_score:
                    best_result = MatchingResult(
                        pairings=pairings,
                        total_score=score,
                        violations=violations,
                        iteration_count=i + 1
                    )
                
                # Optimization: If we find a perfect match (score 0), stop early
                if score == 0.0:
                    logger.info(f"Found perfect match at iteration {i+1}")
                    break
                    
            except ValueError as e:
                logger.error(f"Error generating match: {e}")
                break

        if best_result is None:
             # Should only happen if participants < 2 or other critical error
             return MatchingResult({}, float('inf'))

        return best_result
