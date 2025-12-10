# Force Match - Star Wars Knowledge Graph

This project builds a Cognee knowledge graph from Star Wars (SWAPI) RDF data stored in Turtle (TTL) format. The system uses a local LLM via LM Studio for both text generation and embeddings to process semantic relationships in the data.

## LM Studio Setup

This project relies on a local LM Studio instance to provide LLM and Embedding capabilities.

### 1. Required Models
Ensure you have the following models downloaded in LM Studio:
- **Text Generation (LLM):** `deepseek-r1-0528-qwen3-8b` (or a similar model suitable for your hardware, e.g., 16GB RAM).
- **Embeddings:** `nomic-embed-text-v1.5-GGUF` (Required for semantic search and graph construction).

### 2. Server Startup Instructions
1. Open **LM Studio**.
2. Go to the **Local Server** tab (double-headed arrow icon).
3. **Load the LLM:** Select `deepseek-r1-0528-qwen3-8b` from the top dropdown.
4. **Load the Embedding Model:**
   - **Recommended Method (CLI):** Open a terminal and run:
     ```bash
     lms load text-embedding-nomic-embed-text-v1.5
     ```
     *Note: If the command fails, run `lms ls` to see available models and copy the exact name.*
   - **Alternative (GUI):** In newer versions of LM Studio, look for a "Text Embedding Model" slot in the Server tab.
5. **Start Server:** Click the green **Start Server** button.
   - Ensure the server is running on **Port 1234** (default).
   - The endpoint should be `http://localhost:1234/v1`.

### 3. Health Check Usage
Before running the data pipeline, verify that LM Studio is correctly configured and reachable.

Run the health check script:
```bash
# Activate virtual environment first
source .venv/bin/activate

# Run the health check
python backend/utils/lm_studio_health.py
```

**Verbose Logging:**
To see detailed connection info and payloads, run with `VERBOSE_LOGGING=true`:
```bash
VERBOSE_LOGGING=true python backend/utils/lm_studio_health.py
```

### 4. Troubleshooting Tips

- **Connection Refused:**
  - Is LM Studio running?
  - Is the Local Server started?
  - Is it listening on port 1234?

- **Model Not Found / 404 Error:**
  - Check that the `LLM_MODEL` and `EMBEDDING_MODEL` in your `.env` file match exactly what is loaded in LM Studio.
  - You can copy the model ID from LM Studio's server logs or model card.

- **Timeout:**
  - The model might be taking too long to load or process. Try increasing the timeout in `backend/utils/lm_studio_health.py` if your hardware is slow.

- **"Symbol not found: _sqlite3_enable_load_extension" (macOS):**
  - This is a common Python/SQLite issue on macOS. Run `conda install -y sqlite` if using Conda.

## Project Structure
- `load_to_cognee.py`: Main script to ingest data.
- `backend/utils/lm_studio_health.py`: Health check utility.
- `data/`: Contains `data.ttl` (Source data).
- `frontend/`: React frontend application.
