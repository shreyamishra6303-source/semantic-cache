from fastapi import FastAPI,Depends,BackgroundTasks
from . import schemas,database,llm,models
from sqlalchemy.orm import Session
import time
from . embeddings import lifespan, generate_embedding
import hashlib
import json
# Register the lifespan from embeddings.py
app = FastAPI(title="LLM Semantic Cache Proxy", lifespan=lifespan)
models.base.metadata.create_all(bind=database.engine)

def save_log_and_cache(
    prompt: str,
    model_name: str,
    response_text: str,
    vector: list,
    latency: float,
    params_hash: str
):
    # Instantiate a fresh, independent DB session for the background task
    db = database.SessionLocal()
    
    try:
        cache_data = models.cache_entries(
            tenant_id="default",
            model=model_name,
            params_hash=params_hash,
            prompt=prompt,
            response=response_text,
            embedding=vector,
        )
        db.add(cache_data)

        new_log = models.request_log(prompt=prompt, latency=latency)
        db.add(new_log)

        db.commit()
        print("Background save complete!")
    except Exception as e:
        db.rollback()
        print(f"Error in background task: {e}")
    finally:
        db.close()  # Clean up the connection when finished


@app.post("/v1/chat/completions")
async def generate_response(
    request: schemas.completionMessage,
    background_tasks: BackgroundTasks,
):
    start_time = time.perf_counter()

    user_model = request.model
    first_message = request.messages[0].content

    llm_params = {
        "temperature": getattr(request, "temperature", 0.7),
        "max_tokens": getattr(request, "max_tokens", 1024),
        "model": request.model
    }
    params_string = json.dumps(llm_params, sort_keys=True)
    real_params_hash = hashlib.md5(params_string.encode('utf-8')).hexdigest(
    )
    # 1. Generate response from LLM
    response_data = await llm.generate(request)

    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000

    # 2. Extract values and generate vector
    vector = await generate_embedding(first_message)
    assistant_reply = response_data["choices"][0]["message"]["content"]

    # 3. Offload saving to background task
    background_tasks.add_task(
        save_log_and_cache,
        prompt=first_message,
        model_name=user_model,
        response_text=assistant_reply,
        vector=vector,
        latency=latency_ms,
        params_hash=real_params_hash
        
    )

    # 4. Return response immediately to client
    return response_data