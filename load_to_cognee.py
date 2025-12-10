#!/usr/bin/env python3
"""
Script to load TTL (Turtle) RDF data into Cognee knowledge graph.
Reads the data.ttl file, parses it to extract character data, and processes it through Cognee.
"""

import asyncio
import cognee
from cognee import SearchType
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import rdflib
from rdflib import RDF, RDFS

# Import health check
import sys
sys.path.append(str(Path(__file__).parent)) # Ensure backend module is found
from backend.utils.lm_studio_health import check_lm_studio_health

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_rdf_data(file_path):
    """
    Parses the RDF TTL file and extracts character attributes.
    Returns a dictionary of characters and their attributes.
    """
    logger.info(f"Parsing RDF file: {file_path}")
    g = rdflib.Graph()
    g.parse(file_path, format="turtle")
    
    characters = {}
    
    # SPARQL query to get all properties of characters
    query = """
    PREFIX voc: <https://swapi.co/vocabulary/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?character ?p ?o
    WHERE {
        ?character a voc:Character .
        ?character ?p ?o .
    }
    """
    
    results = g.query(query)
    
    for row in results:
        char_uri = str(row.character)
        pred = str(row.p)
        obj = str(row.o)
        
        if char_uri not in characters:
            characters[char_uri] = {"uri": char_uri}
            
        # Simplify predicate name (remove namespace)
        if "vocabulary/" in pred:
            key = pred.split("vocabulary/")[-1]
        elif "rdf-schema#" in pred:
            key = pred.split("rdf-schema#")[-1]
        elif "1999/02/22-rdf-syntax-ns#" in pred:
            key = pred.split("1999/02/22-rdf-syntax-ns#")[-1]
        else:
            key = pred
            
        # Handle multiple values for the same predicate (e.g. films)
        if key in characters[char_uri]:
            if isinstance(characters[char_uri][key], list):
                characters[char_uri][key].append(obj)
            else:
                characters[char_uri][key] = [characters[char_uri][key], obj]
        else:
            characters[char_uri][key] = obj
            
    logger.info(f"Extracted {len(characters)} characters from RDF.")
    return characters

async def extract_relationships(character_name):
    """
    Queries the Cognee knowledge graph for character relationships.
    """
    try:
        query = f"Who is {character_name} related to? List family, master, apprentice, allies, and rivals based on the data."
        # Use GRAPH_COMPLETION to leverage the graph structure
        results = await cognee.search(query, query_type=SearchType.GRAPH_COMPLETION)
        return results
    except Exception as e:
        logger.error(f"Error extracting relationships for {character_name}: {e}")
        return []

async def main():
    # Load environment variables
    load_dotenv()
    
    # Run Health Check
    logger.info("Running LM Studio health check...")
    health_status = await check_lm_studio_health()
    if not health_status:
        logger.error("LM Studio health check failed. Exiting.")
        return

    # Path to the TTL file
    ttl_file_path = Path(__file__).parent / "data" / "data.ttl"
    
    # Parse RDF Data
    characters = parse_rdf_data(ttl_file_path)
    
    # Debug: Print first character to verify
    if characters:
        first_char_key = list(characters.keys())[0]
        logger.info(f"Sample character data ({first_char_key}): {characters[first_char_key]}")

    print(f"Loading TTL file: {ttl_file_path}")
    print(f"Using LLM provider: {os.getenv('LLM_PROVIDER')}")
    
    # Prune existing data and metadata in Cognee
    print("\nResetting Cognee data...")
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)
    
    # Read the TTL file content for Cognee
    with open(ttl_file_path, 'r', encoding='utf-8') as f:
        ttl_content = f.read()
    
    print(f"Read {len(ttl_content)} characters from TTL file")
    
    # Add the TTL content to Cognee
    print("Adding data to Cognee...")
    await cognee.add(ttl_content, dataset_name="star-wars-ttl")
    
    # Process the data to build the knowledge graph
    print("Building knowledge graph (cognifying)...")
    await cognee.cognify()
    
    logger.info("Cognee processing complete.")

    # Step 3: Extract Relationships
    logger.info("Extracting relationships from Knowledge Graph...")
    
    # Limit to a subset for demonstration/performance if needed, or process all
    # For now, we'll process all but with a counter to track progress
    count = 0
    total = len(characters)
    
    for char_uri, char_data in characters.items():
        count += 1
        name = char_data.get("label", "Unknown")
        if name == "Unknown":
            continue
            
        logger.info(f"[{count}/{total}] Extracting relationships for {name}...")
        relationships = await extract_relationships(name)
        
        # Store relationships in the character data structure
        # relationships is likely a list of text results from GRAPH_COMPLETION
        char_data["relationships"] = relationships
        
        logger.debug(f"Relationships for {name}: {relationships}")

    logger.info("Relationship extraction complete.")
    
    # Debug: Print a sample with relationships
    if characters:
        first_char_key = list(characters.keys())[0]
        logger.info(f"Enriched character data ({characters[first_char_key].get('label')}): {characters[first_char_key]}")

if __name__ == '__main__':
    asyncio.run(main())
