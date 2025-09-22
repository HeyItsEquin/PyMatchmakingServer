import socket
from util import logging
from network.protocol import Message, MessageType, Address
from network.socket import recv_all_data, recv_all_data_udp, is_valid_socket
from threading import Thread
from uuid import UUID
from time import sleep

ADDRESS_ANY = ("", 0)

class Client:
    tcp: socket.socket
    udp: socket.socket

    udp_thread: Thread

    id: UUID
    name: str
    addr: Address
    
    server_tcp_addr: Address
    server_udp_addr: Address
    
    connected: bool
    initialized: bool
    shutdown: bool
    
    def __init__(self):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_thread = Thread(target=self.handle_udp_message)
        self.id = -1
        self.connected = False
        self.initialized = False
        self.shutdown = False
        self.name = ""
        self.addr = ("", 0)
        self.server_tcp_addr = ("127.0.0.1", 8001)
        self.server_udp_addr = ("127.0.0.1", 8002)
        
    def __cleanup(self):
        try:
            if self.connected:
                self.disconnect()

            if self.shutdown:
                return

            self.initialized = False

            logging.info("Closing client sockets")

            self.tcp.close()
            self.udp.close()

            self.shutdown = True
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
            logging.info("Received SYN response from servers", True)
            logging.info(f"Assigned UUID <{assigned}>")
            logging.info("Sending ACK response to server, awaiting <VER> response", True)
            
            ack = Message()
            ack.header.type = MessageType.ACK
            ack.header.name = ""
            ack.header.id = assigned
            
            ack.send(self.tcp)
            
            buf = recv_all_data(self.tcp)
            res = Message.from_string(buf)
            if res.header.type == MessageType.VERIFIED:
                logging.info("Ready to communicate")
            
            if res.header.type == MessageType.REJECTED:
                logging.info("Authentication rejected, likely ID mismatch")
            
            self.id = assigned
        except ConnectionRefusedError:
            logging.error("Connection refused. Is the server running?")
            self.__cleanup()
        except TimeoutError:
            logging.error("TCP handshake time out. The server may not be running")
            self.__cleanup()
        except OSError as e:
            logging.error(f"Socket error during TCP handshake: {e}")
            self.__cleanup()
        except Exception as e:
            logging.error(f"An error occurred during TCP handshake: {e}")
            self.__cleanup()
        
    def set_server_identity(self, name: str):
        try:
            if not self.id:
                logging.error("Client ID is not set. Cannot send identity to server")
                return
            
            self.name = name
            self.send_udp_message(MessageType.IDENTITY)

            logging.info(f"Sent updated client identity to server: Name=<\"{self.name}\">", True)
        except Exception as e:
            logging.error(f"Something went wrong trying to send identity to server: {e}")
        
    def handle_udp_message(self):
        try:
            while self.initialized and not self.shutdown and is_valid_socket(self.udp):
                buf, addr = recv_all_data_udp(self.udp)
                msg = Message.from_string(buf)

                if msg.header.type == MessageType.ANONTEST:
                    logging.info(f"Received <ANONTEST> from server: {msg.body['message']}", True)
                    continue
                logging.info(f"Received <{MessageType(msg.header.type).name}> message from server", True)
        except Exception as e:
            logging.error(f"Something went wrong in UDP listener thread: {e}")
            return

    def send_udp_message(self, type: MessageType, body = {}):
        try:
            if not self.connected:
                return
            
            msg = Message()
            msg.header.type = type
            msg.header.name = self.name
            msg.header.id = self.id or -1

            msg.body = body

            logging.info(f"Sending <{type.name}> message to server", True)
            msg.sendto(self.udp, self.server_udp_addr)

        except Exception as e:
            logging.error(f"Something went wrong trying to send message to server: {e}")
    
    def send_anon_udp_message(self, type: MessageType, body = {}):
        try:
            msg = Message()
            msg.header.type = type
            msg.header.name = ""
            msg.header.id = -1
            msg.body = body

            msg.sendto(self.udp, self.server_udp_addr)
        except Exception as e:
            logging.error(f"Something went wrong trying to send anonymous message: {e}")
            return        

    def connect(self, name: str):
        try:
            self.tcp.connect(self.server_tcp_addr)
            self.udp.bind(ADDRESS_ANY)

            self.initialized = True

            self.udp_thread.start()

            self.send_anon_udp_message(MessageType.ANONTEST)

            logging.info("Connected to server")
            logging.info("Initializing TCP handshake")
            
            self.init_tcp_handshake()

            self.connected = True

            self.set_server_identity(name)
        except ConnectionRefusedError as e:
            logging.error(f"Connection refused (is the server running?): {e}")
            self.__cleanup()
        except Exception as e:
            logging.error(f"Something went wrong when trying to connect to the server: {e}")
            self.__cleanup()
            
    def disconnect(self):
        try:
            if not self.connected:
                return

            self.send_udp_message(MessageType.DISCONNECT)

            self.connected = False
        except Exception as e:
            logging.error(f"Something went wrong trying to disconnect from server: {e}")

    def cleanup(self):
        self.__cleanup()
        