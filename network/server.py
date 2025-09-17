import socket
from network.socket import *
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
            logging.info(f"Data received from client: <{buf}>")

            cl_id = uuid4()
            logging.info(f"Assigning client new UUID <{cl_id}>")

            cl_sock.send(cl_id.__str__().encode())
            logging.info("Awaiting client ACK response")

            

            cl_sock.close()

            self.listening = False

        self.__cleanup()