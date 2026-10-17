from fastapi import FastAPI,Depends,BackgroundTasks
from . import schemas,database,llm,models
from sqlalchemy.orm import Session
import time
from . embeddings import lifespan, generate_embedding

# Register the lifespan from embeddings.py
app = FastAPI(title="LLM Semantic Cache Proxy", lifespan=lifespan)
models.base.metadata.create_all(bind=database.engine)

@app.post("/test-embed")
async def test_embed(prompt: str):
    # Call your asynchronous helper
    vector = await generate_embedding(prompt)
    return {
        "prompt": prompt,
        "vector_dimensions": len(vector),
        "sample_values": vector[:5]  # First 5 numbers of the 384 array
    }


@app.post("/v1/chat/completions")
async def generate_response(request:schemas.completionMessage,background_tasks: BackgroundTasks,db:Session=Depends(database.get_db)):
    start_time=time.perf_counter()


    user_model=request.model
    first_message=request.messages[0].content
    response_data=await llm.generate(request)

    end_time=time.perf_counter()
    latency_ms=(end_time-start_time)*1000
    def save_log():

        new_log=models.request_log(prompt=first_message,latency=latency_ms)
        db.add(new_log)
        db.commit()

    background_tasks.add_task(save_log)    

    return response_data
    
