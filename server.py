import socket
from threading import Thread
from msvcrt import getch
from network.client import *

class ServerInfo:
    udp_port: int
    tcp_port: int

    addr: str

class Server:
    udp_sock: socket
    tcp_sock: socket
    tcp_thread: Thread
    info: ServerInfo

    connected: list[Client]

    def __init__(self):
        self.info = ServerInfo()
        self.info.addr = "127.0.0.1"
        self.info.tcp_port = 8001
        self.info.udp_port = 8002

        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.tcp_thread = Thread(target=self.handle_tcp_connection)

        self.connected = []

    def handle_tcp_client(self, client: socket, ret_addr: tuple[str, int]):
        data = client.recv(1024)
        decoded = data.decode('utf-8')

        print("Message received from client: \n", decoded)

        print("Disconnecting client (" + ret_addr[0] + ":" + str(ret_addr[1]) + ")")
        
        client.close()

    def handle_tcp_connection(self):
        try:
            self.tcp_sock.listen()
            (cl_sock, addr) = self.tcp_sock.accept()

            print("Client connected (" + addr[0] + ":" + str(addr[1]) + ")")

            client_dat = Client()
            client_dat.addr = addr
            client_dat.sock = cl_sock

            self.connected.append(client_dat)

            self.handle_tcp_client(cl_sock, addr)
        except Exception as e:
            pass

    def setup_sockets(self):
        self.tcp_sock.bind((self.info.addr, self.info.tcp_port))
        print("Server TCP socket bound to " + str(self.info.tcp_port))

    def setup_listeners(self):
        self.tcp_thread.start()

    def start(self):
        try:
            self.setup_sockets()
            self.setup_listeners()
            print("Server listening on " + self.info.addr + ":" + str(self.info.tcp_port))
        except KeyboardInterrupt:
            self.cleanup()
        except Exception as e:
            print("An unhandled exception occurred: \n", e)

    def cleanup(self):
        for client in self.connected:
            client.sock.close()

        if self.tcp_thread:
            self.tcp_thread.join()
        
        self.tcp_sock.close()
        self.udp_sock.close()