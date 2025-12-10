from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Type, Optional
from enum import Enum
from backend.knowledge.relationships import RelationshipType

@dataclass
class ConstraintViolation:
    """
    Represents a violation of a matching constraint.
    """
    constraint_name: str
    description: str
    severity: str = "BLOCKING"  # BLOCKING, WARNING, INFO

class Constraint(ABC):
    """
    Abstract base class for all matching constraints.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the constraint."""
        pass

    @property
    def description(self) -> str:
        """Description of what the constraint checks."""
        return ""

    @abstractmethod
    def validate(self, giver: Dict[str, Any], receiver: Dict[str, Any], enriched_data: Dict[str, Any]) -> List[ConstraintViolation]:
        """
        Validates the constraint against the giver and receiver.
        
        Args:
            giver: The character data for the giver.
            receiver: The character data for the receiver.
            enriched_data: The full enriched dataset (context).
            
        Returns:
            A list of ConstraintViolation objects. Empty list if valid.
        """
        pass

class ConstraintRegistry:
    """
    Registry to manage and instantiate available constraints.
    """
    _registry: Dict[str, Type[Constraint]] = {}

    @classmethod
    def register(cls, constraint_cls: Type[Constraint]):
        """Registers a constraint class."""
        instance = constraint_cls() # Instantiate to get the name property
        cls._registry[instance.name] = constraint_cls
        return constraint_cls

    @classmethod
    def get_constraint(cls, name: str) -> Optional[Type[Constraint]]:
        """Retrieves a constraint class by name."""
        return cls._registry.get(name)

    @classmethod
    def get_all_constraints(cls) -> Dict[str, Type[Constraint]]:
        """Returns all registered constraints."""
        return cls._registry.copy()

    @classmethod
    def instantiate_constraints(cls, names: List[str]) -> List[Constraint]:
        """
        Instantiates a list of constraints by name.
        Ignores unknown names.
        """
        constraints = []
        for name in names:
            constraint_cls = cls.get_constraint(name)
            if constraint_cls:
                constraints.append(constraint_cls())
        return constraints

@ConstraintRegistry.register
class RelationshipAvoidanceConstraint(Constraint):
    """
    Prevents matching characters with specific existing relationships.
    """
    @property
    def name(self) -> str:
        return "relationship_avoidance"

    @property
    def description(self) -> str:
        return "Prevents matching characters who are family, master/apprentice, or rivals."

    def validate(self, giver: Dict[str, Any], receiver: Dict[str, Any], enriched_data: Dict[str, Any]) -> List[ConstraintViolation]:
        violations = []
        
        # Get receiver identifier (name or URI)
        receiver_name = receiver.get("label", receiver.get("name", ""))
        receiver_uri = next((k for k, v in enriched_data.items() if v == receiver), None)
        
        relationships = giver.get("relationships", [])
        
        avoid_types = {
            RelationshipType.FAMILY.value,
            RelationshipType.MASTER_APPRENTICE.value,
            RelationshipType.RIVAL.value
        }
        
        for rel in relationships:
            target = ""
            rel_type = ""
            
            if isinstance(rel, dict):
                target = rel.get("target", "")
                rel_type = rel.get("type", "")
            elif hasattr(rel, "target") and hasattr(rel, "type"):
                target = rel.target
                rel_type = rel.type.value if hasattr(rel.type, "value") else str(rel.type)
                
            # Check if this relationship targets the receiver
            if target and (target == receiver_name or (receiver_uri and target == receiver_uri)):
                if rel_type in avoid_types:
                    violations.append(ConstraintViolation(
                        constraint_name=self.name,
                        description=f"Giver has a {rel_type} relationship with the receiver.",
                        severity="BLOCKING"
                    ))
                    
        return violations

@ConstraintRegistry.register
class FactionBalanceConstraint(Constraint):
    """
    Checks faction compatibility. 
    Default behavior: Flags if giver and receiver are in the same faction (encouraging diversity).
    """
    @property
    def name(self) -> str:
        return "faction_balance"

    @property
    def description(self) -> str:
        return "Checks if giver and receiver belong to the same faction."

    def validate(self, giver: Dict[str, Any], receiver: Dict[str, Any], enriched_data: Dict[str, Any]) -> List[ConstraintViolation]:
        violations = []
        
        def get_factions(char_data: Dict[str, Any]) -> set:
            factions = set()
            relationships = char_data.get("relationships", [])
            for rel in relationships:
                target = ""
                rel_type = ""
                if isinstance(rel, dict):
                    target = rel.get("target", "")
                    rel_type = rel.get("type", "")
                elif hasattr(rel, "target") and hasattr(rel, "type"):
                    target = rel.target
                    rel_type = rel.type.value if hasattr(rel.type, "value") else str(rel.type)
                
                if rel_type == RelationshipType.FACTION_MEMBER.value:
                    factions.add(target)
            
            # Also check for direct 'affiliations' list if it exists
            if "affiliations" in char_data and isinstance(char_data["affiliations"], list):
                factions.update(char_data["affiliations"])
                
            return factions

        giver_factions = get_factions(giver)
        receiver_factions = get_factions(receiver)
        
        common_factions = giver_factions.intersection(receiver_factions)
        
        if common_factions:
            violations.append(ConstraintViolation(
                constraint_name=self.name,
                description=f"Giver and receiver are both in: {', '.join(common_factions)}",
                severity="WARNING" # Default to WARNING for diversity check
            ))
            
        return violations

@ConstraintRegistry.register
class HomeworldDiversityConstraint(Constraint):
    """
    Ensures giver and receiver are from different homeworlds.
    """
    @property
    def name(self) -> str:
        return "homeworld_diversity"

    @property
    def description(self) -> str:
        return "Checks if giver and receiver are from the same homeworld."

    def validate(self, giver: Dict[str, Any], receiver: Dict[str, Any], enriched_data: Dict[str, Any]) -> List[ConstraintViolation]:
        violations = []
        
        giver_homeworld = giver.get("homeworld")
        receiver_homeworld = receiver.get("homeworld")
        
        if giver_homeworld and receiver_homeworld and giver_homeworld == receiver_homeworld:
            violations.append(ConstraintViolation(
                constraint_name=self.name,
                description=f"Both characters are from {giver_homeworld}.",
                severity="INFO" # Usually just for diversity, not blocking
            ))
            
        return violations
