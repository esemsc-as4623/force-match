from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Type, Optional
from enum import Enum
from backend.knowledge.relationships import RelationshipType
from backend.knowledge.graph_utils import build_graph, calculate_degree

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

@ConstraintRegistry.register
class DegreeOfSeparationConstraint(Constraint):
    """
    Ensures giver and receiver are within (or outside) a specific distance in the graph.
    Default: Checks if they are too close (e.g. distance < 2).
    """
    @property
    def name(self) -> str:
        return "degree_of_separation"

    @property
    def description(self) -> str:
        return "Checks the degree of separation between characters."

    def validate(self, giver: Dict[str, Any], receiver: Dict[str, Any], enriched_data: Dict[str, Any]) -> List[ConstraintViolation]:
        violations = []
        
        # We need to build the graph to calculate degree. 
        # In a real production system, the graph might be pre-built or cached.
        # For this implementation, we build it on the fly.
        
        graph = build_graph(enriched_data)
        
        giver_name = giver.get("label", giver.get("name", ""))
        receiver_name = receiver.get("label", receiver.get("name", ""))
        
        degree = calculate_degree(graph, giver_name, receiver_name)
        
        # Constraint: Avoid if too close (e.g. direct connection or 1 hop)
        min_distance = 2
        
        if degree < min_distance:
             violations.append(ConstraintViolation(
                constraint_name=self.name,
                description=f"Characters are too close in the graph (degree {degree} < {min_distance}).",
                severity="WARNING"
            ))
            
        return violations

@ConstraintRegistry.register
class DirectContactAvoidanceConstraint(Constraint):
    """
    Checks for direct interaction history (if available in semantics).
    """
    @property
    def name(self) -> str:
        return "direct_contact_avoidance"

    @property
    def description(self) -> str:
        return "Checks if characters have a history of direct contact."

    def validate(self, giver: Dict[str, Any], receiver: Dict[str, Any], enriched_data: Dict[str, Any]) -> List[ConstraintViolation]:
        violations = []
        
        # Check semantics for mentions of the other character
        giver_semantics = giver.get("semantics", {})
        receiver_name = receiver.get("label", receiver.get("name", ""))
        
        if not giver_semantics or not receiver_name:
            return violations
            
        # If semantics is a dict (from JSON) or SemanticProfile object
        history = []
        if isinstance(giver_semantics, dict):
            history = giver_semantics.get("traits", []) + giver_semantics.get("motivations", [])
        elif hasattr(giver_semantics, "traits"):
             history = giver_semantics.traits + giver_semantics.motivations
             
        for text in history:
            if receiver_name.lower() in text.lower():
                 violations.append(ConstraintViolation(
                    constraint_name=self.name,
                    description=f"Giver's semantic profile mentions receiver: '{text[:50]}...'",
                    severity="WARNING"
                ))
                
        return violations

@ConstraintRegistry.register
class TimelineEraConstraint(Constraint):
    """
    Checks if characters belong to compatible eras.
    """
    @property
    def name(self) -> str:
        return "timeline_era"

    @property
    def description(self) -> str:
        return "Checks if characters are from compatible timeline eras."

    def validate(self, giver: Dict[str, Any], receiver: Dict[str, Any], enriched_data: Dict[str, Any]) -> List[ConstraintViolation]:
        violations = []
        
        # In SWAPI, we might have birth_year.
        # We can try to parse it. e.g. "19BBY"
        
        def parse_year(year_str: str) -> float:
            if not year_str or year_str == "unknown":
                return None
            try:
                if "BBY" in year_str:
                    return -float(year_str.replace("BBY", ""))
                elif "ABY" in year_str:
                    return float(year_str.replace("ABY", ""))
                else:
                    return float(year_str) # Assume ABY if no suffix? Or just raw number
            except ValueError:
                return None

        giver_year = parse_year(giver.get("birth_year"))
        receiver_year = parse_year(receiver.get("birth_year"))
        
        if giver_year is not None and receiver_year is not None:
            # If birth years are more than 100 years apart, maybe they can't meet?
            # Unless they are long-lived species (Yoda).
            # This is a simple heuristic.
            
            diff = abs(giver_year - receiver_year)
            if diff > 60: # Arbitrary generation gap
                 violations.append(ConstraintViolation(
                    constraint_name=self.name,
                    description=f"Large age gap ({diff} years) between characters.",
                    severity="INFO"
                ))
        
        return violations

@ConstraintRegistry.register
class AllegianceChainConstraint(Constraint):
    """
    Checks for complex allegiance patterns.
    """
    @property
    def name(self) -> str:
        return "allegiance_chain"

    @property
    def description(self) -> str:
        return "Checks for conflicting allegiance chains."

    def validate(self, giver: Dict[str, Any], receiver: Dict[str, Any], enriched_data: Dict[str, Any]) -> List[ConstraintViolation]:
        violations = []
        # Placeholder for advanced logic. 
        # Could check if Giver -> Master -> Enemy -> Receiver
        return violations
