from typing import Union
from transformers import AutoTokenizer, AutoModel
from pathlib import Path
from typing import Optional, Union
from config.model_config import DEFAULT_MODEL, MODEL_CARDS, MODEL_ROOT_PATH
from config.server_config import DEFAULT_DEVICE
import os


def get_model_path(model_name: str) -> str:
    if path_str := MODEL_CARDS[model_name]["path"]:  # 以 "chatglm-6b": "THUDM/chatglm-6b-new" 为例，以下都是支持的路径
        path = Path(path_str)
        if path.is_dir():  # 任意绝对路径
            return str(path)

        root_path = Path(MODEL_ROOT_PATH)
        if root_path.is_dir():
            path = root_path / model_name
            if path.is_dir():  # use key, {MODEL_ROOT_PATH}/chatglm-6b
                return str(path)
            path = root_path / path_str
            if path.is_dir():  # use value, {MODEL_ROOT_PATH}/THUDM/chatglm-6b-new
                return str(path)
            path = root_path / "embedding" / path_str
            if path.is_dir(): # use category and value, {MODEL_ROOT_PATH}/embedding/mokai/m3e-large
                return str(path)
            path = root_path / "llm" / path_str
            if path.is_dir(): # use category and value, {MODEL_ROOT_PATH}/llm/THUDM/chatglm-6b-new
                return str(path)
            path = root_path / path_str.split("/")[-1]
            if path.is_dir():  # use value split by "/", {MODEL_ROOT_PATH}/chatglm-6b-new
                return str(path)
            path = root_path / "embedding" / path_str.split("/")[-1]
            if path.is_dir(): # use category and value split by "/", {MODEL_ROOT_PATH}/embedding/m3e-large
                return str(path)
            path = root_path / "llm" / path_str.split("/")[-1]
            if path.is_dir(): # use category and value split by "/", {MODEL_ROOT_PATH}/llm/chatglm-6b-new
                return str(path)
        return path_str  # THUDM/chatglm06b

    else:
        raise KeyError


def create_worker(model_name: str):
    worker = MODEL_CARDS[model_name]["worker"](get_model_path(model_name))
    return worker