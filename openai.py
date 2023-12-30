import subprocess
import signal
import time
import os


def siginit_handler(signum, frame):
    print("\nClearing logs...")
    for filename in os.listdir("."):
        if filename.endswith(".log"):
            filepath = os.path.join(".", filename)
            try:
                os.remove(filepath)
            except:
                print(f"Failed to remove {filepath}")

    print("Exiting...")
    for p in process_list:
        p.terminate()
    time.sleep(1)
    exit(0)


host = "0.0.0.0"
port = 11451
model_path = "/home/orion/ai/Models/chatglm3-6b"
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
    host,
    "--port",
    str(port),
]

p_server_controller = subprocess.Popen(cmd_server_controller)
p_model_worker = subprocess.Popen(cmd_model_worker)
p_openai_api_server = subprocess.Popen(cmd_openai_api_server)
process_list = [p_server_controller, p_model_worker, p_openai_api_server]

signal.signal(signal.SIGINT, siginit_handler)

for p in process_list:
    p.wait()
