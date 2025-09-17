import socket
from network.socket import *
from network.protocol import *
from uuid import *
from util import logging

class Server:
    tcp: socket.socket
    udp: socket.socket

    listening: bool

    def __cleanup(self):
        logging.info("Closing server sockets")
        self.tcp.close()
        self.udp.close()

    def init_tcp_handshake(self, sock):
        logging.info("Received <CONNECT> request from client")
        cl_id = uuid4()
        logging.info(f"Assigned client UUID <{cl_id}>")
        logging.info("Sending <SYN> response with ID")
        res = Message()
        res.header.type = MessageType.SYN
        res.header.name = "<SERVER>"
                    
        res.body["assigned"] = cl_id.__str__()
            
        res.send(sock)

        logging.info("Awaiting <ACK> response from client")
            
        buf = recv_all_data(sock)
        msg = Message.from_string(buf)
            
        if msg.header.type != MessageType.ACK:
            logging.error("Did not receive message type <ACK> from client")
            sock.close()
            return -1
            
        if msg.header.id != cl_id:
            logging.error("ID mismatch in <ACK> response from client")
            logging.error(f"Expected UUID <{cl_id}>; received <{msg.header.id}>")
            res = Message()
            res.header.type = MessageType.REJ
            res.header.name = "<SERVER>"
                
            res.send(sock)
            sock.close()
            return -1
            
        logging.info("Received <ACK> response from client, authentication success")
            
        res = Message()
        res.header.type = MessageType.VER
        res.header.name = "<SERVER>"
            
        res.send(sock)
        
        return 0

    def start(self):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.tcp.bind(("127.0.0.1", 8001))
        
        self.listening = True

        while self.listening:
            logging.info("Server TCP socket bound and listening at 127.0.0.1:8001")
            self.tcp.listen()
            cl_sock, cl_addr = self.tcp.accept()
            logging.info(f"Accepting new incoming connection ({cl_addr[0]}:{cl_addr[1]})")

            buf = recv_all_data(cl_sock)
            msg = Message.from_string(buf)
            
            if msg.header.type != MessageType.CONNECT and msg.header.type != MessageType.ACK:
                logging.error("Did not receive message type <CONNECT> from client on TCP socket")
                cl_sock.close()
                continue
            
            if msg.header.type == MessageType.ACK:
                logging.error("Received message type <ACK> but no handshake was initialized")
                cl_sock.close()
                continue
            
            success = self.init_tcp_handshake(cl_sock)
            
            if success: cl_sock.close()

            self.listening = False

        self.__cleanup()