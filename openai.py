from config.model_config import LLM_ROOT_DIR, LLM_CARD, LLM
from config.server_config import HOST, PORT
import subprocess
import signal
import time
import os


def clear_logs(dir: str):
    print("\nClearing logs...")
    for filename in os.listdir(dir):
        if filename.endswith(".log"):
            filepath = os.path.join(dir, filename)
            try:
                os.remove(filepath)
            except:
                print(f"Failed to remove {filepath}")


def siginit_handler(signum, frame):
    clear_logs(os.getenv("PWD"))

    print("Exiting...")
    for p in process_list:
        p.terminate()
    time.sleep(0.5)
    exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, siginit_handler)
    console_msg = (
        f"| Loading {LLM}"
        + (
            f" with extra params {LLM_CARD[LLM]['params']}"
            if LLM_CARD[LLM]["params"]
            else ""
        )
        + " 🤗| "
    )

    print("\n" + "=" * len(console_msg))
    print(console_msg)
    print("=" * len(console_msg) + "\n")

    model_path = os.path.join(LLM_ROOT_DIR, LLM_CARD[LLM]["path"])
    model_names = [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo",
        "text-davinci-003",
        "text-embedding-ada-002",
    ]

    cmd_server_controller = ["python", "-m", "fastchat.serve.controller"]
    cmd_model_worker = [
        "python",
        "-m",
        "fastchat.serve.model_worker",
        "--model-names",
        ",".join(model_names),
        "--model-path",
        model_path,
    ]
    cmd_openai_api_server = [
        "python",
        "-m",
        "fastchat.serve.openai_api_server",
        "--host",
        str(HOST),
        "--port",
        str(PORT),
    ]

    for param in LLM_CARD[LLM]["params"]:
        cmd_model_worker.append(param)

    p_server_controller = subprocess.Popen(cmd_server_controller)
    p_model_worker = subprocess.Popen(cmd_model_worker)
    p_openai_api_server = subprocess.Popen(cmd_openai_api_server)
    process_list = [p_server_controller, p_model_worker, p_openai_api_server]

    for p in process_list:
        p.wait()
