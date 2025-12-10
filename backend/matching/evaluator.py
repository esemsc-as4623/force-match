from typing import Dict, Any, List
from collections import Counter
from backend.matching.matcher import MatchingResult

class MatchEvaluator:
    """
    Evaluates the quality of a matching result and generates detailed metrics.
    """

    def evaluate_match(self, matching_result: MatchingResult) -> Dict[str, Any]:
        """
        Calculates high-level metrics for a matching result.

        Args:
            matching_result: The result object from the MatchingEngine.

        Returns:
            A dictionary containing:
            - total_violations: Total count of violations.
            - violations_by_type: Histogram of violations per constraint type.
            - perfect_pairings_pct: Percentage of pairings with 0 violations.
            - satisfaction_score: Overall score (0-100%).
            - detailed_violations: Frontend-friendly list of violations.
        """
        total_violations = len(matching_result.violations)
        violations_by_type = Counter()
        
        # Track violations per pair to calculate perfect pairings
        pair_violations = {giver: 0 for giver in matching_result.pairings.keys()}
        
        formatted_violations = []

        for v in matching_result.violations:
            violations_by_type[v['constraint']] += 1
            pair_violations[v['giver']] += 1
            
            formatted_violations.append({
                "giver": v['giver'],
                "receiver": v['receiver'],
                "violation": f"{v['constraint']}: {v['description']}",
                "severity": v['severity']
            })

        # Calculate perfect pairings
        total_pairs = len(matching_result.pairings)
        perfect_pairs = sum(1 for count in pair_violations.values() if count == 0)
        perfect_pairings_pct = (perfect_pairs / total_pairs * 100) if total_pairs > 0 else 0.0

        # Calculate Satisfaction Score
        # This is a heuristic. We can define it as:
        # 100 - (total_score_penalty / max_possible_penalty * 100)
        # But max_possible_penalty is hard to define.
        # Let's use a simpler heuristic based on perfect pairings and severity.
        # Or just use the inverse of the normalized score if we had a normalization factor.
        # For now, let's base it on the percentage of perfect pairings, 
        # but penalized heavily by BLOCKING violations.
        
        has_blocking = any(v['severity'] == 'BLOCKING' for v in matching_result.violations)
        
        if has_blocking:
            satisfaction_score = 0.0
        else:
            # If no blocking, score is roughly proportional to perfect pairings,
            # maybe adjusted by WARNING count.
            # Let's keep it simple: same as perfect_pairings_pct for now, 
            # but maybe reduce it slightly for every warning.
            warning_count = sum(1 for v in matching_result.violations if v['severity'] == 'WARNING')
            # Deduct 5% for each warning, but don't go below 0
            penalty = warning_count * 5
            satisfaction_score = max(0.0, perfect_pairings_pct - penalty)

        # Group violations by pair for the frontend requirement:
        # [{ "giver": uri, "receiver": uri, "violations": ["ConstraintName: Description", ...] }]
        violations_by_pair = {}
        for v in matching_result.violations:
            key = (v['giver'], v['receiver'])
            if key not in violations_by_pair:
                violations_by_pair[key] = []
            violations_by_pair[key].append(f"{v['constraint']}: {v['description']}")
            
        frontend_violations = []
        for (giver, receiver), v_list in violations_by_pair.items():
            frontend_violations.append({
                "giver": giver,
                "receiver": receiver,
                "violations": v_list
            })

        return {
            "total_violations": total_violations,
            "violations_by_type": dict(violations_by_type),
            "perfect_pairings_pct": round(perfect_pairings_pct, 2),
            "satisfaction_score": round(satisfaction_score, 2),
            "detailed_violations": frontend_violations,
            "pairings": matching_result.pairings,
            "total_score": matching_result.total_score,
            "iteration_count": matching_result.iteration_count
        }
