import unittest
import os
import json
import shutil
from pathlib import Path
from backend.data.enriched_store import EnrichedStore
from backend.knowledge.relationships import Relationship, RelationshipType, SemanticProfile

class TestEnrichedStore(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("tests/temp_data")
        self.test_dir.mkdir(exist_ok=True)
        self.test_file = self.test_dir / "test_enriched_characters.json"
        self.store = EnrichedStore()

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_save_and_load_data(self):
        # Create dummy data
        dummy_data = {
            "http://swapi.co/resource/human/1": {
                "uri": "http://swapi.co/resource/human/1",
                "label": "Luke Skywalker",
                "relationships": [
                    Relationship(target="Darth Vader", type=RelationshipType.FAMILY, details="father of"),
                    Relationship(target="Obi-Wan Kenobi", type=RelationshipType.MASTER_APPRENTICE, details="trained by")
                ],
                "semantics": SemanticProfile(
                    traits=["Brave", "Impulsive"],
                    motivations=["Save the galaxy", "Become a Jedi"],
                    role="Protagonist"
                )
            },
            "http://swapi.co/resource/droid/2": {
                "uri": "http://swapi.co/resource/droid/2",
                "label": "R2-D2",
                "relationships": [],
                "semantics": None
            }
        }

        # Save data
        self.store.save_data(dummy_data, str(self.test_file))

        # Verify file exists
        self.assertTrue(self.test_file.exists())

        # Load data back
        loaded_store = EnrichedStore()
        loaded_data = loaded_store.load_data(str(self.test_file))

        # Verify loaded data
        self.assertEqual(len(loaded_data), 2)
        
        luke = loaded_data["http://swapi.co/resource/human/1"]
        self.assertEqual(luke["label"], "Luke Skywalker")
        self.assertEqual(len(luke["relationships"]), 2)
        self.assertIsInstance(luke["relationships"][0], Relationship)
        self.assertEqual(luke["relationships"][0].target, "Darth Vader")
        self.assertEqual(luke["relationships"][0].type, RelationshipType.FAMILY)
        
        self.assertIsInstance(luke["semantics"], SemanticProfile)
        self.assertEqual(luke["semantics"].traits, ["Brave", "Impulsive"])

        r2 = loaded_data["http://swapi.co/resource/droid/2"]
        self.assertEqual(r2["relationships"], [])
        self.assertIsNone(r2["semantics"])

    def test_get_methods(self):
        dummy_data = {
            "uri1": {
                "uri": "uri1", 
                "relationships": [Relationship(target="t", type=RelationshipType.ALLY, details="d")]
            }
        }
        self.store.save_data(dummy_data, str(self.test_file))
        
        # Test get_character
        char = self.store.get_character("uri1")
        self.assertIsNotNone(char)
        self.assertEqual(char["uri"], "uri1")
        
        # Test get_all_characters
        all_chars = self.store.get_all_characters()
        self.assertEqual(len(all_chars), 1)
        
        # Test get_relationships
        rels = self.store.get_relationships("uri1")
        self.assertEqual(len(rels), 1)
        self.assertEqual(rels[0].type, RelationshipType.ALLY)

if __name__ == '__main__':
    unittest.main()
