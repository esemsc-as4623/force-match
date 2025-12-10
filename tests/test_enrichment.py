import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from pathlib import Path
import networkx as nx

# Add project root to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

from backend.knowledge.relationships import RelationshipClassifier, SemanticAnalyzer, RelationshipType, Relationship
from backend.knowledge.graph_utils import build_graph, calculate_degree
import load_to_cognee

class TestRelationshipClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = RelationshipClassifier()

    def test_family_relationship(self):
        text = "Luke Skywalker is the son of Darth Vader."
        results = self.classifier.classify(text)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].type, RelationshipType.FAMILY)
        self.assertEqual(results[0].target, "Darth Vader")

    def test_master_apprentice_relationship(self):
        text = "Obi-Wan Kenobi was the master of Anakin Skywalker."
        results = self.classifier.classify(text)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].type, RelationshipType.MASTER_APPRENTICE)
        self.assertEqual(results[0].target, "Anakin Skywalker")

    def test_multiple_relationships(self):
        text = "Luke is the son of Vader. He is the brother of Leia Organa."
        results = self.classifier.classify(text)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].target, "Vader")
        self.assertEqual(results[1].target, "Leia Organa")

    def test_no_relationship(self):
        text = "This is a random sentence about Tatooine."
        results = self.classifier.classify(text)
        self.assertEqual(len(results), 0)

    def test_empty_input(self):
        results = self.classifier.classify("")
        self.assertEqual(len(results), 0)

class TestSemanticAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = SemanticAnalyzer()

    def test_traits_extraction(self):
        text = "He is a brave and loyal warrior."
        profile = self.analyzer.analyze(text)
        self.assertIn("brave", profile.traits)
        self.assertIn("loyal", profile.traits)

    def test_motivation_extraction(self):
        text = "She wants to bring peace and justice to the galaxy."
        profile = self.analyzer.analyze(text)
        self.assertIn("justice", profile.motivations)
        self.assertIn("peace", profile.motivations)

    def test_role_extraction(self):
        text = "Yoda is a powerful Jedi Master."
        profile = self.analyzer.analyze(text)
        self.assertEqual(profile.role, "Jedi")

class TestGraphUtils(unittest.TestCase):
    def setUp(self):
        self.characters = {
            "Luke": {
                "label": "Luke",
                "relationships": [
                    Relationship(target="Vader", type=RelationshipType.FAMILY, details="son of"),
                    Relationship(target="Leia", type=RelationshipType.FAMILY, details="brother of")
                ]
            },
            "Vader": {
                "label": "Vader",
                "relationships": [
                    Relationship(target="Luke", type=RelationshipType.FAMILY, details="father of")
                ]
            },
            "Leia": {
                "label": "Leia",
                "relationships": []
            },
            "Han": {
                "label": "Han",
                "relationships": []
            }
        }
        self.graph = build_graph(self.characters)

    def test_build_graph_nodes(self):
        self.assertTrue(self.graph.has_node("Luke"))
        self.assertTrue(self.graph.has_node("Vader"))
        self.assertTrue(self.graph.has_node("Leia"))
        # Han is in characters but has no relationships, should still be a node
        self.assertTrue(self.graph.has_node("Han"))

    def test_build_graph_edges(self):
        self.assertTrue(self.graph.has_edge("Luke", "Vader"))
        self.assertTrue(self.graph.has_edge("Luke", "Leia"))
        self.assertFalse(self.graph.has_edge("Luke", "Han"))

    def test_calculate_degree_direct(self):
        degree = calculate_degree(self.graph, "Luke", "Vader")
        self.assertEqual(degree, 1.0)

    def test_calculate_degree_indirect(self):
        # Vader -> Luke -> Leia (Path length 2)
        degree = calculate_degree(self.graph, "Vader", "Leia")
        self.assertEqual(degree, 2.0)

    def test_calculate_degree_disconnected(self):
        degree = calculate_degree(self.graph, "Luke", "Han")
        self.assertEqual(degree, float('inf'))

    def test_calculate_degree_unknown_node(self):
        degree = calculate_degree(self.graph, "Luke", "Jabba")
        self.assertEqual(degree, float('inf'))

class TestRDFParsing(unittest.TestCase):
    def setUp(self):
        # Create a temporary TTL file
        self.test_ttl_path = "test_data.ttl"
        with open(self.test_ttl_path, "w") as f:
            f.write("""
@prefix voc: <https://swapi.co/vocabulary/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<https://swapi.co/resource/human/1> a voc:Character ;
    rdfs:label "Luke Skywalker" ;
    voc:hair_color "blond" .
            """)

    def tearDown(self):
        if os.path.exists(self.test_ttl_path):
            os.remove(self.test_ttl_path)

    def test_parse_rdf_data(self):
        characters = load_to_cognee.parse_rdf_data(self.test_ttl_path)
        self.assertIn("https://swapi.co/resource/human/1", characters)
        char_data = characters["https://swapi.co/resource/human/1"]
        self.assertEqual(char_data["label"], "Luke Skywalker")
        self.assertEqual(char_data["hair_color"], "blond")

if __name__ == '__main__':
    unittest.main()
