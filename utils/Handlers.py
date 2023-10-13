from typing import Union
from transformers import AutoTokenizer, AutoModel
from config.model_config import DEFAULT_MODEL, models_info
from config.server_config import DEFAULT_DEVICE
import os


def load_model(model_name: Union[str, None] = None):
    if not model_name:
        model_info = models_info[DEFAULT_MODEL]
        model = AutoModel.from_pretrained(model_info["path"], trust_remote_code=True).to("cuda")
        tokenizer = AutoTokenizer.from_pretrained(model_info["path"], trust_remote_code=True)
        return model, tokenizer
    else:
        model_info = models_info[model_name]
        model = AutoModel.from_pretrained(model_info["path"], trust_remote_code=True).to("cuda")
        tokenizer = AutoTokenizer.from_pretrained(model_info["path"], trust_remote_code=True)
        return model, tokenizer
    

def call_public(port: int = 11451):
    os.system(f"nrgok http {port}")