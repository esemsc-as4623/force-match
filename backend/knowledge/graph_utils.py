import networkx as nx
from typing import Dict, Any, List, Optional
import logging
from .relationships import Relationship

logger = logging.getLogger(__name__)

def build_graph(characters: Dict[str, Any]) -> nx.Graph:
    """
    Builds a NetworkX graph from the characters dictionary.
    Nodes are character names (or URIs if names are not unique/available).
    Edges represent relationships.
    """
    G = nx.Graph()
    
    for char_uri, char_data in characters.items():
        # Use label (name) as the node identifier if available, otherwise URI
        source_name = char_data.get("label", char_uri)
        
        if not G.has_node(source_name):
            G.add_node(source_name, uri=char_uri)
            
        # Add edges from structured relationships
        relationships = char_data.get("relationships", [])
        
        # relationships might be a list of Relationship objects or raw strings if not yet processed
        # We assume they are Relationship objects as per the plan
        
        for rel in relationships:
            if isinstance(rel, Relationship):
                target_name = rel.target
                rel_type = rel.type.value
                
                # Add target node if it doesn't exist
                if not G.has_node(target_name):
                    G.add_node(target_name)
                
                # Add edge
                G.add_edge(source_name, target_name, relation=rel_type)
            elif isinstance(rel, dict) and "target" in rel:
                 # Handle case where it might be a dict
                target_name = rel["target"]
                rel_type = rel.get("type", "UNKNOWN")
                
                if not G.has_node(target_name):
                    G.add_node(target_name)
                
                G.add_edge(source_name, target_name, relation=rel_type)

    logger.info(f"Built graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    return G

def calculate_degree(graph: nx.Graph, source: str, target: str) -> float:
    """
    Calculates the degree of separation (shortest path length) between two characters.
    Returns float('inf') if no path exists.
    """
    if not graph.has_node(source) or not graph.has_node(target):
        logger.warning(f"One or both nodes not found in graph: {source}, {target}")
        return float('inf')
        
    try:
        # shortest_path_length returns the number of edges
        degree = nx.shortest_path_length(graph, source=source, target=target)
        return float(degree)
    except nx.NetworkXNoPath:
        return float('inf')

def get_path(graph: nx.Graph, source: str, target: str) -> List[str]:
    """
    Returns the shortest path between two characters as a list of node names.
    """
    if not graph.has_node(source) or not graph.has_node(target):
        return []
        
    try:
        return nx.shortest_path(graph, source=source, target=target)
    except nx.NetworkXNoPath:
        return []
