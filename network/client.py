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
        
    def init_tcp_handshake(self):
        socket.setdefaulttimeout(12.0)
        
        
        msg = Message()
        msg.header.name = ""
        msg.header.type = MessageType.CONNECT
        
        logging.info("Sending <CONNECT> request, awaiting <SYN> response from server")
        msg.send(self.tcp)
        
        buf = recv_all_data(self.tcp)
        res = Message.from_string(buf)
        
        if res.header.type != MessageType.SYN:
            logging.error(f"Authentication failed. Received <{MessageType(res.header.type).name}> response, expected <SYN>")
        
        assigned = UUID(res.body["assigned"])
        logging.info(f"Received SYN response from servers")
        logging.info(f"Assigned UUID <{assigned}>")
        logging.info(f"Sending ACK response to server, awaiting <VER> response")
        
        ack = Message()
        ack.header.type = MessageType.ACK
        ack.header.name = ""
        ack.header.id = assigned
        
        ack.send(self.tcp)
        
        buf = recv_all_data(self.tcp)
        res = Message.from_string(buf)
        if res.header.type == MessageType.VER:
            logging.info("Received <VER> response from server, ready to communicate")
        
        if res.header.type == MessageType.REJ:
            logging.info("Authentication rejected, likely ID mismatch")
        
        self.id = assigned
        
    def connect(self):
        self.tcp.connect(("127.0.0.1", 8001))
        
        logging.info("Connected to server")
        logging.info("Initializing TCP handshake process")
        
        self.init_tcp_handshake()
        
        socket.setdefaulttimeout(None)