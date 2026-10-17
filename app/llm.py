from . import schemas
from .config import settings
import asyncio
import httpx

async def mock_llm(request:schemas.completionMessage):
    await asyncio.sleep(2)
    return {
        "id": "chatcmpl-mock123",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a fake response from your mock LLM!"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 12, "total_tokens": 22}
    }

async def real_llm(request:schemas.completionMessage):
    model=settings.model
    url = settings.base_url + "/v1/chat/completions"
    body={
        "model":settings.model,
        "messages":[m.model_dump() for m in request.messages],
        "temperature":request.temperature
    }
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(url, json=body)
        if response.status_code >= 400:
             print("OLLAMA REJECTION REASON:", response.text)
        response.raise_for_status()
        return response.json()

async def generate(request:schemas.completionMessage):
    if settings.backend_name=="Ollama":
        return await real_llm(request)
    else:
        return await mock_llm(request)
