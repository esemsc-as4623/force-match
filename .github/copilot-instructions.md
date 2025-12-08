# Copilot Instructions for force-match

## Project Overview
This project builds a Cognee knowledge graph from Star Wars (SWAPI) RDF data stored in Turtle (TTL) format. The system uses a local LLM via LM Studio for both text generation and embeddings to process semantic relationships in the data.

## Architecture & Key Components

### Data Pipeline
- **Input**: `data/data.ttl` - 4,652 lines of RDF/Turtle format Star Wars data (planets, characters, species, films)
- **Processor**: Cognee knowledge graph engine with LanceDB (vector store) and Kuzu (graph database)
- **Main Script**: `load_to_cognee.py` - orchestrates data ingestion and graph construction

### LLM Infrastructure (Local/On-Device)
- **Provider**: LM Studio running locally on port 1234
- **LLM Model**: deepseek-r1-0528-qwen3-8b for text generation
- **Embedding Model**: nomic-embed-text-v1.5-GGUF for semantic embeddings
- **Critical**: Both LLM and embedding providers MUST be configured in `.env` - Cognee defaults to OpenAI if only one is set

## Environment Setup

### Virtual Environment
**Always activate the venv before running commands:**
```bash
source .venv/bin/activate
```

### Configuration (.env)
```bash
# LLM Configuration
LLM_PROVIDER="custom"
LLM_MODEL="lm_studio/deepseek/deepseek-r1-0528-qwen3-8b"
LLM_ENDPOINT="http://127.0.0.1:1234/v1"
LLM_INSTRUCTOR_MODE="json_schema_mode"

# Embedding Configuration (REQUIRED - do not omit)
EMBEDDING_PROVIDER="custom"
EMBEDDING_MODEL="lm_studio/nomic-ai/nomic-embed-text-v1.5-GGUF"
EMBEDDING_ENDPOINT="http://127.0.0.1:1234/v1"
```

## Critical Workflows

### Running the Data Pipeline
```bash
source .venv/bin/activate
python load_to_cognee.py
```

**Expected behavior:**
1. Loads environment variables from `.env`
2. Prunes existing Cognee data and metadata
3. Reads TTL file (should report ~4,652 lines of content)
4. Adds data to Cognee as "star-wars-ttl" dataset
5. Runs `cognify()` to build the knowledge graph

### LM Studio Prerequisites
Before running the pipeline, ensure:
1. LM Studio application is running
2. The LLM model is loaded in LM Studio
3. The embedding model is available (may need separate slot or switching)
4. Local server is started on port 1234 (check LM Studio's "Local Server" tab)

### Common Issues

**SQLite Import Error**: If you see `Symbol not found: _sqlite3_enable_load_extension`, the Conda Python's sqlite3 is incompatible with macOS system SQLite. Fix:
```bash
conda install -y sqlite
```

**Connection Refused (port 1234)**: LM Studio server is not running. Start it in LM Studio UI.

**OpenAI API Key Error**: Missing embedding configuration in `.env`. Both `LLM_*` and `EMBEDDING_*` variables are required.

## Data Format Patterns

### RDF/Turtle Structure
The TTL file uses SWAPI vocabulary with these key classes:
- `voc:Character`, `voc:Planet`, `voc:Species`
- `voc:Mammal`, `voc:Reptile`, `voc:Sentient`, etc.
- Prefix: `<https://swapi.co/resource/>`

Example pattern:
```turtle
<https://swapi.co/resource/planet/13> a voc:Planet ;
    voc:film <https://swapi.co/resource/film/6> ;
    voc:resident <https://swapi.co/resource/human/10> .
```

## Dependencies
- **Cognee 0.4.1**: Knowledge graph framework
- **LiteLLM**: Multi-provider LLM interface
- **LanceDB**: Vector database for embeddings
- **Kuzu**: Graph database backend
- **RDFLib**: RDF/Turtle parsing (if needed for preprocessing)

## Development Notes
- This is macOS environment (conda-based Python 3.12.4)
- Virtual environment is in `.venv/` directory
- Cognee stores data in `.venv/lib/python3.12/site-packages/cognee/.cognee_system/databases/`
