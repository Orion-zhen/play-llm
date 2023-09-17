import json
import arrow
import signal
import sys
from socket import socket, AF_INET, SOCK_STREAM
from transformers import AutoTokenizer, AutoModel

from utils.Arugs import parser
from config.model_config import DEFAULT_MODEL, models_info
from config.server_config import server_info, rDNS, DEFAULT_DEVICE
from utils.Device import llm_device, detect_device
model_path = models_info[DEFAULT_MODEL]["path"]
if DEFAULT_DEVICE == "auto":
    device = llm_device(detect_device())
else:
    device = llm_device(DEFAULT_DEVICE)

class AIserver:
    
    def __init__(self) -> None:
        try:
            with open("resource/log.json", "r", encoding="utf-8") as f:
                self.log = json.load(f)
        except:
            self.log = []
            
        signal.signal(signal.SIGINT, self.interruptionHandler)
        
        self.args = parser.parse_args()
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(model_path, trust_remote_code=True).to(device)
        
        self.serverPort = server_info["port"]
        self.rDNS = rDNS
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        self.maxlen = 1024*1024*1024 # 1GB
        
    def interruptionHandler(self, signal, frame) -> None:
        print("")
        print("Keyboard interruption detected! Logs have been written to log.json")
        with open("resource/log.json", "w", encoding="utf-8") as f:
            json.dump(self.log, f, ensure_ascii=False, indent=4)
        sys.exit(0)
    
    def run(self) -> None:
        self.serverSocket.bind(('', self.serverPort))
        self.serverSocket.listen(1)
        print('The server is ready to receive')
        
        while True:
            conversation = {}
            connectionSocket, addr = self.serverSocket.accept()
            if addr[0] in self.rDNS:
                addr = (self.rDNS[addr[0]], addr[1])
            
            time = arrow.now().format('YYYY-MM-DD HH:mm:ss')
            print("**********************")
            print("<" + time + ">")
            print(f"User at {addr} connected")
            conversation["user"] = addr
            conversation["time"] = time
            dialogs = []
            
            try:
                sentence = connectionSocket.recv(self.maxlen).decode()
            except UnicodeDecodeError:
                print("Max length exceeded, exiting...")
                message = json.dumps({"text": "Max length exceeded, please retry", "history": []}, ensure_ascii=False)
                conversation["error"] = "Max length exceeded"
                print(f"User at {addr} exited") 
                print("**********************")
                self.log.append(conversation)
                connectionSocket.close()
                continue
                
            request = json.loads(sentence)
            while request["text"] != 'exit':
                dialog = {}
                print("Client: " + request["text"])
                response, history = self.model.chat(self.tokenizer, request["text"], history=request["history"])
                print("Server: " + response)
                dialog["client"] = request["text"]
                dialog["server"] = response
                dialogs.append(dialog)
                message = json.dumps({"text": response, "history": history}, ensure_ascii=False)
                connectionSocket.send(message.encode())
                
                try:
                    sentence = connectionSocket.recv(self.maxlen).decode()
                except UnicodeDecodeError:
                    print("Max length exceeded, retrying...")
                    message = json.dumps({"text": "Max length exceeded, please retry", "history": []}, ensure_ascii=False)
                    conversation["error"] = "Max length exceeded"
                    continue
                    
                request = json.loads(sentence)
                
            conversation["dialogs"] = dialogs
            print(f"User at {addr} exited") 
            print("**********************")
            self.log.append(conversation)
            connectionSocket.close()


if __name__ == "__main__":
    server = AIserver()
    server.run()