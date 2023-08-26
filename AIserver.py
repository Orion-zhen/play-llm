import json
import arrow
import signal
import sys
import os
import argparse
from socket import *
from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM
from transformers.generation import GenerationConfig


class AIserver:
    parser = argparse.ArgumentParser(description="choose a model to load")
    parser.add_argument("--chatglm2", "--chatglm", action="store_true", default=False, help="load chatglm2-6b")
    parser.add_argument("-chatglm2-32k", "--chatglm-32k", action="store_true", default=False, help="load chatglm2-32k")
    parser.add_argument("--qwen", "--Qwen", action="store_true", default=False, help="load 通义千问-7b")
    
    def __init__(self) -> None:
        try:
            with open("resource/log.json", "r", encoding="utf-8") as f:
                self.log = json.load(f)
        except:
            self.log = []
            
        signal.signal(signal.SIGINT, self.interruptionHandler)
        
        self.args = self.parser.parse_args()
        
        if self.args.chatglm2:
            self.tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm2-6b", trust_remote_code=True)
            self.model = AutoModel.from_pretrained("THUDM/chatglm2-6b", trust_remote_code=True, device='cuda').eval()
        elif self.args.chatglm_32k:
            self.tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm2-32k", trust_remote_code=True)
            self.model = AutoModel.from_pretrained("THUDM/chatglm2-32k", trust_remote_code=True, device='cuda').eval()
        elif self.args.qwen:
            self.tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-7B-Chat", trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-7B-Chat", device_map="auto", trust_remote_code=True).eval()
            self.model.generation_config = GenerationConfig.from_pretrained("Qwen/Qwen-7B-Chat", trust_remote_code=True)
        else:
            print("Please specify a model to load")
            sys.exit(0)
        
        try:
            with open("resource/knownIP.json", "r", encoding="utf8") as f:
                knownIP = json.load(f)
            self.serverPort = knownIP["Port"]
        except FileNotFoundError:
            self.serverPort = input("Please enter the server port: ")
            ip = gethostbyname(gethostname())
            os.makedirs("resource", exist_ok=True)
            with open("resource/knownIP.json", "w", encoding="utf8") as f:
                json.dump({"Server": ip, "Port": self.serverPort}, f, ensure_ascii=False, indent=4)
        
        try:
            with open("resource/DNS.json", "r", encoding="utf8") as f:
                self.DNS = json.load(f)
        except FileNotFoundError:
            self.DNS = {}
            with open("resource/DNS.json", "w", encoding="utf8") as f:
                json.dump(self.DNS, f, ensure_ascii=False, indent=4)
        
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
            if addr[0] in self.DNS:
                addr = (self.DNS[addr[0]], addr[1])
            
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