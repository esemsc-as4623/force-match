import json
import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from backend.knowledge.relationships import Relationship, RelationshipType, SemanticProfile

logger = logging.getLogger(__name__)

class EnrichedStore:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._is_loaded = False

    def save_data(self, data: Dict[str, Any], filepath: str) -> None:
        """
        Saves the enriched character data to a JSON file.
        Handles serialization of Enums and Dataclasses.
        """
        serialized_data = {}
        for uri, char_data in data.items():
            serialized_char = char_data.copy()
            
            # Serialize relationships
            if "relationships" in serialized_char:
                serialized_rels = []
                for rel in serialized_char["relationships"]:
                    if isinstance(rel, Relationship):
                        rel_dict = asdict(rel)
                        rel_dict["type"] = rel.type.value  # Convert Enum to string
                        serialized_rels.append(rel_dict)
                    elif isinstance(rel, dict):
                         serialized_rels.append(rel) # Already a dict
                serialized_char["relationships"] = serialized_rels
            
            # Serialize semantics
            if "semantics" in serialized_char:
                sem = serialized_char["semantics"]
                if isinstance(sem, SemanticProfile):
                    serialized_char["semantics"] = asdict(sem)
                elif sem is None:
                    serialized_char["semantics"] = None
            
            serialized_data[uri] = serialized_char

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serialized_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Enriched data saved to {filepath}")
        
        # Update cache
        self._cache = data
        self._is_loaded = True

    def load_data(self, filepath: str) -> Dict[str, Any]:
        """
        Loads enriched character data from a JSON file.
        Reconstructs Enums and Dataclasses.
        """
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            return {}

        with open(filepath, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        deserialized_data = {}
        for uri, char_data in raw_data.items():
            deserialized_char = char_data.copy()
            
            # Deserialize relationships
            if "relationships" in deserialized_char:
                deserialized_rels = []
                for rel_dict in deserialized_char["relationships"]:
                    try:
                        # Handle case where type might be a string from JSON
                        rel_type_str = rel_dict.get("type", "UNKNOWN")
                        # Convert string back to Enum
                        try:
                            rel_type = RelationshipType(rel_type_str)
                        except ValueError:
                            rel_type = RelationshipType.UNKNOWN
                            
                        deserialized_rels.append(Relationship(
                            target=rel_dict.get("target", ""),
                            type=rel_type,
                            details=rel_dict.get("details", "")
                        ))
                    except Exception as e:
                        logger.error(f"Error deserializing relationship for {uri}: {e}")
                deserialized_char["relationships"] = deserialized_rels
            
            # Deserialize semantics
            if "semantics" in deserialized_char and deserialized_char["semantics"]:
                sem_dict = deserialized_char["semantics"]
                deserialized_char["semantics"] = SemanticProfile(
                    traits=sem_dict.get("traits", []),
                    motivations=sem_dict.get("motivations", []),
                    role=sem_dict.get("role", "")
                )
            else:
                deserialized_char["semantics"] = None # Ensure it's None if missing or null

            deserialized_data[uri] = deserialized_char

        self._cache = deserialized_data
        self._is_loaded = True
        logger.info(f"Loaded {len(deserialized_data)} characters from {filepath}")
        return deserialized_data

    def get_character(self, uri: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single character by URI."""
        return self._cache.get(uri)

    def get_all_characters(self) -> Dict[str, Any]:
        """Retrieves all characters."""
        return self._cache

    def get_relationships(self, uri: str) -> List[Relationship]:
        """Retrieves relationships for a specific character."""
        char = self.get_character(uri)
        if char and "relationships" in char:
            return char["relationships"]
        return []
