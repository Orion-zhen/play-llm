from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union
from threading import Thread
from utils.Arugs import parser
from utils.Handlers import load_model, call_public
from config.model_config import MODEL_CARDS
import uvicorn
import os

args = parser.parse_args()


class chat(BaseModel):
    host: Union[str, None] = None
    query: Union[str, None] = None
    answer: Union[str, None] = None
    history: list = []
    
app = FastAPI()
model, tokenizer = load_model()

@app.get("/chatbots")
async def chatbots():
    return list(MODEL_CARDS.keys())

@app.get("/chat")
async def one_shot(q: str = ""):
    response, _ = model.chat(tokenizer, q, history=[])
    return response

@app.post("/chat")
async def chat_api(query: chat):
    response = chat()
    response.answer, response.history = model.chat(tokenizer, query.query, history=query.history)
    response.host = query.host
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=11451)
    