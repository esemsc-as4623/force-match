import unittest
from backend.matching.evaluator import MatchEvaluator
from backend.matching.matcher import MatchingResult

class TestMatchEvaluator(unittest.TestCase):
    def test_evaluate_match_perfect(self):
        """Test evaluation of a perfect match (no violations)."""
        matching_result = MatchingResult(
            pairings={"A": "B", "B": "C", "C": "A"},
            total_score=0.0,
            violations=[],
            iteration_count=1
        )
        
        evaluator = MatchEvaluator()
        metrics = evaluator.evaluate_match(matching_result)
        
        self.assertEqual(metrics["total_violations"], 0)
        self.assertEqual(metrics["perfect_pairings_pct"], 100.0)
        self.assertEqual(metrics["satisfaction_score"], 100.0)
        self.assertEqual(len(metrics["detailed_violations"]), 0)

    def test_evaluate_match_with_violations(self):
        """Test evaluation with some violations."""
        violations = [
            {
                "giver": "A",
                "receiver": "B",
                "constraint": "relationship_avoidance",
                "description": "Siblings",
                "severity": "WARNING",
                "score_penalty": 10.0
            },
            {
                "giver": "B",
                "receiver": "C",
                "constraint": "relationship_avoidance",
                "description": "Rivals",
                "severity": "WARNING",
                "score_penalty": 10.0
            }
        ]
        
        matching_result = MatchingResult(
            pairings={"A": "B", "B": "C", "C": "A"},
            total_score=20.0,
            violations=violations,
            iteration_count=1
        )
        
        evaluator = MatchEvaluator()
        metrics = evaluator.evaluate_match(matching_result)
        
        self.assertEqual(metrics["total_violations"], 2)
        self.assertEqual(metrics["violations_by_type"]["relationship_avoidance"], 2)
        
        # 3 pairs, 2 have violations, 1 is perfect (C->A)
        # Perfect pairings pct = 1/3 * 100 = 33.33
        self.assertAlmostEqual(metrics["perfect_pairings_pct"], 33.33, places=2)
        
        # Satisfaction score: 33.33 - (2 warnings * 5) = 23.33
        self.assertAlmostEqual(metrics["satisfaction_score"], 23.33, places=2)
        
        self.assertEqual(len(metrics["detailed_violations"]), 2)
        self.assertEqual(metrics["detailed_violations"][0]["giver"], "A")
        self.assertEqual(metrics["detailed_violations"][0]["violations"][0], "relationship_avoidance: Siblings")

    def test_evaluate_match_blocking(self):
        """Test evaluation with a blocking violation."""
        violations = [
            {
                "giver": "A",
                "receiver": "B",
                "constraint": "hard_constraint",
                "description": "Impossible",
                "severity": "BLOCKING",
                "score_penalty": 1000.0
            }
        ]
        
        matching_result = MatchingResult(
            pairings={"A": "B", "B": "A"},
            total_score=1000.0,
            violations=violations,
            iteration_count=1
        )
        
        evaluator = MatchEvaluator()
        metrics = evaluator.evaluate_match(matching_result)
        
        self.assertEqual(metrics["satisfaction_score"], 0.0)

if __name__ == '__main__':
    unittest.main()
