from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from contextlib import asynccontextmanager
from typing import List
from fastapi.concurrency import run_in_threadpool

app_state={}

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Starting up:Loading Model")
    app_state["model"]=SentenceTransformer('all-MiniLM-L6-v2')
    yield
    print("Closing:Clearing space")
    app_state.clear()

def embed(text:str)->List[float]:
    model=app_state["model"]
    embedding_array=model.encode(text)
    return embedding_array.tolist()

async def generate_embedding(text:str)->List[float]:

    return await run_in_threadpool(embed,text)

 