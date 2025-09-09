from socket import *
from threading import Thread

class ServerInfo:
    udp_port: int
    tcp_port: int

    addr: str

class Server:
    udp_sock: socket
    tcp_sock: socket
    tcp_thread: Thread
    info: ServerInfo

    def handle_tcp(self):
        try:
            self.tcp_sock.listen()
            (cl_sock, addr) = self.tcp_sock.accept()

            print("Client connected ( " + addr[0] + ":" + str(addr[1]) + " )")
        except Exception as e:
            pass

    def setup_sockets(self):
        self.udp_sock = socket(AF_INET, SOCK_DGRAM)
        self.tcp_sock = socket(AF_INET, SOCK_STREAM)

        self.tcp_sock.bind((self.info.addr, self.info.tcp_port))
        print("TCP socket bound")

        tcp_thread = Thread(target=self.handle_tcp)
        tcp_thread.start()
        print("Server listening on " + self.info.addr + ":" + str(self.info.tcp_port))

    def start(self):
        try:
            self.setup_sockets()

            input()
        except KeyboardInterrupt:
            self.tcp_sock.close()
            if self.tcp_thread: self.tcp_thread.join()
        except Exception as e:
            print("An unhandled exception occurred: \n", e)