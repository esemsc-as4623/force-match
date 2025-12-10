from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Type, Optional
from enum import Enum

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
