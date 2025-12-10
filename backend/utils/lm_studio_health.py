import asyncio
import os
import logging
import httpx
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def check_lm_studio_health():
    """
    Verifies the availability of LM Studio LLM and Embedding endpoints.
    """
    load_dotenv()
    
    verbose = os.getenv("VERBOSE_LOGGING", "false").lower() == "true"
    if verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled.")

    llm_endpoint = os.getenv("LLM_ENDPOINT", "http://127.0.0.1:1234/v1")
    embedding_endpoint = os.getenv("EMBEDDING_ENDPOINT", "http://127.0.0.1:1234/v1")
    
    llm_model = os.getenv("LLM_MODEL", "deepseek-r1-0528-qwen3-8b")
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-nomic-embed-text-v1.5")

    # Strip /v1 if present for base url checks, but we usually hit /v1/models or specific endpoints
    # LM Studio usually serves at http://localhost:1234/v1
    
    logger.info(f"Checking LM Studio health at {llm_endpoint}...")
    logger.debug(f"LLM Model: {llm_model}")
    logger.debug(f"Embedding Model: {embedding_model}")

    # Increased timeout to 60s to account for model loading times
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Check LLM Endpoint (Chat Completions)
        try:
            logger.debug(f"Testing LLM endpoint: {llm_endpoint}/chat/completions")
            llm_payload = {
                "model": llm_model,
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 1
            }
            response = await client.post(f"{llm_endpoint}/chat/completions", json=llm_payload)
            response.raise_for_status()
            logger.info(f"✅ LLM Endpoint ({llm_model}) is reachable and responding.")
            logger.debug(f"LLM Response: {response.json()}")
        except httpx.ConnectError:
            logger.error(f"❌ Failed to connect to LLM endpoint at {llm_endpoint}. Is LM Studio running?")
            return False
        except httpx.TimeoutException:
            logger.error(f"❌ Request timed out checking LLM endpoint. The model might be loading or running slowly.")
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ LLM Endpoint returned error {e.response.status_code}: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error checking LLM endpoint: {str(e)}")
            return False

        # 2. Check Embedding Endpoint
        try:
            logger.debug(f"Testing Embedding endpoint: {embedding_endpoint}/embeddings")
            embed_payload = {
                "model": embedding_model,
                "input": "ping"
            }
            response = await client.post(f"{embedding_endpoint}/embeddings", json=embed_payload)
            response.raise_for_status()
            logger.info(f"✅ Embedding Endpoint ({embedding_model}) is reachable and responding.")
            logger.debug(f"Embedding Response: {response.json()}")
        except httpx.ConnectError:
            logger.error(f"❌ Failed to connect to Embedding endpoint at {embedding_endpoint}. Is LM Studio running?")
            return False
        except httpx.TimeoutException:
            logger.error(f"❌ Request timed out checking Embedding endpoint. The model might be loading or running slowly.")
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Embedding Endpoint returned error {e.response.status_code}: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error checking Embedding endpoint: {str(e)}")
            return False

    logger.info("🎉 LM Studio health check passed!")
    return True

if __name__ == "__main__":
    try:
        asyncio.run(check_lm_studio_health())
    except KeyboardInterrupt:
        pass
