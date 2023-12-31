import json
import signal
import sys
from socket import socket, AF_INET, SOCK_STREAM
from config.server_config import server_info


class AIclient:
    def __init__(self) -> None:
        signal.signal(signal.SIGINT, self.interruptionHandler)

        self.serverName = server_info["IP"]
        self.serverPort = server_info["port"]
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.maxlen = 1024*1024*1024 # 1GB
    
    def interruptionHandler(self, signal, frame) -> None:
        print("")
        print("Keyboard interruption detected! Preparing to tear down the connection...")
        request = json.dumps({"text": "exit", "history": []}, ensure_ascii=False)
        self.clientSocket.send(request.encode())  
        self.clientSocket.close()
        print("Connection closed successfully!")
        sys.exit(0)
        
    def run(self):
        try:
            self.clientSocket.connect((self.serverName, self.serverPort))
        except ConnectionError:
            print("Connection error, please confirm your server IP and port")
            sys.exit(0)
            
        print("Connection established successfully!")
        sentence = input(f"Human(0 / {self.maxlen} bytes used): ")
        history = []
        
        while sentence != "exit":
            request = json.dumps({"text": sentence, "history": history}, ensure_ascii=False)
            self.clientSocket.send(request.encode())
            try:
                response = self.clientSocket.recv(self.maxlen).decode()
            except UnicodeDecodeError:
                print("Max length exceeded, history cleared")
                history = []
                continue
            except ConnectionResetError:
                print("Connection reset by peer, exiting...")
                sys.exit(0)
            
            message = json.loads(response)
            history = message["history"]
            print("AI: " + message["text"])
            sentence = input(f"Human({len(response)} / {self.maxlen} bytes used): ")
        
        print("")
        print("Human exit detected! Preparing to tear down the connection...")
        request = json.dumps({"text": "exit", "history": []}, ensure_ascii=False)
        self.clientSocket.send(request.encode())  
        self.clientSocket.close()
        print("Connection closed successfully!")


if __name__ == "__main__":
    client = AIclient()
    client.run()
