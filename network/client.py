import socket
from util import logging
from network.protocol import *
from network.socket import *

class Client:
    tcp: socket.socket
    id: UUID
    name: str
    
    def __init__(self):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.id = None
        
    def __cleanup(self):
        try:
            logging.info("Closing client sockets")

            self.tcp.close()
        except Exception as e:
            logging.error(f"Error occurred during client shutdown: {e}")

    def init_tcp_handshake(self):
        try:
            socket.setdefaulttimeout(12.0)
            
            msg = Message()
            msg.header.name = ""
            msg.header.type = MessageType.CONNECT
            
            logging.info("Sending <CONNECT> request, awaiting <SYN> response from server", True)
            msg.send(self.tcp)
            
            buf = recv_all_data(self.tcp)
            res = Message.from_string(buf)
            
            if res.header.type != MessageType.SYN:
                logging.error(f"Authentication failed. Received <{MessageType(res.header.type).name}> response, expected <SYN>")
            
            assigned = UUID(res.body["assigned"])
            logging.info(f"Received SYN response from servers", True)
            logging.info(f"Assigned UUID <{assigned}>")
            logging.info(f"Sending ACK response to server, awaiting <VER> response", True)
            
            ack = Message()
            ack.header.type = MessageType.ACK
            ack.header.name = ""
            ack.header.id = assigned
            
            ack.send(self.tcp)
            
            buf = recv_all_data(self.tcp)
            res = Message.from_string(buf)
            if res.header.type == MessageType.VER:
                logging.info("Ready to communicate")
            
            if res.header.type == MessageType.REJ:
                logging.info("Authentication rejected, likely ID mismatch")
            
            self.id = assigned
        except ConnectionRefusedError as e:
            logging.error("Connection refused. Is the server running?")
            self.__cleanup()
        except socket.error as e:
            logging.error(f"Socket error during TCP handshake: {e}")
            self.__cleanup()
        except socket.timeout:
            logging.error("TCP handshake time out. The server may not be running")
            self.__cleanup()
        except Exception as e:
            logging.error(f"An error occurred during TCP handshake: {e}")
            self.__cleanup()
        
    def connect(self):
        try:
            self.tcp.connect(("127.0.0.1", 8001))
            
            logging.info("Connected to server")
            logging.info("Initializing TCP handshake")
            
            self.init_tcp_handshake()

            self.__cleanup()
        except Exception as e:
            logging.error(f"Something went wrong when trying to connect to the server: {e}")
            self.__cleanup()