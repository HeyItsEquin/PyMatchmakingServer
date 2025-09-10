from server import *
import socket

class Client:
    tcp_sock: socket.socket
    udp_sock: socket.socket
    s_info: ServerInfo

    def connect(self):
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.tcp_sock.connect((self.s_info.addr, self.s_info.tcp_port))
        self.tcp_sock.send(b"Hello from client")
        self.tcp_sock.close()

def main():
    client = Client()

    client.s_info = ServerInfo()
    client.s_info.addr = "127.0.0.1"
    client.s_info.tcp_port = 8001

    client.connect()

if __name__ == "__main__":
    main()