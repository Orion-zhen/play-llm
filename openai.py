from config.model_config import LLM_ROOT_DIR, LLM_CARD, LLM, MODEL_NAMES
from config.server_config import HOST, PORT, PORT_SSL
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
    
    # make sure all process terminated
    os.system("ps -eo pid,user,cmd|grep -P 'openai.py|fastchat.serve|multiprocessing'|grep -v grep|awk '{print $1}'|xargs kill -9")
    
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
    
    ssl_ok = True if (os.getenv("SSL_KEYFILE")!=None and os.getenv("SSL_CERTFILE")!=None) else False

    model_path = os.path.join(LLM_ROOT_DIR, LLM_CARD[LLM]["path"])
    model_names = MODEL_NAMES

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
    
    if ssl_ok:
        cmd_openai_api_server_ssl = [
            "python",
            "-m",
            "fastchat.serve.openai_api_server",
            "--host",
            str(HOST),
            "--port",
            str(PORT_SSL),
            "--ssl",        
        ]
        p_openai_api_server_ssl = subprocess.Popen(cmd_openai_api_server_ssl)
        process_list.append(p_openai_api_server_ssl)

    for p in process_list:
        p.wait()
