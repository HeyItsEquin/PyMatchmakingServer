from socket import *

class ServerInfo:
    udp_port: int
    tcp_port: int

class Server:
    udp_sock: socket
    tcp_sock: socket
    info: ServerInfo

    def Start(self):
        try:
            self.udp_sock = socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.tcp_sock = socket(socket.AF_INET, socket.SOCK_STREAM)

            self.tcp_sock.bind(("127.0.0.1", self.info.tcp_port))
            self.udp_sock.bind(("127.0.0.1", self.info.udp_port))

            print("TCP socket bound")
            print("UDP socket bound")
        except Exception as e:
            print("An unhandled exception occurred: \n", e)