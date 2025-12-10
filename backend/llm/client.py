import os
import logging
import httpx
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.base_url = os.getenv("LLM_ENDPOINT", "http://127.0.0.1:1234/v1")
        self.model = os.getenv("LLM_MODEL", "deepseek-r1-0528-qwen3-8b")
        self.timeout = 60.0  # seconds

    async def generate_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Optional[str]:
        """
        Sends a chat completion request to the LLM.
        """
        # Ensure base_url doesn't end with slash if we append /chat/completions
        base_url = self.base_url.rstrip('/')
        url = f"{base_url}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 500,
            "stream": False
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"Sending request to LLM: {url}")
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.warning("LLM response did not contain choices.")
                    return None
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting {e.request.url!r}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Error response {e.response.status_code} while requesting {e.request.url!r}: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during LLM call: {e}")
            return None

    async def get_gift_suggestions(self, giver: Dict[str, Any], receiver: Dict[str, Any]) -> List[str]:
        """
        Generates 3 humorous gift suggestions based on giver and receiver profiles.
        """
        prompt = self._construct_gift_prompt(giver, receiver)
        messages = [
            {"role": "system", "content": "You are a helpful assistant in the Star Wars universe. You provide humorous and in-universe gift recommendations."},
            {"role": "user", "content": prompt}
        ]
        
        logger.info(f"Requesting gift suggestions for {giver.get('name')} -> {receiver.get('name')}")
        response_text = await self.generate_completion(messages, temperature=0.8)
        
        if not response_text:
            logger.warning("LLM returned no text for gift suggestions.")
            return []
            
        return self._parse_gift_list(response_text)

    def _construct_gift_prompt(self, giver: Dict[str, Any], receiver: Dict[str, Any]) -> str:
        giver_name = giver.get("name", "Unknown")
        giver_species = giver.get("species", "Unknown Species")
        giver_traits = ", ".join(giver.get("traits", [])) if giver.get("traits") else "None"
        
        receiver_name = receiver.get("name", "Unknown")
        receiver_species = receiver.get("species", "Unknown Species")
        receiver_traits = ", ".join(receiver.get("traits", [])) if receiver.get("traits") else "None"
        
        return (
            f"Suggest 3 humorous and in-universe gift ideas for {giver_name} ({giver_species}) "
            f"to give to {receiver_name} ({receiver_species}).\n\n"
            f"Giver Traits: {giver_traits}\n"
            f"Receiver Traits: {receiver_traits}\n\n"
            "The gifts should be funny, ironic, or oddly specific to their lore. "
            "For example, Vader giving Luke a 'Hand Replacement Coupon'.\n"
            "Return ONLY the list of 3 gifts, one per line, without numbering or extra text."
        )

    def _parse_gift_list(self, text: str) -> List[str]:
        lines = text.strip().split('\n')
        gifts = []
        for line in lines:
            cleaned = line.strip()
            # Remove numbering like "1. ", "2. ", "- ", "* "
            if cleaned.startswith(tuple("0123456789.-*")):
                 cleaned = cleaned.lstrip("0123456789.-* ")
            if cleaned:
                gifts.append(cleaned)
        return gifts[:3]
