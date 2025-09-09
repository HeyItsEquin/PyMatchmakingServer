import socket

class Client:
    addr: tuple[str, int]
    sock: socket.socket