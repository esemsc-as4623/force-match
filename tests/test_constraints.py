import unittest
from typing import Dict, Any
from backend.matching.constraints import (
    ConstraintRegistry,
    RelationshipAvoidanceConstraint,
    FactionBalanceConstraint,
    HomeworldDiversityConstraint,
    DegreeOfSeparationConstraint,
    DirectContactAvoidanceConstraint,
    TimelineEraConstraint,
    ConstraintViolation
)
from backend.knowledge.relationships import RelationshipType

class TestConstraints(unittest.TestCase):

    def setUp(self):
        self.enriched_data = {
            "http://swapi.co/resource/human/1": {
                "label": "Luke Skywalker",
                "homeworld": "Tatooine",
                "birth_year": "19BBY",
                "relationships": [
                    {"target": "Darth Vader", "type": "FAMILY"},
                    {"target": "Leia Organa", "type": "FAMILY"},
                    {"target": "Obi-Wan Kenobi", "type": "MASTER_APPRENTICE"},
                    {"target": "Rebel Alliance", "type": "FACTION_MEMBER"}
                ],
                "semantics": {
                    "traits": ["Heroic", "Pilot"],
                    "motivations": ["Defeat the Empire", "Save his father"]
                }
            },
            "http://swapi.co/resource/human/2": {
                "label": "Darth Vader",
                "homeworld": "Tatooine",
                "birth_year": "41.9BBY",
                "relationships": [
                    {"target": "Luke Skywalker", "type": "FAMILY"},
                    {"target": "Galactic Empire", "type": "FACTION_MEMBER"}
                ],
                "semantics": {
                    "traits": ["Ruthless", "Powerful"],
                    "motivations": ["Crush the Rebellion", "Find Luke Skywalker"]
                }
            },
            "http://swapi.co/resource/human/3": {
                "label": "Han Solo",
                "homeworld": "Corellia",
                "birth_year": "29BBY",
                "relationships": [
                    {"target": "Rebel Alliance", "type": "FACTION_MEMBER"}
                ],
                "semantics": {
                    "traits": ["Smuggler", "Charming"],
                    "motivations": ["Money", "Love"]
                }
            }
        }

    def test_registry(self):
        constraints = ConstraintRegistry.get_all_constraints()
        self.assertIn("relationship_avoidance", constraints)
        self.assertIn("faction_balance", constraints)
        self.assertIn("homeworld_diversity", constraints)
        
        instantiated = ConstraintRegistry.instantiate_constraints(["relationship_avoidance", "faction_balance"])
        self.assertEqual(len(instantiated), 2)
        self.assertIsInstance(instantiated[0], RelationshipAvoidanceConstraint)

    def test_relationship_avoidance(self):
        constraint = RelationshipAvoidanceConstraint()
        luke = self.enriched_data["http://swapi.co/resource/human/1"]
        vader = self.enriched_data["http://swapi.co/resource/human/2"]
        
        violations = constraint.validate(luke, vader, self.enriched_data)
        self.assertTrue(len(violations) > 0)
        self.assertEqual(violations[0].severity, "BLOCKING")
        self.assertIn("FAMILY", violations[0].description)

    def test_faction_balance(self):
        constraint = FactionBalanceConstraint()
        luke = self.enriched_data["http://swapi.co/resource/human/1"]
        han = self.enriched_data["http://swapi.co/resource/human/3"]
        vader = self.enriched_data["http://swapi.co/resource/human/2"]
        
        # Luke and Han are both Rebels -> Warning
        violations = constraint.validate(luke, han, self.enriched_data)
        self.assertTrue(len(violations) > 0)
        self.assertEqual(violations[0].severity, "WARNING")
        
        # Luke and Vader are different factions -> No violation (in this simple logic)
        violations = constraint.validate(luke, vader, self.enriched_data)
        self.assertEqual(len(violations), 0)

    def test_homeworld_diversity(self):
        constraint = HomeworldDiversityConstraint()
        luke = self.enriched_data["http://swapi.co/resource/human/1"]
        vader = self.enriched_data["http://swapi.co/resource/human/2"]
        han = self.enriched_data["http://swapi.co/resource/human/3"]
        
        # Luke and Vader both from Tatooine -> Info
        violations = constraint.validate(luke, vader, self.enriched_data)
        self.assertTrue(len(violations) > 0)
        self.assertEqual(violations[0].severity, "INFO")
        
        # Luke and Han different -> No violation
        violations = constraint.validate(luke, han, self.enriched_data)
        self.assertEqual(len(violations), 0)

    def test_degree_of_separation(self):
        constraint = DegreeOfSeparationConstraint()
        luke = self.enriched_data["http://swapi.co/resource/human/1"]
        vader = self.enriched_data["http://swapi.co/resource/human/2"]
        
        # Luke <-> Vader is direct (degree 1) -> Warning
        violations = constraint.validate(luke, vader, self.enriched_data)
        self.assertTrue(len(violations) > 0)
        self.assertIn("degree 1.0", violations[0].description)

    def test_direct_contact_avoidance(self):
        constraint = DirectContactAvoidanceConstraint()
        vader = self.enriched_data["http://swapi.co/resource/human/2"]
        luke = self.enriched_data["http://swapi.co/resource/human/1"]
        
        # Vader's motivation mentions "Luke Skywalker" -> Warning
        violations = constraint.validate(vader, luke, self.enriched_data)
        self.assertTrue(len(violations) > 0)
        self.assertIn("mentions receiver", violations[0].description)

    def test_timeline_era(self):
        constraint = TimelineEraConstraint()
        luke = self.enriched_data["http://swapi.co/resource/human/1"]
        vader = self.enriched_data["http://swapi.co/resource/human/2"]
        
        # 19BBY vs 41.9BBY -> Diff ~22.9 -> No violation (< 60)
        violations = constraint.validate(luke, vader, self.enriched_data)
        self.assertEqual(len(violations), 0)
        
        # Create a very old character
        yoda = {
            "label": "Yoda",
            "birth_year": "896BBY"
        }
        
        # Yoda vs Luke -> Diff ~877 -> Info
        violations = constraint.validate(yoda, luke, self.enriched_data)
        self.assertTrue(len(violations) > 0)
        self.assertEqual(violations[0].severity, "INFO")

if __name__ == '__main__':
    unittest.main()
