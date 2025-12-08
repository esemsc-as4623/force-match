#!/usr/bin/env python3
"""
Script to load TTL (Turtle) RDF data into Cognee knowledge graph.
Reads the data.ttl file and processes it through Cognee.
"""

import asyncio
import cognee
import os
from pathlib import Path
from dotenv import load_dotenv


async def main():
    # Load environment variables from .env file
    # Cognee will automatically use LLM_PROVIDER, LLM_MODEL, LLM_ENDPOINT, LLM_API_KEY
    load_dotenv()
    
    # Path to the TTL file
    ttl_file_path = Path(__file__).parent / "data" / "data.ttl"
    
    print(f"Loading TTL file: {ttl_file_path}")
    print(f"Using LLM provider: {os.getenv('LLM_PROVIDER')}")
    print(f"Using LLM endpoint: {os.getenv('LLM_ENDPOINT')}")
    print(f"Using LLM model: {os.getenv('LLM_MODEL')}")
    
    # Prune existing data and metadata in Cognee
    print("\nResetting Cognee data...")
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)
    
    # Read the TTL file content
    with open(ttl_file_path, 'r', encoding='utf-8') as f:
        ttl_content = f.read()
    
    print(f"Read {len(ttl_content)} characters from TTL file")
    
    # Add the TTL content to Cognee
    print("Adding data to Cognee...")
    await cognee.add(ttl_content, dataset_name="star-wars-ttl")
    
    # Process the data to build the knowledge graph
    print("Building knowledge graph (cognifying)...")
    await cognee.cognify()

if __name__ == '__main__':
    asyncio.run(main())
