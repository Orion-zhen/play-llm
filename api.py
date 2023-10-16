from urllib import response
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union
from threading import Thread
from utils.Arugs import parser
from utils.Handlers import create_worker
from config.model_config import MODEL_CARDS, DEFAULT_MODEL
import uvicorn

args = parser.parse_args()


class chat(BaseModel):
    host: Union[str, None] = None
    query: Union[str, None] = None
    answer: Union[str, None] = None
    history: list = []
    
app = FastAPI()

@app.get("/chatbots")
async def chatbots():
    return list(MODEL_CARDS.keys())

@app.get("/chat/{chatbot}")
async def one_shot(chatbot: str = DEFAULT_MODEL, q: str = ""):
    worker = create_worker(chatbot)
    response = worker.chat(q)
    return response

@app.post("/chat")
async def chat_api(query: chat):
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=11451)
    