from server import *

def main():
    s = Server()

    s.info = ServerInfo()
    s.info.addr = "127.0.0.1"
    s.info.tcp_port = 8001
    s.info.udp_port = 8002

    s.start()

if __name__ == "__main__":
    main()