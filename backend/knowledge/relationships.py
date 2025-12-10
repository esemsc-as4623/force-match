from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import re

class RelationshipType(Enum):
    FAMILY = "FAMILY"
    MASTER_APPRENTICE = "MASTER_APPRENTICE"
    RIVAL = "RIVAL"
    ALLY = "ALLY"
    FACTION_MEMBER = "FACTION_MEMBER"
    UNKNOWN = "UNKNOWN"

@dataclass
class Relationship:
    target: str
    type: RelationshipType
    details: str

@dataclass
class SemanticProfile:
    traits: List[str] = field(default_factory=list)
    motivations: List[str] = field(default_factory=list)
    role: str = ""

class RelationshipClassifier:
    def __init__(self):
        self.patterns = {
            RelationshipType.FAMILY: [
                r"son of", r"daughter of", r"father of", r"mother of", r"brother of", r"sister of", r"parent of", r"child of", r"sibling of", r"cousin of", r"uncle of", r"aunt of", r"nephew of", r"niece of", r"grandfather of", r"grandmother of", r"grandson of", r"granddaughter of", r"wife of", r"husband of", r"spouse of"
            ],
            RelationshipType.MASTER_APPRENTICE: [
                r"master of", r"apprentice of", r"padawan of", r"mentor of", r"student of", r"teacher of", r"trained by", r"trained"
            ],
            RelationshipType.RIVAL: [
                r"rival of", r"enemy of", r"opponent of", r"fought against", r"killed by", r"killed"
            ],
            RelationshipType.ALLY: [
                r"ally of", r"friend of", r"partner of", r"colleague of", r"fought with", r"helped"
            ],
            RelationshipType.FACTION_MEMBER: [
                r"member of", r"leader of", r"served in", r"belongs to"
            ]
        }

    def classify(self, text: str) -> List[Relationship]:
        relationships = []
        if not text:
            return relationships
            
        # Simple sentence splitting
        sentences = re.split(r'[.!?]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            found_match = False
            for rel_type, patterns in self.patterns.items():
                for pattern in patterns:
                    # Regex to find "Target is [pattern] Source" or "Source is [pattern] Target"
                    # We assume the text describes the subject's relationships.
                    # So "son of Vader" -> Target: Vader
                    
                    regex = re.compile(f"{pattern}\\s+([A-Z][a-zA-Z\\s]+)", re.IGNORECASE)
                    match = regex.search(sentence)
                    if match:
                        target = match.group(1).strip()
                        # Clean up target (remove trailing words if they look like noise)
                        target = self._clean_target(target)
                        
                        relationships.append(Relationship(
                            target=target,
                            type=rel_type,
                            details=pattern
                        ))
                        found_match = True
                        break # Stop checking patterns for this sentence if one matches
                if found_match:
                    break
                    
        return relationships

    def _clean_target(self, target: str) -> str:
        # Stop at common conjunctions or prepositions if captured by greedy regex
        stop_words = [" and ", " but ", " who ", " which ", " when ", " where ", " with ", " for ", " to ", " in ", " on ", " at "]
        for word in stop_words:
            if word in target:
                target = target.split(word)[0]
        return target.strip()

class SemanticAnalyzer:
    def analyze(self, text: str) -> SemanticProfile:
        profile = SemanticProfile()
        
        if not text:
            return profile
            
        # Simple keyword extraction for traits and motivations
        
        text_lower = text.lower()
        
        # Traits
        potential_traits = ["brave", "loyal", "wise", "evil", "good", "cunning", "strong", "weak", "fearful", "heroic", "villainous", "ambitious", "reckless", "calm", "angry"]
        for trait in potential_traits:
            if trait in text_lower:
                profile.traits.append(trait)
                
        # Motivations
        if "save" in text_lower or "protect" in text_lower:
            profile.motivations.append("protection")
        if "power" in text_lower or "rule" in text_lower:
            profile.motivations.append("power")
        if "justice" in text_lower:
            profile.motivations.append("justice")
        if "peace" in text_lower:
            profile.motivations.append("peace")
        if "revenge" in text_lower:
            profile.motivations.append("revenge")
        if "freedom" in text_lower:
            profile.motivations.append("freedom")
            
        # Role
        if "jedi" in text_lower:
            profile.role = "Jedi"
        elif "sith" in text_lower:
            profile.role = "Sith"
        elif "senator" in text_lower:
            profile.role = "Senator"
        elif "pilot" in text_lower:
            profile.role = "Pilot"
        elif "bounty hunter" in text_lower:
            profile.role = "Bounty Hunter"
        elif "princess" in text_lower:
            profile.role = "Princess"
        elif "emperor" in text_lower:
            profile.role = "Emperor"
        elif "general" in text_lower:
            profile.role = "General"
        else:
            profile.role = "Unknown"
            
        return profile
