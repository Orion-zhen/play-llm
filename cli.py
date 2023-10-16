from config.model_config import DEFAULT_MODEL, MODEL_CARDS
from utils.Handlers import create_worker


if __name__ == "__main__":
    worker = create_worker(DEFAULT_MODEL)
    while True:
        inputs = input("Human: ")
        outputs = worker.chat(inputs)
        print("AI: "+ outputs)